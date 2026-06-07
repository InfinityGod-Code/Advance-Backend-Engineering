# Savepoint Implementation - Technical Documentation

## Overview
This document explains how SQL savepoints are implemented in the `/transfer-with-loyalty` endpoint and why they're important for robust transaction management.

---

## File Structure

### Modified Files:
1. **app/schemas/transaction_schema.py** - Added `LoyaltyBonusResponse` model
2. **app/service/transaction_service.py** - Added `transfer_with_loyalty_bonus()` method
3. **app/route/transfers.py** - Added `/transfer-with-loyalty` endpoint

---

## Code Implementation

### 1. Response Schema (transaction_schema.py)

```python
class LoyaltyBonusResponse(BaseModel):
    """Response model for transfer with loyalty bonus using savepoints."""
    status: str  # "completed", "bonus_rolled_back"
    loyalty_bonus_applied: bool  # Whether bonus succeeded
    bonus_amount: Decimal  # 5% of transfer amount
    savepoint_demo: str  # Explanation of savepoint behavior
    # ... plus balance fields for verification
```

**Purpose**: Clearly communicate what happened with the savepoint.

---

### 2. Service Method (transaction_service.py)

#### Method Signature:
```python
@staticmethod
async def transfer_with_loyalty_bonus(
    session: AsyncSession,
    source_account_number: str,
    destination_account_number: str,
    amount: Decimal,
    simulate_bonus_error: bool = False,
)
```

#### Key Steps:

**Step 1: Lock Accounts (Isolation)**
```python
source, destination = await TransactionService._lock_accounts_in_order(
    session, source_account_number, destination_account_number
)
```
- Uses `SELECT ... FOR UPDATE` to lock rows
- Prevents other transactions from modifying accounts
- Locked in sorted order to prevent deadlocks

**Step 2: Validate Balance**
```python
if source_balance_before < amount:
    raise HTTPException(...)
```
- Business logic check before any database changes

**Step 3: Core Transfer (First Savepoint)**
```python
# Debit source
source.balance -= amount
source.version += 1
session.add(source)

# Credit destination
destination.balance += amount
destination.version += 1
session.add(destination)

# Flush to database
await session.flush()

# CREATE SAVEPOINT 'transfer_complete'
# This marks the successful debit + credit point
await session.execute("SAVEPOINT transfer_complete")
```

**Why flush() before savepoint?**
- `flush()` executes SQL without committing
- `SAVEPOINT` marks this as a rollback point
- If bonus fails, we rollback to here (keeping transfer)

**Step 4: Loyalty Bonus (Second Savepoint)**
```python
try:
    bonus_amount = (amount * Decimal("0.05")).quantize(Decimal("0.01"))
    
    if simulate_bonus_error:
        raise Exception("Simulated bonus error")
    
    destination.balance += bonus_amount
    await session.flush()
    
    # CREATE SAVEPOINT 'bonus_applied'
    await session.execute("SAVEPOINT bonus_applied")
    
    # COMMIT entire transaction
    await session.commit()
    
    return {"status": "completed", ...}
    
except Exception as bonus_error:
    # ROLLBACK TO SAVEPOINT 'transfer_complete'
    # This undoes the bonus attempt but keeps the transfer
    await session.execute("ROLLBACK TO SAVEPOINT transfer_complete")
    
    # Commit only the transfer
    await session.commit()
    
    return {"status": "bonus_rolled_back", ...}
```

---

## How Savepoints Work in PostgreSQL

### Transaction Timeline:

```
BEGIN;                                    -- Start transaction
  INSERT INTO accounts ...;              -- Debit source (version 1)
  UPDATE accounts ...;                   -- Credit destination (version 2)
  SAVEPOINT transfer_complete;           -- SAVEPOINT created
  
  UPDATE accounts SET balance = ... ;    -- Add bonus (version 3)
  SAVEPOINT bonus_applied;               -- Another savepoint
  
  ROLLBACK TO SAVEPOINT transfer_complete; -- Undo bonus!
                                          -- Now at version 2 (pre-bonus)
  
COMMIT;                                  -- Commit to version 2
```

