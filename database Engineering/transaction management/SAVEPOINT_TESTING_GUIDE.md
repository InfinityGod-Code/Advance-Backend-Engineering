# Testing Savepoint Demo in Postman

## Overview
This guide demonstrates how to test the `/transfer-with-loyalty` endpoint which showcases SQL savepoints for partial transaction rollback.

## Understanding Savepoints

### What are Savepoints?
Savepoints are markers within a transaction that allow you to rollback to a specific point without rolling back the entire transaction.

**Flow:**
```
START TRANSACTION
  ├─ Core Transfer (debit + credit) → SAVEPOINT 'transfer_complete'
  ├─ Apply Loyalty Bonus (5%) → SAVEPOINT 'bonus_applied'
  │
  ├─ IF ERROR during bonus:
  │   └─ ROLLBACK TO SAVEPOINT 'transfer_complete'
  │       (Undo bonus only, keep transfer)
  │
  └─ COMMIT (either full transaction or transfer only)
```

### Key Benefit
Unlike full transaction rollback, savepoints let you undo only part of a transaction while preserving earlier work.

---

## Prerequisites

### 1. Database Setup
Ensure PostgreSQL is running and the database is initialized:
```bash
cd "database Engineering/transaction management"
python3 main.py
```

The app should start on `http://localhost:8000`

### 2. Create Test Accounts
Create two accounts with sufficient balance for testing:

**Request 1: Create Account A**
```
POST http://localhost:8000/accounts
Content-Type: application/json

{
  "account_number": "ACC001",
  "owner_email": "alice@example.com",
  "initial_balance": 1000.00
}
```

**Request 2: Create Account B**
```
POST http://localhost:8000/accounts
Content-Type: application/json

{
  "account_number": "ACC002",
  "owner_email": "bob@example.com",
  "initial_balance": 500.00
}
```

**Request 3: Create Account C (for testing)**
```
POST http://localhost:8000/accounts
Content-Type: application/json

{
  "account_number": "ACC003",
  "owner_email": "charlie@example.com",
  "initial_balance": 2000.00
}
```

---

## Postman Test Scenarios

### Scenario 1: Successful Transfer with Loyalty Bonus (Complete Flow)

This tests the happy path where both transfer and bonus succeed.

**Endpoint:**
```
POST http://localhost:8000/transactions/transfer-with-loyalty?simulate_bonus_error=false
```

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "source_account_number": "ACC001",
  "destination_account_number": "ACC002",
  "amount": 100.00
}
```

**Expected Response:**
```json
{
  "status": "completed",
  "message": "Successfully transferred 100.00 from 'ACC001' to 'ACC002' and applied 5.00 loyalty bonus.",
  "source_account_number": "ACC001",
  "destination_account_number": "ACC002",
  "amount": 100.00,
  "source_balance_before": 1000.00,
  "source_balance_after": 900.00,
  "destination_balance_before": 500.00,
  "destination_balance_after": 605.00,
  "loyalty_bonus_applied": true,
  "bonus_amount": 5.00,
  "savepoint_demo": "No savepoint rollback occurred. Both transfer and loyalty bonus were committed successfully. Savepoints 'transfer_complete' and 'bonus_applied' reached."
}
```

**What Happened:**
- ✅ Transfer of 100.00 succeeded (ACC001: 1000 → 900, ACC002: 500 → 600)
- ✅ Loyalty bonus of 5.00 (5% of 100) was applied
- ✅ Final destination balance: 600 + 5 = 605
- ✅ Both savepoints were reached and committed

**Verification in Database:**
```sql
SELECT account_number, balance FROM accounts WHERE account_number IN ('ACC001', 'ACC002');
```
Expected:
- ACC001: 900.00
- ACC002: 605.00

---

### Scenario 2: Transfer Succeeds, Bonus Fails (Savepoint Rollback!)

This is the KEY DEMO - showing savepoint rollback in action.

**Endpoint:**
```
POST http://localhost:8000/transactions/transfer-with-loyalty?simulate_bonus_error=true
```

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "source_account_number": "ACC001",
  "destination_account_number": "ACC003",
  "amount": 50.00
}
```

**Expected Response:**
```json
{
  "status": "bonus_rolled_back",
  "message": "Transfer succeeded, but loyalty bonus failed. Rolled back to SAVEPOINT 'transfer_complete'. Transfer of 50.00 is intact. Error: Bonus calculation service unavailable: simulated error in loyalty system",
  "source_account_number": "ACC001",
  "destination_account_number": "ACC003",
  "amount": 50.00,
  "source_balance_before": 900.00,
  "source_balance_after": 850.00,
  "destination_balance_before": 2000.00,
  "destination_balance_after": 2050.00,
  "loyalty_bonus_applied": false,
  "bonus_amount": 0.00,
  "savepoint_demo": "ROLLBACK TO SAVEPOINT 'transfer_complete' was executed. Bonus of 2.50 was undone, but the transfer of 50.00 was preserved and committed. This demonstrates partial rollback using savepoints!"
}
```

**What Happened (IMPORTANT):**
- ✅ Transfer of 50.00 was successful (ACC001: 900 → 850, ACC003: 2000 → 2050)
- ❌ Bonus calculation failed after SAVEPOINT 'transfer_complete' was created
- ⚡ ROLLBACK TO SAVEPOINT 'transfer_complete' was called
- ✅ Bonus was rolled back (NOT applied)
- ✅ Transfer remained intact and was committed
- **This demonstrates PARTIAL ROLLBACK using savepoints!**

