## Our Organization Plan 

#### We are going to build this plan in the same order as described below : 

[PLATFORM SPHERE]
 └── System SuperAdmin (Global Cloud Ops)
      └── Customer Support Tier 2 (Read-only access across tenants for debugging)

[TENANT SPHERE (Company ABC)]
 └── Organization Owner / Tenant Admin (Ultimate Root for the Client)
      ├── FINANCE BRANCH
      │    └── Chief Financial Officer / Accountant (Manages corporate ledger, bank connections)
      └── OPERATIONS BRANCH
           └── Department Head / Regional Manager
                └── Team Lead / local Manager
                     └── Base Employee / Card Holder (Can only request/spend)


## Points to Ponder for the CASBIN process :

- What it looks like inside PostgreSQL
The adapter creates a single database table named casbin_rule. Because different policy structures (p or g) use varying numbers of parameters, Casbin maps everything to a highly flexible generic column structure (v0 through v5).

To view your active access control sheets in production, run this standard SQL command in your terminal or database GUI (like PgAdmin or DBeaver)

# The Live Database Rows Representation

| id | ptype | v0 (sub)            | v1 (dom)               | v2 (obj)           | v3 (act) | v4   | Notes                |
| -- | ----- | ------------------- | ---------------------- | ------------------ | -------- | ---- | -------------------- |
| 1  | p     | platform_superadmin | *                      | /api/v1/platform/* | *        | NULL | Platform Capability  |
| 2  | p     | employee            | company_abc            | /api/v1/my-wallet  | read     | NULL | Tenant Policy        |
| 3  | g     | regional_manager    | manager                | company_abc        | NULL     | NULL | Operations Hierarchy |
| 4  | g     | tenant_admin        | accountant             | company_abc        | NULL     | NULL | Admin Convergence    |
| 5  | g     | alice               | tenant_admin           | company_abc        | NULL     | NULL | User Assignment      |
| 6  | g     | support_sam         | customer_support_tier2 | platform_global    | NULL     | NULL | Platform Worker      |

## Column Meaning

| Column | Description                                                             |
| ------ | ----------------------------------------------------------------------- |
| id     | Primary key of the Casbin rule record                                   |
| ptype  | Policy type (`p` = permission policy, `g` = grouping/role relationship) |
| v0     | Subject (user or role)                                                  |
| v1     | Domain / Tenant                                                         |
| v2     | Object / Resource                                                       |
| v3     | Action                                                                  |
| v4     | Optional extra field                                                    |
| Notes  | Human-readable explanation                                              |

## Interpretation

### Permission Policies (`ptype = p`)

| Subject             | Domain      | Resource           | Action |
| ------------------- | ----------- | ------------------ | ------ |
| platform_superadmin | *           | /api/v1/platform/* | *      |
| employee            | company_abc | /api/v1/my-wallet  | read   |

### Role Hierarchy & Assignments (`ptype = g`)

| Member           | Assigned Role          | Domain          |
| ---------------- | ---------------------- | --------------- |
| regional_manager | manager                | company_abc     |
| tenant_admin     | accountant             | company_abc     |
| alice            | tenant_admin           | company_abc     |
| support_sam      | customer_support_tier2 | platform_global |


- How Casbin Compares Each Time Efficiently

Casbin never hits the database during an evaluation request.Here is the exact mechanical pipeline that keeps Casbin operating at lightning-fast speed ($\approx 1$ to $10$ microseconds per check):
1. In-Memory Graph CompilationWhen your application initializes via enforcer.load_policy(), Casbin executes a single SELECT * query to fetch the entire casbin_rule table. It takes those raw database records and compiles them into a highly optimized, specialized In-Memory Directed Acyclic Graph (DAG) and an index array.

2. Microsecond Evaluation EngineWhen an API call executes enforcer.enforce("alice", "company_abc", "/api/v1/my-wallet", "read"):No SQL Query Runs: The database remains completely untouched.Adjacency List Traversal: Casbin accesses its local memory cache graph. It instantly resolves Alice's roles by traversing the pre-built pointer paths (alice $\rightarrow$ tenant_admin $\rightarrow$ accountant/regional_manager $\rightarrow$ employee).Bitwise & Hash Lookups: The matching conditions (like checking strings or resolving paths via keyMatch2) are executed entirely as raw CPU mathematical and regex index lookups inside RAM.

3. How Changes Are Synced NativelyIf you grant an employee a new role via your administration control dashboard:You execute enforcer.add_grouping_policy("david", "manager", "company_abc").The Casbin adapter generates and fires a fast, targeted INSERT INTO casbin_rule ... query directly to PostgreSQL so the rule is saved safely to disk.Simultaneously, Casbin updates its local internal RAM memory matrix to include the new graph connection.This ensures that subsequent API authorization checks evaluate the updated rule structure instantly, bypassing the need to reboot your application or query PostgreSQL again.