### Result in Database:
- Debit: ✅ Applied
- Credit: ✅ Applied  
- Bonus: ❌ Rolled back

---

## Key Differences: Savepoint vs Full Rollback

### Full Transaction Rollback:
```python
try:
    # Do work 1
    # Do work 2
    # Do work 3
except Exception:
    await session.rollback()  # UNDOES EVERYTHING (1, 2, 3)
```

### Savepoint (Partial) Rollback:
```python
# Do work 1
await session.flush()
await session.execute("SAVEPOINT sp1")

try:
    # Do work 2
    # Do work 3
except Exception:
    await session.execute("ROLLBACK TO SAVEPOINT sp1")
    # Work 1 stays, work 2+3 undone
```

**Advantage**: Work 1 is preserved! You can still commit it.

---

## Concurrency Control

### Pessimistic Locking (FOR UPDATE):
```python
statement = select(AccountModel) \
    .where(AccountModel.account_number == account_number) \
    .with_for_update()
```

**Prevents:**
- Dirty reads (reading uncommitted data)
- Lost updates (two transactions overwriting each other)

**Works with Savepoints:**
- Locks are held until COMMIT
- SAVEPOINT doesn't release locks
- ROLLBACK TO SAVEPOINT keeps locks

---

## Error Scenarios

### Scenario 1: Insufficient Balance
```
Validation fails before any savepoint
→ HTTPException (400 Bad Request)
→ No database changes
```

### Scenario 2: Transfer Succeeds, Bonus Fails
```
SAVEPOINT transfer_complete ✅
  Bonus calculation ❌
  ROLLBACK TO transfer_complete
  COMMIT  ← Transfer is preserved!
```

### Scenario 3: Database Error During Transfer
```
Exception before savepoint
→ session.rollback()  ← Full rollback
→ HTTPException (500 Internal Server Error)
```

---

## Performance Implications

### Memory Usage:
- Savepoints have minimal memory overhead
- Typically <1KB per savepoint in PostgreSQL

### Latency:
- Creating savepoint: ~0.1ms
- Rollback to savepoint: ~0.2ms
- Similar to regular SQL operations

### Concurrency:
- Savepoints don't reduce concurrency
- Locks are held same as without savepoints
- Other transactions wait at row level

---

## Best Practices Demonstrated

### 1. Lock Ordering
```python
# Always lock in same order to prevent deadlocks
if source_number < destination_number:
    lock_source_first()
else:
    lock_destination_first()
```

### 2. Validate Before Savepoint
```python
# Check balances BEFORE creating savepoint
if source.balance < amount:
    raise HTTPException()

# Only after validation, proceed to savepoint
await session.flush()
await session.execute("SAVEPOINT transfer_complete")
```

### 3. Clear Error Messages
```python
"ROLLBACK TO SAVEPOINT 'transfer_complete' was executed. "
"Bonus of 2.50 was undone, but the transfer of 50.00 was "
"preserved and committed."
```

### 4. Separate Try/Except Blocks
```python
try:
    # Core transaction
    ...
    await session.flush()
    await session.execute("SAVEPOINT sp1")
    
    try:
        # Optional work
        ...
    except Exception:
        # Partial rollback
        await session.execute("ROLLBACK TO SAVEPOINT sp1")
except Exception:
    # Full rollback
    await session.rollback()
```

---

## Testing Scenarios Provided

### Test 1: Happy Path (simulate_bonus_error=false)
- ✅ Transfer succeeds
- ✅ Bonus applied
- ✅ Both savepoints reached
- ✅ Full commit

### Test 2: Bonus Fails (simulate_bonus_error=true)
- ✅ Transfer succeeds
- ❌ Bonus fails
- ⚡ ROLLBACK TO SAVEPOINT executed
- ✅ Transfer committed, bonus undone

