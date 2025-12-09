# backend/db_connector.py
# Uses asyncpg for non-blocking PostgreSQL access.

import asyncpg
import logging
from datetime import datetime
from .config import Config

# Global connection pool placeholder
pool = None
logger = logging.getLogger(__name__)

async def connect_db():
    """Initializes the global asynchronous connection pool."""
    global pool
    if pool is None:
        try:
            # Create a pool of connections using Config settings
            pool = await asyncpg.create_pool(
                host=Config.POSTGRES_HOST,
                database=Config.POSTGRES_DB,
                user=Config.POSTGRES_USER,
                password=Config.POSTGRES_PASSWORD,
                min_size=1,
                max_size=10
            )
            logger.info("AsyncPG pool created successfully.")
        except Exception as e:
            logger.error(f"Failed to create AsyncPG pool: {e}")
            raise ConnectionError("Could not connect to the PostgreSQL database.") from e
    return pool

async def disconnect_db():
    """Closes the connection pool gracefully."""
    global pool
    if pool:
        await pool.close()
        pool = None
        logger.info("AsyncPG pool closed.")

async def initialize_schema_and_seed_data():
    """Initializes the database schema and inserts seed data if the table is new."""
    
    if pool is None:
        await connect_db()

    # Acquire connection from the pool for initialization tasks
    conn = await pool.acquire()
    try:
        # Check for table existence
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM pg_tables
                WHERE schemaname = 'public' AND tablename  = 'test_entries'
            );
        """)

        if not table_exists:
            logger.warning("Table 'test_entries' not found. Creating schema and inserting seed data...")
            
            # Create the table using PostgreSQL data types
            await conn.execute("""
                CREATE TABLE test_entries (
                    id SERIAL PRIMARY KEY,
                    feature TEXT NOT NULL,
                    sub_feature TEXT NOT NULL,
                    test_case TEXT NOT NULL,
                    linked_issue TEXT,             
                    selenium_test TEXT,            
                    api_test TEXT,                 
                    notes TEXT,
                    
                    status_edge TEXT NOT NULL,
                    status_chrome TEXT NOT NULL,
                    status_firefox TEXT NOT NULL,
                    
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # --- Seed Data Insertion (10 Records) ---
            seed_data = [
                ('3D Visualizer', 'General', 'Verify model rotation on mouse drag (TC-001)', '', 'test_rotate_model', '', 'Checked against specification v2.1. [Confluence Link: https://wiki.company.com/pages/viewpage.action?pageId=98765]', 'OK', 'OK', 'OK'),
                ('3D Visualizer', 'Model Loading', 'Check loading support for .pdbgz format on low bandwidth (TC-002)', 'LDQA-498', 'test_pdb_load_fail', '', 'Fails only on Firefox due to WebGL context loss. Tracking in JIRA.', 'OK', 'JIRA/Issue', 'JIRA/Issue'),
                ('Sequence Viewer Sync', 'Selection Sync', 'Selecting residue highlights in 3D (TC-003)', '', '', 'test_seq_sync_api', 'Automated API test passed. Manual verification pending.', 'AUTO_PASS', 'AUTO_PASS', 'AUTO_PASS'),
                ('Sequence Viewer Sync', 'Zoom Behavior', 'Zooming in sequence viewer correctly reflects scale in 3D (TC-004)', '', '', '', '', 'NOT-TESTED', 'NOT-TESTED', 'NOT-TESTED'),
                ('Data Grid', '3D Column', 'Opening 3D model when data is NULL (TC-005)', 'LDQA-501', 'test_null_data', 'test_grid_api_err', 'API returns 404. Should return a graceful "No 3D Data" message. [Google Doc Link: https://docs.google.com/document/d/1XyZ...]', 'FAIL', 'FAIL', 'AUTO_FAIL'),
                ('UI/UX', 'Tooltips', 'Verify protein/ligand tooltips show correct metadata (TC-006)', '', 'test_tooltip_presence', '', 'Tooltip data source confirmed correct. No visual defects found.', 'OK', 'OK', 'OK'),
                ('Data Grid', 'Filtering', 'Filtering the grid correctly updates 3D content (TC-007)', '', 'test_grid_filter', '', 'Filtering works as expected. Performance is slow on large data sets.', 'OK', 'OK', 'OK'),
                ('3D Visualizer', 'Style Presets', 'Applying custom style preset is preserved across reloads (TC-008)', '', '', '', 'Manual test passed. Used Confluence article for steps: [Confluence Link: https://wiki.company.com/pages/viewpage.action?pageId=98765]', 'OK', 'OK', 'OK'),
                ('Performance', 'Initial Load', 'Time taken to render largest model is under 3 seconds (TC-009)', 'LDQA-509', '', 'test_perf_load', 'Intermittent performance issues observed in MS-Edge, causing FAIL status.', 'JIRA/Issue', 'OK', 'OK'),
                ('Aesthetics', 'Color Schemes', 'Verify dark mode color palette rendering (TC-010)', '', '', '', '', 'BLANK', 'BLANK', 'BLANK'),
            ]
            
            insert_query = """
                INSERT INTO test_entries (
                    feature, sub_feature, test_case, linked_issue, selenium_test, api_test, notes,
                    status_edge, status_chrome, status_firefox
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """
            # Use execute_many for efficient batch insertion
            await conn.executemany(insert_query, seed_data)
            logger.info("Database schema created and seed data inserted.")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise e 
    finally:
        # Release the connection back to the pool
        await pool.release(conn)
