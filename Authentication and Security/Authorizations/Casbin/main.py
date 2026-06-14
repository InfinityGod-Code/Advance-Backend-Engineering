from fastapi import Depends, FastAPI, HTTPException, Request,status
from contextlib import asynccontextmanager
from app.database import create_db_tables
from app.utility.casbin_enforcer import ProductionEnforcer 
from pydantic import BaseModel


app_decription = """

That project demonstrates the complex usage for access control model like 
 - Access-control list : 
    In computer security, an access-control list (ACL) is a list of permissions[a] associated
    with a system resource (object or facility). An ACL specifies which users or system
    processes are granted access to resources, as well as what operations are allowed on given resources.

- RBAC (Role-Based Access Control) : 
    Role-based access control is a policy-neutral access control mechanism defined around roles and privileges.
    The components of RBAC such as role-permissions, user-role and role-role relationships make
    it simple to perform user assignments.

- ABAC (Attribute-Based Access Control) : 
    Attribute-based access control (ABAC), also known as policy-based access control for IAM,
    defines an access control paradigm whereby a subject's authorization to perform a set of
    operations is determined by evaluating attributes associated with the subject, object,
    requested operations, and, in some cases, environment attributes.

 """

@asynccontextmanager
async def lifespan(app : FastAPI) :
    await create_db_tables()
    # 2. ⚡ INITIALIZE CASBIN SINGLETON HERE
    # Connects to PostgreSQL, reads rules, builds the in-memory graph cache
    ProductionEnforcer.initialize()
    yield

app = FastAPI(
    title="Casbin-Authorize",
    description=app_decription,
    lifespan=lifespan
)


# ==========================================
# 🔐 STEP 1: AUTHENTICATION LAYER (JWT CLAIMS)
# ==========================================
class UserClaims(BaseModel):
    """Represents the decoded data extracted from a valid JWT."""
    user_id: str
    tenant_id: str  # The domain/company this user belongs to

def get_current_user(request: Request) -> UserClaims:
    """
    Production Mock: In a real system, you would read the 'Authorization: Bearer <JWT>' 
    header, cryptographically verify it with your public key, and parse the claims.
    
    To test different roles in your Swagger UI (/docs), simulate users by passing 
    custom headers: 'x-test-user' and 'x-test-tenant'.
    """
    user_id = request.headers.get("x-test-user")
    tenant_id = request.headers.get("x-test-tenant")
    
    if not user_id or not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing valid authentication JWT credentials. Provide headers 'x-test-user' and 'x-test-tenant'."
        )
    
    return UserClaims(user_id=user_id, tenant_id=tenant_id)


# ==========================================
# 🛡️ STEP 2: AUTHORIZATION LAYER (CASBIN GUARD)
# ==========================================
class CasbinGuard:
    """A reusable FastAPI dependency that checks access rights dynamically."""
    def __init__(self, action: str):
        self.action = action

    def __call__(self, request: Request, current_user: UserClaims = Depends(get_current_user)):
        # 1. Fetch our pre-heated in-memory Casbin enforcer
        enforcer = ProductionEnforcer.get_enforcer()
        
        # 2. Extract dynamic parameters
        r_sub = current_user.user_id      # Who is making the request
        r_dom = current_user.tenant_id    # What tenant are they acting in
        r_obj = request.url.path          # The target path (e.g., /api/v1/my-wallet)
        r_act = self.action               # The action requested (e.g., read, write)
        
        # 3. Ask Casbin to traverse its graphs and evaluate the request
        is_authorized = enforcer.enforce(r_sub, r_dom, r_obj, r_act)
        
        if not is_authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied. User '{r_sub}' does not have '{r_act}' privileges on '{r_obj}' inside domain '{r_dom}'."
            )
            
        return current_user


# ==========================================
# 📋 STEP 3: ENDPOINTS FOR MATRIX VALIDATION
# ==========================================

# 🔹 1. BASE EMPLOYEE LEVEL
@app.get("/api/v1/my-wallet", dependencies=[Depends(CasbinGuard(action="read"))])
async def view_wallet():
    """Accessible by: employee, manager, regional_manager, tenant_admin"""
    return {"status": "success", "balance": "$1,250.00", "currency": "USD"}


# 🔹 2. OPERATIONS BRANCH (LOCAL MANAGER AND ABOVE)
@app.post("/api/v1/ops/department/expenses/42/approve", dependencies=[Depends(CasbinGuard(action="write"))])
async def approve_expense():
    """Accessible by: manager, regional_manager, tenant_admin (Blocked for: employee, accountant)"""
    return {"status": "success", "message": "Expense #42 approved for payment."}


# 🔹 3. FINANCE BRANCH (ACCOUNTANT AND OWNER)
@app.get("/api/v1/finance/ledger-entries", dependencies=[Depends(CasbinGuard(action="read"))])
async def view_ledger():
    """Accessible by: accountant, tenant_admin (Blocked for: manager, employee)"""
    return {"status": "success", "records": "Corporate Ledger Entries Matrix Root"}


# 🔹 4. GLOBAL PLATFORM SPHERE (SAAS SUPPORT & SUPERADMIN ONLY)
@app.get("/api/v1/tenants/company_abc/debug-logs", dependencies=[Depends(CasbinGuard(action="read"))])
async def read_tenant_logs():
    """Accessible by: platform_superadmin, customer_support_tier2 (Blocked for ALL tenant users!)"""
    return {"status": "success", "system_logs": "System container performance normal."}

@app.get("/")
def home()  :
    return {
        "content" : "Hello World"
    }
