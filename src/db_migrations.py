"""Database migration system using Alembic"""
import os
from alembic import command
from alembic.config import Config
import logging

logger = logging.getLogger(__name__)

class MigrationManager:
    """Manage database migrations"""
    
    def __init__(self, alembic_ini_path: str = 'alembic.ini'):
        """Initialize migration manager"""
        self.alembic_config = Config(alembic_ini_path)
    
    def create_migration(self, message: str) -> bool:
        """
        Create a new migration
        
        Args:
            message: Description of the migration (e.g., "add_stadium_capacity_to_teams")
        
        Returns:
            True if successful
        """
        try:
            logger.info(f"Creating migration: {message}")
            command.revision(self.alembic_config, autogenerate=True, message=message)
            logger.info(f"✓ Migration created successfully")
            return True
        except Exception as e:
            logger.error(f"✗ Error creating migration: {e}")
            return False
    
    def upgrade_database(self, revision: str = 'head') -> bool:
        """
        Upgrade database to a specific revision
        
        Args:
            revision: Target revision ('head' for latest, or specific revision ID)
        
        Returns:
            True if successful
        """
        try:
            logger.info(f"Upgrading database to {revision}...")
            command.upgrade(self.alembic_config, revision)
            logger.info(f"✓ Database upgraded successfully")
            return True
        except Exception as e:
            logger.error(f"✗ Error upgrading database: {e}")
            return False
    
    def downgrade_database(self, revision: str = '-1') -> bool:
        """
        Downgrade database to a specific revision
        
        Args:
            revision: Target revision ('-1' for previous, or specific revision ID)
        
        Returns:
            True if successful
        """
        try:
            logger.info(f"Downgrading database to {revision}...")
            command.downgrade(self.alembic_config, revision)
            logger.info(f"✓ Database downgraded successfully")
            return True
        except Exception as e:
            logger.error(f"✗ Error downgrading database: {e}")
            return False
    
    def show_current_revision(self) -> str:
        """Show current database revision"""
        try:
            logger.info("Fetching current revision...")
            # This would require custom implementation with alembic API
            logger.info("Run: alembic current")
            return None
        except Exception as e:
            logger.error(f"✗ Error: {e}")
            return None
    
    def show_history(self) -> bool:
        """Show migration history"""
        try:
            logger.info("Showing migration history...")
            command.history(self.alembic_config)
            return True
        except Exception as e:
            logger.error(f"✗ Error: {e}")
            return False

# Migration templates and documentation
MIGRATION_TEMPLATES = {
    'add_column': """
# Migration: Add column to table
# Usage: Add a new column to an existing table

def upgrade():
    op.add_column('table_name', sa.Column('new_column', sa.String(100)))

def downgrade():
    op.drop_column('table_name', 'new_column')
""",
    
    'drop_column': """
# Migration: Drop column from table
# Usage: Remove a column from a table

def upgrade():
    op.drop_column('table_name', 'old_column')

def downgrade():
    op.add_column('table_name', sa.Column('old_column', sa.String(100)))
""",
    
    'rename_column': """
# Migration: Rename column
# Usage: Rename a column in a table

def upgrade():
    op.alter_column('table_name', 'old_name', new_column_name='new_name')

def downgrade():
    op.alter_column('table_name', 'new_name', new_column_name='old_name')
""",
    
    'create_index': """
# Migration: Create index
# Usage: Add an index for faster queries

def upgrade():
    op.create_index('ix_column_name', 'table_name', ['column_name'])

def downgrade():
    op.drop_index('ix_column_name', table_name='table_name')
""",
    
    'add_constraint': """
# Migration: Add constraint
# Usage: Add a unique or foreign key constraint

def upgrade():
    op.create_unique_constraint('uq_constraint_name', 'table_name', ['column_name'])

def downgrade():
    op.drop_constraint('uq_constraint_name', 'table_name')
"""
}

if __name__ == '__main__':
    import sys
    
    manager = MigrationManager()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python db_migrations.py create <message>  - Create new migration")
        print("  python db_migrations.py upgrade           - Upgrade to latest")
        print("  python db_migrations.py downgrade         - Downgrade one step")
        print("  python db_migrations.py history           - Show migration history")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'create' and len(sys.argv) >= 3:
        message = ' '.join(sys.argv[2:])
        success = manager.create_migration(message)
        sys.exit(0 if success else 1)
    
    elif command == 'upgrade':
        success = manager.upgrade_database()
        sys.exit(0 if success else 1)
    
    elif command == 'downgrade':
        success = manager.downgrade_database()
        sys.exit(0 if success else 1)
    
    elif command == 'history':
        success = manager.show_history()
        sys.exit(0 if success else 1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
