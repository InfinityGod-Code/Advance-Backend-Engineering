from fastapi import APIRouter, Depends
from app.security.authorizations import CasbinGuard
router = APIRouter(prefix="/api/v1")



# 1. BASE EMPLOYEE LEVEL
@router.get("/my-wallet", dependencies=[Depends(CasbinGuard(action="read"))])
async def view_wallet():
    """Accessible by: employee, manager, regional_manager, tenant_admin"""
    return {"status": "success", "balance": "$1,250.00", "currency": "USD"}


# 2. OPERATIONS BRANCH (LOCAL MANAGER AND ABOVE)
@router.post("/ops/department/expenses/42/approve", dependencies=[Depends(CasbinGuard(action="write"))])
async def approve_expense():
    """Accessible by: manager, regional_manager, tenant_admin (Blocked for: employee, accountant)"""
    return {"status": "success", "message": "Expense #42 approved for payment."}


# 3. FINANCE BRANCH (ACCOUNTANT AND OWNER)
@router.get("/finance/ledger-entries", dependencies=[Depends(CasbinGuard(action="read"))])
async def view_ledger():
    """Accessible by: accountant, tenant_admin (Blocked for: manager, employee)"""
    return {"status": "success", "records": "Corporate Ledger Entries Matrix Root"}


# 4. GLOBAL PLATFORM SPHERE (SAAS SUPPORT & SUPERADMIN ONLY)
@router.get("/tenants/company_abc/debug-logs", dependencies=[Depends(CasbinGuard(action="read"))])
async def read_tenant_logs():
    """Accessible by: platform_superadmin, customer_support_tier2 (Blocked for ALL tenant users!)"""
    return {"status": "success", "system_logs": "System container performance normal."}

@router.get("/")
def home()  :
    return {
        "content" : "Hello World"
    }