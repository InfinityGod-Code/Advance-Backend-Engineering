## CASBIN WORKFLOW 
Uvicorn Process Starts
   │
   ▼
FastAPI triggers the 'lifespan' function
   │
   ├─► 1. DB engine establishes connection pool.
   ├─► 2. Casbin SQL Adapter issues a check to PostgreSQL.
   ├─► 3. 'casbin_rule' table is validated/created if missing.
   └─► 4. 'load_policy()' pulls all rows from Postgres into RAM.
   │
   ▼
Memory Graph compiled successfully!
   │
   ▼
Application reaches the 'yield' statement
   │
   ▼
FastAPI opens ports and begins accepting public incoming web requests

#### Why This Architecture Matters for Security

- Fails Closed on DB Faults: If your PostgreSQL database is down or experiencing network lag during server boot, ProductionEnforcer.initialize() will raise an exception and crash the boot sequence. This is a critical security property called failing closed—it prevents your application from scaling up healthy containers that are completely blank of access control rules.

- No Cold Starts: The first user to hit your API doesn't suffer from a slow request because the database was hit to check their permissions; the tables were parsed and indexed into cache before they even loaded the login page.


#### How to test and Verify
-  As of now we have to send x-test-user and x-test-tenant in the headers section.
- In the production level we generally send these in the JWT claims sections.
- We can make test for both scenarios first for the positive flows and then negative by putting wrong in order.
-       r_sub = current_user.user_id      # Who is making the request
        r_dom = current_user.tenant_id    # What tenant are they acting in
        r_obj = request.url.path          # The target path (e.g., /api/v1/my-wallet)
        r_act = self.action               # The action requested (e.g., read, write)
- For example, if we check **/api/v1/my-wallet** and we provide 
  x-test-user = employee
  x-test-tenant = company_abc 
  then it will pass because this exactly match with the casbin configuration we have seeded in the database.
  anything violating this will cause 403 status error access denied.