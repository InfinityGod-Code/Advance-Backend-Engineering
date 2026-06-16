from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import create_db_tables
from app.utility.casbin_enforcer import ProductionEnforcer
from app.routes import router as auth_route

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
async def lifespan(app: FastAPI):
    await create_db_tables()
    # 2. ⚡ INITIALIZE CASBIN SINGLETON HERE
    # Connects to PostgreSQL, reads rules, builds the in-memory graph cache
    # Generally we will initializing this as separate script in the docker 
    ProductionEnforcer.initialize()
    yield


app = FastAPI(title="Casbin-Authorize", description=app_decription, lifespan=lifespan)

app.include_router(auth_route)


