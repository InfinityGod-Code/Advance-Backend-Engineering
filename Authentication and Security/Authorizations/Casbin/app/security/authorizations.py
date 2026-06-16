from fastapi import Depends, HTTPException, Request,status
from pydantic import BaseModel
from app.utility.casbin_enforcer import ProductionEnforcer



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