**Why This Matters:**
Demonstrates that the main operation is preserved even when optional add-ons fail.

---

## Real-World Applications

### E-commerce:
```
SAVEPOINT 'order_placed'
  SAVEPOINT 'inventory_allocated'
    SAVEPOINT 'loyalty_points_added'
      if loyalty_service_fails:
          ROLLBACK TO loyalty_points_added
          COMMIT (order + inventory intact)
```

### Banking:
```
SAVEPOINT 'debit_source'
  SAVEPOINT 'credit_destination'
    SAVEPOINT 'notify_customer'
      if notification_fails:
          ROLLBACK TO notify_customer
          COMMIT (transfer intact)
```

### SaaS:
```
SAVEPOINT 'subscription_created'
  SAVEPOINT 'email_sent'
    SAVEPOINT 'analytics_logged'
      if analytics_fails:
          ROLLBACK TO analytics_logged
          COMMIT (subscription created)
```

---

## Comparison with Other Approaches

### 1. No Savepoints (Current Code Uses This):
```python
try:
    transfer()
    bonus()
except:
    rollback()  # Both transfer and bonus undone
```
**Problem**: Loses the transfer when bonus fails

### 2. With Savepoints (New Implementation):
```python
transfer()
SAVEPOINT sp1
try:
    bonus()
except:
    ROLLBACK TO sp1
commit()  # Transfer preserved
```
**Benefit**: Transfer saved even if bonus fails

### 3. Separate Transactions:
```python
transfer()  # COMMIT
try:
    bonus()  # COMMIT
except:
    pass
```
**Problem**: Transfer succeeds but no rollback safety for bonus

---

## Limitations & Gotchas

### 1. PostgreSQL Only
- SQLite: Limited savepoint support
- MySQL: Variable support across storage engines
- Recommended: PostgreSQL (production-grade)

### 2. Savepoint Names Must Be Unique
```python
SAVEPOINT sp1  # First one OK
SAVEPOINT sp1  # Error if second same name!

# Solution: Use unique names or use begin_nested()
await session.begin_nested()  # Auto-generated savepoint
```

### 3. Rollback Scope
```python
# This rolls back EVERYTHING after savepoint
ROLLBACK TO SAVEPOINT sp1

# NOT this (doesn't exist in SQL):
ROLLBACK SAVEPOINT sp1  # Wrong syntax!
```

### 4. Nested Savepoint Handling
```python
SAVEPOINT sp1
SAVEPOINT sp2
ROLLBACK TO sp2  # OK
ROLLBACK TO sp1  # OK

# But after ROLLBACK TO sp1:
ROLLBACK TO sp2  # ERROR! sp2 no longer exists
```

---

## Monitoring & Debugging

### Check Transaction State:
```sql
SELECT txid_current(), xmin, xmax, cmin, cmax 
FROM pg_stat_activity 
WHERE pid = pg_backend_pid();
```

### View Active Savepoints:
```sql
-- PostgreSQL logs savepoint creation
-- Enable with: log_statement = 'all'
SELECT * FROM pg_stat_statements 
WHERE query LIKE '%SAVEPOINT%';
```

### Application Logging:
```python
logger.info(f"Created savepoint: transfer_complete")
logger.warning(f"Rolled back to savepoint: transfer_complete")
logger.info(f"Transaction committed")
```

---

## Summary

**Savepoints enable:**
- ✅ Partial transaction rollback
- ✅ Preserved main operations on optional failure
- ✅ Granular error recovery
- ✅ Complex multi-step workflows

**Used in this implementation for:**
- Transfer with optional loyalty bonus
- Demonstrates SAVEPOINT creation and rollback
- Shows real-world error handling patterns
- Provides clear response indicators

**Key Takeaway:**
Savepoints are essential for robust transaction management in complex business logic where certain operations are optional or might fail independently.
