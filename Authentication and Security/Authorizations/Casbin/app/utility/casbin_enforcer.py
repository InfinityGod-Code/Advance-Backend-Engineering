import os
import casbin
from casbin_sqlalchemy_adapter import Adapter
from app.config import database_settings


class ProductionEnforcer:
    _instance = None
    
    # Core Capabilities (p rules): (sub, dom, obj, act)
    _POLICIES_TO_SEED = [
        # 🌐 PLATFORM SPHERE PERMISSIONS
        ("platform_superadmin", "*", "/api/v1/platform/*", "*"),
        ("platform_superadmin", "*", "/api/v1/tenants", "write"),
        ("customer_support_tier2", "*", "/api/v1/tenants/:tenant_id/debug-logs", "read"),
        ("customer_support_tier2", "*", "/api/v1/tenants/:tenant_id/metadata", "read"),

        # 🏢 TENANT SPHERE PERMISSIONS (Example Tenant: company_abc)
        # Organization Owner / Tenant Admin Unique Scopes
        ("tenant_admin", "company_abc", "/api/v1/tenant/settings", "write"),
        ("tenant_admin", "company_abc", "/api/v1/tenant/billing/*", "*"),
        ("tenant_admin", "company_abc", "/api/v1/tenant/integrations/sso", "write"),

        # Finance Branch (Accountant / CFO)
        ("accountant", "company_abc", "/api/v1/finance/ledger*", "*"),
        ("accountant", "company_abc", "/api/v1/finance/bank-connections", "*"),
        ("accountant", "company_abc", "/api/v1/cards/issue", "write"),

        # Operations Branch: Regional Manager Unique Scopes
        ("regional_manager", "company_abc", "/api/v1/ops/regions/:region_id/budgets", "write"),
        ("regional_manager", "company_abc", "/api/v1/ops/regions/transfer", "write"),

        # Operations Branch: Local Manager Scopes
        ("manager", "company_abc", "/api/v1/ops/department/expenses/:id/approve", "write"),
        ("manager", "company_abc", "/api/v1/ops/department/expenses/:id/reject", "write"),
        ("manager", "company_abc", "/api/v1/ops/team/roster", "read"),

        # Operations Branch: Base Employee / Card Holder Scopes
        ("employee", "company_abc", "/api/v1/my-wallet", "read"),
        ("employee", "company_abc", "/api/v1/my-expenses", "write"),
        ("employee", "company_abc", "/api/v1/my-expenses/:id", "read"),
    ]

    # Functional Role Hierarchies (g rules): (sub_role, parent_role, domain)
    _GROUPINGS_TO_SEED = [
        # 🌐 PLATFORM SPHERE INHERITANCE
        ("platform_superadmin", "customer_support_tier2", "platform_global"),

        # 🏢 TENANT SPHERE INHERITANCE (Example Tenant: company_abc)
        # Operations Branch Tree (Regional Manager -> Manager -> Employee)
        ("regional_manager", "manager", "company_abc"),
        ("manager", "employee", "company_abc"),
        
        # Root Tenant Admin Convergence (Owner inherits both Finance and Ops trees)
        ("tenant_admin", "accountant", "company_abc"),
        ("tenant_admin", "regional_manager", "company_abc"),
    ]

    @classmethod
    def initialize(cls):
        if cls._instance is None:
            # 1. Initialize the adapter connected to PostgreSQL
            adapter = Adapter(database_settings.POSTGRES_SYNC_URL)
            
            # 2. Reference the abstract path to your casbin configuration
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, "casbin_auth.conf")
            
            # 3. Build the primary enforcer instance
            cls._instance = casbin.Enforcer(model_path, adapter)
            
            # 4. Pull existing system records into warm local RAM memory
            cls._instance.load_policy()
            print("💾 PostgreSQL Casbin Engine synchronized and active.")
            
            # 5. Run idempotent structural seed synchronization
            cls._seed_structural_definitions()

    @classmethod
    def get_enforcer(cls) -> casbin.Enforcer:
        return cls._instance

    @classmethod
    def _seed_structural_definitions(cls):
        """
        Executes an idempotent check across the structural matrices.
        Only commits new additions directly to PostgreSQL if they do not already exist.
        """
        p_added = 0
        g_added = 0

        # Syncing Abstract Capabilities
        for policy in cls._POLICIES_TO_SEED:
            if cls._instance.add_policy(policy[0], policy[1], policy[2], policy[3]):
                p_added += 1

        # Syncing Functional Structural Hierarchies
        for grouping in cls._GROUPINGS_TO_SEED:
            if cls._instance.add_grouping_policy(grouping[0], grouping[1], grouping[2]):
                g_added += 1

        # Transparent architectural metrics logging
        if p_added > 0 or g_added > 0:
            print(f"✨ RBAC Seed Complete: Appended {p_added} capabilities and {g_added} structural hierarchy relations.")
        else:
            print("✅ RBAC Matrix Verification: System structure is completely up to date.")