**Why This is Important:**
- Without savepoints: The ENTIRE transaction would rollback (transfer AND attempt to apply bonus)
- With savepoints: Only the bonus part was rolled back, transfer succeeded
- Real-world use: You don't lose the main operation if an optional add-on fails

**Verification in Database:**
```sql
SELECT account_number, balance FROM accounts WHERE account_number IN ('ACC001', 'ACC003');
```
Expected:
- ACC001: 850.00 (100 transferred)
- ACC003: 2050.00 (50 transferred, NO 2.50 bonus)

---

## Postman Collection JSON

Copy this into Postman as a collection for easy testing:

```json
{
  "info": {
    "name": "Savepoint Demo Collection",
    "description": "Testing SQL Savepoints with Transfer & Loyalty Bonus"
  },
  "item": [
    {
      "name": "Create Account A",
      "request": {
        "method": "POST",
        "url": "http://localhost:8000/accounts",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"account_number\": \"ACC001\", \"owner_email\": \"alice@example.com\", \"initial_balance\": 1000.00}"
        }
      }
    },
    {
      "name": "Create Account B",
      "request": {
        "method": "POST",
        "url": "http://localhost:8000/accounts",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"account_number\": \"ACC002\", \"owner_email\": \"bob@example.com\", \"initial_balance\": 500.00}"
        }
      }
    },
    {
      "name": "Create Account C",
      "request": {
        "method": "POST",
        "url": "http://localhost:8000/accounts",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"account_number\": \"ACC003\", \"owner_email\": \"charlie@example.com\", \"initial_balance\": 2000.00}"
        }
      }
    },
    {
      "name": "Transfer with Loyalty (SUCCESS)",
      "request": {
        "method": "POST",
        "url": "http://localhost:8000/transactions/transfer-with-loyalty?simulate_bonus_error=false",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"source_account_number\": \"ACC001\", \"destination_account_number\": \"ACC002\", \"amount\": 100.00}"
        }
      }
    },
    {
      "name": "Transfer with Loyalty (SAVEPOINT ROLLBACK)",
      "request": {
        "method": "POST",
        "url": "http://localhost:8000/transactions/transfer-with-loyalty?simulate_bonus_error=true",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"source_account_number\": \"ACC001\", \"destination_account_number\": \"ACC003\", \"amount\": 50.00}"
        }
      }
    }
  ]
}
```

---

## SQL Queries to Verify State

### Check Account Balances:
```sql
SELECT account_number, balance, updated_at FROM accounts ORDER BY account_number;
```

### Check Transaction History:
```sql
SELECT * FROM transactions ORDER BY created_at DESC;
```

### Verify Savepoint Behavior:
```sql
-- If bonus was applied (successful scenario)
SELECT 
  account_number,
  balance,
  CASE
    WHEN balance = 1000.00 THEN 'Unchanged'
    WHEN balance = 900.00 THEN 'Transferred 100'
    WHEN balance = 605.00 THEN 'Received 100 + 5 bonus'
    ELSE 'Check manually'
  END as status
FROM accounts
WHERE account_number IN ('ACC001', 'ACC002', 'ACC003');
```

---

## Key Takeaways

### What Savepoints Accomplish:
1. **Partial Rollback**: Undo only part of a transaction
2. **Nested Transactions**: Create multiple rollback points
3. **Error Recovery**: Handle errors without losing earlier work
4. **Flexibility**: Choose what to commit and what to rollback

### When to Use Savepoints:
- Optional operations that might fail (like bonus calculation)
- Multi-step processes where later steps are less critical
- Complex workflows with nested error handling
- Payment systems with optional fees/bonuses

### In Production:
```python
async with session.begin_nested():  # Creates savepoint
    try:
        # Do optional work
        await perform_optional_operation()
    except Exception:
        # Rollback nested transaction only
        pass  # SQLAlchemy automatically rolls back
```

---

## Troubleshooting

### Issue: "Account not found"
**Solution**: Ensure accounts were created with exact names (ACC001, ACC002, ACC003)

### Issue: "Insufficient balance"
**Solution**: Check current balance with GET /accounts/{account_number}

### Issue: "Connection refused"
**Solution**: Start the FastAPI app: `python3 main.py`

### Issue: "ROLLBACK to savepoint failed"
**Solution**: PostgreSQL backend required (not SQLite). Check connection string in `.env`

---

## Advanced Testing

### Test 1: Multiple Savepoints
Create nested savepoints to test multiple levels:
```python
SAVEPOINT level1
  SAVEPOINT level2
    # Do work
  ROLLBACK TO level2
  # Continue with level1
COMMIT
```

### Test 2: Large Transfers
Test with amounts > 500 to see if bonus calculation works correctly:
```json
{
  "amount": 500.00  // Bonus would be 25.00
}
```

### Test 3: Edge Cases
- Transfer amount = 0.01 (bonus = 0.00)
- Transfer to same account (should fail)
- Insufficient balance (should fail before savepoint)

---

## Response Field Explanations

| Field | Meaning |
|-------|---------|
| `status` | "completed" = full success, "bonus_rolled_back" = partial success |
| `savepoint_demo` | Technical explanation of which savepoint was used |
| `bonus_amount` | Amount of 5% bonus applied (0 if rolled back) |
| `loyalty_bonus_applied` | Boolean: was bonus successfully applied? |
| Source/Destination balance before/after | Track exact changes |

---

## Conclusion

The `/transfer-with-loyalty` endpoint successfully demonstrates:
- ✅ SQL SAVEPOINT creation and usage
- ✅ Partial transaction rollback
- ✅ Atomicity with granular control
- ✅ Real-world error handling patterns

Test both scenarios to see savepoints in action!
