# migrate_auth.py
import sys
from app.utility.casbin_enforcer import ProductionEnforcer

def run_migration():
    print("🚀 Starting Production Authorization Matrix Migration...")
    try:
        # This will connect to Postgres, load policies, and run the seed loop once
        ProductionEnforcer.initialize()
        print("✅ Authorization matrix migration completed successfully.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()