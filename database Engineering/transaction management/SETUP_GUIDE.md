# Quick Setup Guide

## Files Created

### 1. **app/schemas/account_schema.py**
   - `AccountCreateRequest` - Schema for creating accounts
   - `AccountResponse` - Schema for account responses
   - `AccountUpdateRequest` - Schema for updating accounts

### 2. **app/service/account_service.py**
   - `AccountService` - Business logic for account operations
   - Methods: `create_account()`, `get_account()`, `list_accounts()`, `update_account()`, `get_account_by_number()`

### 3. **app/database/init_db.py**
   - Database initialization script to create all tables

### 4. **Updated app/route/accounts.py**
   - `POST /accounts/` - Create new account
   - `GET /accounts/` - List all accounts
   - `GET /accounts/{account_id}` - Get specific account
   - `PATCH /accounts/{account_id}` - Update account

### 5. **Package Structure**
   - Created `__init__.py` files in all directories for proper Python package structure

---

## Getting Started

### Step 1: Install Dependencies
```bash
cd "database Engineering/transaction management"
uv sync
```

### Step 2: Initialize Database Schema
```bash
uv run python -m app.database.init_db
```

Expected output:
```
INFO:__main__:Creating database tables...
INFO:__main__:✓ Database schema initialized successfully!
INFO:__main__:✓ Created table: accounts
```

### Step 3: Start the Application
```bash
uv run uvicorn main:app --reload
```

The API will be available at:
- **API Base URL**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

---

## Testing the Endpoints

### Using cURL

#### 1. Create an Account
```bash
curl -X POST "http://localhost:8000/accounts/" \
  -H "Content-Type: application/json" \
  -d '{
    "account_number": "ACC-001",
    "owner_email": "user@example.com",
    "initial_balance": 5000.00
  }'
```

#### 2. List All Accounts
```bash
curl "http://localhost:8000/accounts/"
```

#### 3. Get Specific Account
```bash
curl "http://localhost:8000/accounts/{account_id}"
```

#### 4. Update Account
```bash
curl -X PATCH "http://localhost:8000/accounts/{account_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "owner_email": "newemail@example.com",
    "is_active": false
  }'
```

---

## Database Schema

**Table: accounts**

| Column | Type | Constraints | Description |
|--------|------|-----------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| account_number | VARCHAR(50) | UNIQUE, NOT NULL | Account number |
| owner_email | VARCHAR | NOT NULL | Owner email |
| balance | DECIMAL(19,2) | DEFAULT 0.00 | Account balance |
| version | INT | DEFAULT 1 | Concurrency control |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_at | TIMESTAMP | | Creation timestamp |
| updated_at | TIMESTAMP | | Update timestamp |

---

## API Response Examples

### Create Account (201 Created)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "account_number": "ACC-001",
  "owner_email": "user@example.com",
  "balance": 5000.00,
  "version": 1,
  "is_active": true,
  "created_at": "2024-06-06T16:47:09.643",
  "updated_at": "2024-06-06T16:47:09.643"
}
```

### Error (409 Conflict)
```json
{
  "detail": "Account with number ACC-001 already exists"
}
```

### Error (404 Not Found)
```json
{
  "detail": "Account with ID 550e8400-e29b-41d4-a716-446655440000 not found"
}
```

---

## Key Features

✅ **Async/Await** - Non-blocking database operations
✅ **Type Safety** - Pydantic validation for all inputs
✅ **Error Handling** - Comprehensive error responses with proper HTTP status codes
✅ **Isolation** - Version field for optimistic concurrency control
✅ **Unique Constraints** - Account numbers are unique
✅ **Timestamps** - Audit trail with created_at and updated_at
✅ **Decimal Precision** - Accurate financial calculations

---

## Project Structure

```
app/
├── __init__.py
├── config/
│   ├── __init__.py
│   └── database_config.py              # DB configuration
├── database/
│   ├── __init__.py
│   ├── database.py                     # Engine & session
│   └── init_db.py                      # Schema initialization
├── dependancies/
│   ├── __init__.py
│   └── dependancy.py                   # FastAPI dependencies
├── models/
│   ├── __init__.py
│   └── m_account.py                    # SQLModel definition
├── route/
│   ├── __init__.py
│   └── accounts.py                     # Account routes (UPDATED)
├── schemas/
│   ├── __init__.py
│   └── account_schema.py               # Request/response schemas (NEW)
└── service/
    ├── __init__.py
    └── account_service.py              # Business logic (NEW)
```

---

## Troubleshooting

### Import Errors
If you see module not found errors, ensure dependencies are installed:
```bash
uv sync
```

### Database Connection Errors
Check your `.env` file:
- `POSTGRES_SERVER` should be "localhost" (or your DB host)
- `POSTGRES_PORT` should be 5432
- `POSTGRES_USER` and `POSTGRES_PASSWORD` must match your PostgreSQL setup
- `POSTGRES_DB` must exist

### Port Already in Use
If port 8000 is in use, specify a different port:
```bash
uv run uvicorn main:app --reload --port 8001
```

---

## Next Steps

Ready to implement:
- Transaction transfers between accounts
- Transaction history/audit log
- Interest calculations
- Account reconciliation
- Authentication & authorization

See `API_DOCUMENTATION.md` for complete API documentation.
