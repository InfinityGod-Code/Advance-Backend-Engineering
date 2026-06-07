# Account Management API Documentation

## Overview

This documentation covers the newly created Account Management API endpoints and database schema. The system demonstrates ACID properties through practical account management operations.

---

## Database Schema

### Accounts Table Structure

```sql
accounts (
    id UUID PRIMARY KEY,
    account_number VARCHAR(50) UNIQUE NOT NULL,
    owner_email VARCHAR NOT NULL,
    balance DECIMAL(19, 2) DEFAULT 0.00,
    version INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Field Descriptions

| Field | Type | Constraints | Purpose |
|-------|------|-----------|---------|
| `id` | UUID | PRIMARY KEY, INDEX | Unique identifier (Primary Key Constraint) |
| `account_number` | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | Unique account identifier (Consistency) |
| `owner_email` | VARCHAR | NOT NULL | Email of account owner |
| `balance` | DECIMAL(19, 2) | DEFAULT 0.00 | Current balance (Atomicity demonstration) |
| `version` | INT | DEFAULT 1 | Optimistic concurrency control (Isolation) |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account status |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Account creation time (Durability) |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Last modification time (Durability) |

---

## Setup Instructions

### 1. Initialize Database Schema

Run the initialization script to create all tables:

```bash
cd "/Users/shubhamsrivastava/Desktop/Advance-Backend-Engineering/database Engineering/transaction management"
python -m app.database.init_db
```

**Expected Output:**
```
INFO:__main__:Creating database tables...
INFO:__main__:✓ Database schema initialized successfully!
INFO:__main__:✓ Created table: accounts
```

### 2. Start the Application

```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

---

## API Endpoints

### 1. Create Account

**Endpoint:** `POST /accounts/`

**Description:** Creates a new account with initial balance

**Request Body:**
```json
{
  "account_number": "ACC-001",
  "owner_email": "user@example.com",
  "initial_balance": 5000.00
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "account_number": "ACC-001",
  "owner_email": "user@example.com",
  "balance": 5000.00,
  "version": 1,
  "is_active": true,
  "created_at": "2024-06-06T16:47:09.643000",
  "updated_at": "2024-06-06T16:47:09.643000"
}
```

**Error Responses:**
- `409 Conflict` - Account number already exists
- `422 Unprocessable Entity` - Invalid input data
- `500 Internal Server Error` - Database error

**Example Request:**
```bash
curl -X POST "http://localhost:8000/accounts/" \
  -H "Content-Type: application/json" \
  -d '{
    "account_number": "ACC-001",
    "owner_email": "john@example.com",
    "initial_balance": 1000.00
  }'
```

---

### 2. Get Account by ID

**Endpoint:** `GET /accounts/{account_id}`

**Description:** Retrieves a specific account by its ID

**URL Parameters:**
- `account_id` (UUID): The unique account identifier

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "account_number": "ACC-001",
  "owner_email": "user@example.com",
  "balance": 5000.00,
  "version": 1,
  "is_active": true,
  "created_at": "2024-06-06T16:47:09.643000",
  "updated_at": "2024-06-06T16:47:09.643000"
}
```

**Error Responses:**
- `404 Not Found` - Account doesn't exist

**Example Request:**
```bash
curl "http://localhost:8000/accounts/550e8400-e29b-41d4-a716-446655440000"
```

---

### 3. List All Accounts

**Endpoint:** `GET /accounts/`

**Description:** Retrieves all accounts (ordered by creation date, newest first)

**Response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "account_number": "ACC-001",
    "owner_email": "user@example.com",
    "balance": 5000.00,
    "version": 1,
    "is_active": true,
    "created_at": "2024-06-06T16:47:09.643000",
    "updated_at": "2024-06-06T16:47:09.643000"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "account_number": "ACC-002",
    "owner_email": "jane@example.com",
    "balance": 2500.50,
    "version": 2,
    "is_active": true,
    "created_at": "2024-06-06T16:50:00.000000",
    "updated_at": "2024-06-06T16:52:00.000000"
  }
]
```

**Example Request:**
```bash
curl "http://localhost:8000/accounts/"
```

---

### 4. Update Account

**Endpoint:** `PATCH /accounts/{account_id}`

**Description:** Updates account details (email or active status)

**URL Parameters:**
- `account_id` (UUID): The unique account identifier

**Request Body:**
```json
{
  "owner_email": "newemail@example.com",
  "is_active": false
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "account_number": "ACC-001",
  "owner_email": "newemail@example.com",
  "balance": 5000.00,
  "version": 2,
  "is_active": false,
  "created_at": "2024-06-06T16:47:09.643000",
  "updated_at": "2024-06-06T16:52:30.000000"
}
```

**Error Responses:**
- `404 Not Found` - Account doesn't exist

**Example Request:**
```bash
curl -X PATCH "http://localhost:8000/accounts/550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "owner_email": "updated@example.com",
    "is_active": true
  }'
```

---

## Project Structure

```
app/
├── __init__.py
├── config/
│   ├── __init__.py
│   └── database_config.py          # Database configuration
├── database/
│   ├── __init__.py
│   ├── database.py                 # Engine and session setup
│   └── init_db.py                  # Schema initialization script
├── dependancies/
│   ├── __init__.py
│   └── dependancy.py               # FastAPI dependencies
├── models/
│   ├── __init__.py
│   └── m_account.py                # SQLModel definitions
├── route/
│   ├── __init__.py
│   └── accounts.py                 # Account API routes
├── schemas/
│   ├── __init__.py
│   └── account_schema.py           # Pydantic request/response schemas
└── service/
    ├── __init__.py
    └── account_service.py          # Business logic layer
```

---

## Key Features

### ACID Properties Demonstration

- **Atomicity**: Balance transfers use transactions (future implementation)
- **Consistency**: UNIQUE and NOT NULL constraints on critical fields
- **Isolation**: Version field enables optimistic concurrency control
- **Durability**: Timestamps track creation and modifications

### Error Handling

All endpoints implement comprehensive error handling:
- Validation errors with detailed messages
- Duplicate account detection (409 Conflict)
- Not found errors (404)
- Database errors with rollback support

### Best Practices

- Async/await pattern for non-blocking I/O
- Dependency injection for session management
- Service layer separation for business logic
- Pydantic validation for type safety
- Decimal type for accurate financial calculations

---

## Testing

### Quick Test Script

```python
import httpx
import asyncio

async def test_api():
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # Create account
        response = await client.post(
            f"{base_url}/accounts/",
            json={
                "account_number": "TEST-001",
                "owner_email": "test@example.com",
                "initial_balance": 1000.00
            }
        )
        account = response.json()
        print(f"Created: {account}")
        
        # Get account
        response = await client.get(
            f"{base_url}/accounts/{account['id']}"
        )
        print(f"Retrieved: {response.json()}")
        
        # List accounts
        response = await client.get(f"{base_url}/accounts/")
        print(f"All accounts: {response.json()}")

asyncio.run(test_api())
```

---

## Environment Configuration

Update `.env` file with your PostgreSQL credentials:

```env
POSTGRES_SERVER="localhost"
POSTGRES_PORT=5432
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="your_password"
POSTGRES_DB="transactions_management"
```

---

## Next Steps

Potential enhancements:
- ✅ Account transfer with transaction management
- ✅ Transaction history/audit log
- ✅ Account reconciliation
- ✅ Interest calculation
- ✅ Account suspension/closure logic
- ✅ Authentication and authorization
