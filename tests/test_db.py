from sqlalchemy import inspect
from src.db.database import engine, init_db

def test_database_initialization():
    """Tests if SQLAlchemy can successfully build the schemas in Postgres."""
    # 1. Trigger the schema creation
    init_db()
    
    # 2. Inspect the live database engine
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    # 3. Verify all our tables were created
    assert "projects" in tables, "Missing projects table!"
    assert "model_runs" in tables, "Missing model_runs table!"
    assert "telemetry_data" in tables, "Missing telemetry_data table!"
    
    print("✅ Database schemas successfully created and verified!")