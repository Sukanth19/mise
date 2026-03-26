#!/usr/bin/env python3
"""
Reverse data migration script for Recipe Saver application.

Migrates data from MySQL (source) back to PostgreSQL/SQLite (target)
while preserving all relationships and constraints.

Usage:
    python migrate_from_mysql.py --source-url <mysql_url> --target-url <target_db_url>
    python migrate_from_mysql.py --source-url <mysql_url> --target-url <target_db_url> --dry-run
    python migrate_from_mysql.py --source-url <mysql_url> --target-url <target_db_url> --incremental
"""

import argparse
import logging
import sys
import time
from typing import Dict, Any, Optional, Tuple
from sqlalchemy import create_engine, inspect, MetaData, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('reverse_migration.log')
    ]
)
logger = logging.getLogger(__name__)


class ReverseDatabaseMigrator:
    """Handles reverse data migration from MySQL to PostgreSQL/SQLite using SQLAlchemy."""
    
    def __init__(
        self,
        source_url: str,
        target_url: str,
        dry_run: bool = False,
        incremental: bool = False
    ):
        """
        Initialize the reverse database migrator.
        
        Args:
            source_url: Source database connection string (MySQL)
            target_url: Target database connection string (PostgreSQL/SQLite)
            dry_run: If True, validate without writing to target
            incremental: If True, support resuming from previous migration
        """
        self.source_url = source_url
        self.target_url = target_url
        self.dry_run = dry_run
        self.incremental = incremental
        
        self.source_engine = None
        self.target_engine = None
        self.source_session = None
        self.target_session = None
        
        self.migration_stats: Dict[str, Dict[str, int]] = {}
        
        # ID mappings to preserve foreign key relationships
        # Maps source IDs to target IDs for each table
        self.id_mappings: Dict[str, Dict[int, int]] = {}
        
        # Track migration timing
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
        # Track errors for rollback decision
        self.errors: list = []
        
    def connect(self) -> None:
        """
        Establish connections to source and target databases.
        
        Raises:
            Exception: If connection to either database fails
        """
        try:
            logger.info(f"Connecting to source database (MySQL)...")
            self.source_engine = create_engine(
                self.source_url,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20
            )
            SourceSessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.source_engine
            )
            self.source_session = SourceSessionLocal()
            
            # Test source connection
            self.source_engine.connect()
            logger.info("✓ Successfully connected to source database (MySQL)")
            
        except Exception as e:
            logger.error(f"Failed to connect to source database at {self.source_url}: {e}")
            raise
        
        try:
            logger.info(f"Connecting to target database (PostgreSQL/SQLite)...")
            self.target_engine = create_engine(self.target_url)
            TargetSessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.target_engine
            )
            self.target_session = TargetSessionLocal()
            
            # Test target connection
            self.target_engine.connect()
            logger.info("✓ Successfully connected to target database")
            
        except Exception as e:
            logger.error(f"Failed to connect to target database at {self.target_url}: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close all database connections gracefully."""
        if self.source_session:
            self.source_session.close()
            logger.info("Closed source database session")
        
        if self.target_session:
            self.target_session.close()
            logger.info("Closed target database session")
        
        if self.source_engine:
            self.source_engine.dispose()
            logger.info("Disposed source database engine")
        
        if self.target_engine:
            self.target_engine.dispose()
            logger.info("Disposed target database engine")
    
    def validate_connections(self) -> bool:
        """
        Validate that both database connections are working.
        
        Returns:
            True if both connections are valid, False otherwise
        """
        try:
            # Validate source connection
            with self.source_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✓ Source database connection validated")
            
            # Validate target connection
            with self.target_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✓ Target database connection validated")
            
            return True
            
        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            return False
    
    def count_records(self, table_name: str, session: Session) -> int:
        """
        Count records in a table.
        
        Args:
            table_name: Name of the table
            session: Database session to use
            
        Returns:
            Number of records in the table
        """
        try:
            result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            return result.scalar()
        except Exception as e:
            logger.error(f"Failed to count records in {table_name}: {e}")
            return 0
    
    def verify_record_counts(self, table_name: str) -> Tuple[bool, int, int]:
        """
        Verify that record counts match between source and target.
        
        Args:
            table_name: Name of the table to verify
            
        Returns:
            Tuple of (match_success, source_count, target_count)
        """
        try:
            source_count = self.count_records(table_name, self.source_session)
            target_count = self.count_records(table_name, self.target_session)
            
            match = source_count == target_count
            
            if match:
                logger.info(f"✓ {table_name}: Record counts match ({source_count} records)")
            else:
                logger.error(
                    f"✗ {table_name}: Record count mismatch! "
                    f"Source: {source_count}, Target: {target_count}"
                )
                self.errors.append(f"{table_name}: Count mismatch (source={source_count}, target={target_count})")
            
            return match, source_count, target_count
            
        except Exception as e:
            logger.error(f"Failed to verify record counts for {table_name}: {e}")
            self.errors.append(f"{table_name}: Count verification failed - {e}")
            return False, 0, 0
    
    def rollback_migration(self) -> None:
        """
        Rollback the migration by clearing all data from target database.
        
        This is called when critical errors occur during migration.
        """
        if self.dry_run:
            logger.info("Dry-run mode: No rollback needed")
            return
        
        logger.warning("=" * 80)
        logger.warning("ROLLING BACK MIGRATION")
        logger.warning("=" * 80)
        
        try:
            # Get all tables in reverse order
            inspector = inspect(self.target_engine)
            table_names = inspector.get_table_names()
            
            # Disable foreign key checks temporarily (if PostgreSQL or SQLite)
            if 'postgresql' in self.target_url:
                for table_name in table_names:
                    self.target_session.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))
                    logger.info(f"Rolled back table: {table_name}")
            else:
                # SQLite doesn't support TRUNCATE, use DELETE
                self.target_session.execute(text("PRAGMA foreign_keys = OFF"))
                for table_name in table_names:
                    try:
                        self.target_session.execute(text(f"DELETE FROM {table_name}"))
                        logger.info(f"Rolled back table: {table_name}")
                    except Exception as e:
                        logger.error(f"Failed to rollback table {table_name}: {e}")
                self.target_session.execute(text("PRAGMA foreign_keys = ON"))
            
            self.target_session.commit()
            logger.warning("✓ Rollback completed - all data removed from target database")
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            self.target_session.rollback()
            raise
    
    def migrate_relationship_table(
        self,
        table_name: str,
        foreign_key_mappings: Dict[str, str]
    ) -> Dict[str, int]:
        """
        Generic migration for relationship tables.
        
        Args:
            table_name: Name of the table to migrate
            foreign_key_mappings: Dict mapping column names to their reference table names
                                 e.g., {'recipe_id': 'recipes', 'user_id': 'users'}
        
        Returns:
            Dictionary with migration statistics
        """
        stats = {'total': 0, 'success': 0, 'failed': 0, 'skipped': 0}
        
        logger.info(f"Starting migration for table: {table_name}")
        
        try:
            # Count total records
            count_result = self.source_session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            stats['total'] = count_result.scalar()
            
            if stats['total'] == 0:
                logger.info(f"Table {table_name}: No records to migrate")
                return stats
            
            logger.info(f"Table {table_name}: {stats['total']} records to migrate")
            
            # Fetch all records
            source_records = self.source_session.execute(text(f"SELECT * FROM {table_name}"))
            
            # Initialize ID mapping if this table needs it (has dependent tables)
            if table_name not in self.id_mappings:
                self.id_mappings[table_name] = {}
            
            for record in source_records:
                try:
                    record_dict = dict(record._mapping)
                    source_id = record_dict.get('id')
                    
                    if self.dry_run:
                        stats['success'] += 1
                        if source_id:
                            self.id_mappings[table_name][source_id] = source_id
                    else:
                        # Map foreign keys
                        insert_data = {k: v for k, v in record_dict.items() if k != 'id'}
                        
                        # Map all foreign keys
                        skip_record = False
                        for fk_column, ref_table in foreign_key_mappings.items():
                            if fk_column in insert_data and insert_data[fk_column] is not None:
                                source_fk_id = insert_data[fk_column]
                                if source_fk_id in self.id_mappings[ref_table]:
                                    insert_data[fk_column] = self.id_mappings[ref_table][source_fk_id]
                                else:
                                    logger.warning(
                                        f"{table_name} record (id={source_id}): "
                                        f"{fk_column} {source_fk_id} not found in {ref_table} mapping, skipping"
                                    )
                                    stats['skipped'] += 1
                                    skip_record = True
                                    break
                        
                        if skip_record:
                            continue
                        
                        columns = ', '.join(insert_data.keys())
                        placeholders = ', '.join([f":{key}" for key in insert_data.keys()])
                        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                        
                        result = self.target_session.execute(text(insert_query), insert_data)
                        self.target_session.flush()
                        
                        # Store new ID if this table has an ID column
                        if source_id:
                            new_id = result.lastrowid
                            self.id_mappings[table_name][source_id] = new_id
                        
                        stats['success'] += 1
                        
                except SQLAlchemyError as e:
                    stats['failed'] += 1
                    error_msg = f"Failed to migrate {table_name} record (id={record_dict.get('id')}): {e}"
                    logger.error(error_msg)
                    self.errors.append(f"{table_name}: {error_msg}")
                    continue
            
            if not self.dry_run:
                self.target_session.commit()
                logger.info(f"✓ Table {table_name}: Successfully migrated {stats['success']}/{stats['total']} records")
            else:
                logger.info(f"✓ Table {table_name}: Validated {stats['success']}/{stats['total']} records (dry-run)")
            
        except Exception as e:
            logger.error(f"Error migrating table {table_name}: {e}")
            if not self.dry_run:
                self.target_session.rollback()
            stats['failed'] = stats['total'] - stats['success']
        
        return stats
    
    def migrate_all(self) -> None:
        """
        Migrate all tables from MySQL to target database.
        
        Handles tables in dependency order to preserve foreign key relationships.
        """
        self.start_time = time.time()
        
        logger.info("=" * 80)
        logger.info("Starting reverse database migration (MySQL → PostgreSQL/SQLite)")
        logger.info(f"Source: {self.source_url}")
        logger.info(f"Target: {self.target_url}")
        logger.info(f"Dry-run: {self.dry_run}")
        logger.info(f"Incremental: {self.incremental}")
        logger.info("=" * 80)
        
        # Define migration order based on dependencies
        # Same order as forward migration to preserve relationships
        migration_order = [
            ('users', {'user_id': 'users'}),
            ('recipes', {'user_id': 'users', 'source_recipe_id': 'recipes', 'source_author_id': 'users'}),
            ('nutrition_facts', {'recipe_id': 'recipes'}),
            ('dietary_labels', {'recipe_id': 'recipes'}),
            ('allergen_warnings', {'recipe_id': 'recipes'}),
            ('recipe_ratings', {'recipe_id': 'recipes', 'user_id': 'users'}),
            ('recipe_notes', {'recipe_id': 'recipes', 'user_id': 'users'}),
            ('collections', {'user_id': 'users', 'parent_collection_id': 'collections'}),
            ('collection_recipes', {'collection_id': 'collections', 'recipe_id': 'recipes'}),
            ('meal_plans', {'user_id': 'users', 'recipe_id': 'recipes'}),
            ('meal_plan_templates', {'user_id': 'users'}),
            ('meal_plan_template_items', {'template_id': 'meal_plan_templates', 'recipe_id': 'recipes'}),
            ('shopping_lists', {'user_id': 'users'}),
            ('shopping_list_items', {'shopping_list_id': 'shopping_lists', 'recipe_id': 'recipes'}),
            ('user_follows', {'follower_id': 'users', 'following_id': 'users'}),
            ('recipe_likes', {'recipe_id': 'recipes', 'user_id': 'users'}),
            ('recipe_comments', {'recipe_id': 'recipes', 'user_id': 'users'}),
        ]
        
        # Migrate each table in order
        critical_error = False
        for table_name, fk_mappings in migration_order:
            try:
                logger.info(f"\n{'=' * 80}")
                stats = self.migrate_relationship_table(table_name, fk_mappings)
                self.migration_stats[table_name] = stats
                
                # Check for critical errors (>50% failure rate)
                if stats['total'] > 0:
                    failure_rate = (stats['failed'] + stats['skipped']) / stats['total']
                    if failure_rate > 0.5:
                        logger.error(
                            f"Critical error: {table_name} has {failure_rate*100:.1f}% failure rate"
                        )
                        self.errors.append(
                            f"{table_name}: High failure rate ({failure_rate*100:.1f}%)"
                        )
                        critical_error = True
                        break
                
            except Exception as e:
                logger.error(f"Failed to migrate table {table_name}: {e}")
                self.migration_stats[table_name] = {
                    'total': 0,
                    'success': 0,
                    'failed': 0,
                    'skipped': 0,
                    'error': str(e)
                }
                self.errors.append(f"{table_name}: Migration exception - {e}")
                critical_error = True
                break
        
        self.end_time = time.time()
        
        # If critical error occurred, offer rollback
        if critical_error and not self.dry_run:
            logger.error("=" * 80)
            logger.error("CRITICAL ERROR DETECTED")
            logger.error("=" * 80)
            logger.error("Migration encountered critical errors.")
            logger.error("Errors:")
            for error in self.errors:
                logger.error(f"  - {error}")
            
            # Automatic rollback on critical error
            logger.warning("Initiating automatic rollback...")
            try:
                self.rollback_migration()
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {rollback_error}")
        
        # Validate record counts if not dry-run and no critical errors
        if not self.dry_run and not critical_error:
            logger.info("\n" + "=" * 80)
            logger.info("Validating record counts...")
            logger.info("=" * 80)
            
            validation_passed = True
            for table_name, _ in migration_order:
                if table_name in self.migration_stats:
                    match, source_count, target_count = self.verify_record_counts(table_name)
                    if not match:
                        validation_passed = False
            
            if not validation_passed:
                logger.error("\n" + "=" * 80)
                logger.error("VALIDATION FAILED: Record counts do not match")
                logger.error("=" * 80)
                logger.warning("Consider running rollback or investigating discrepancies")
        
        # Print summary
        self.print_summary()
    
    def print_summary(self) -> None:
        """Print migration summary report with timing and validation."""
        logger.info("\n" + "=" * 80)
        logger.info("REVERSE MIGRATION SUMMARY REPORT")
        logger.info("=" * 80)
        
        # Calculate timing
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            logger.info(f"Total migration time: {duration:.2f} seconds ({duration/60:.2f} minutes)")
            logger.info("=" * 80)
        
        # Table-by-table summary
        total_records = 0
        total_success = 0
        total_failed = 0
        total_skipped = 0
        
        logger.info("\nTable Migration Results:")
        logger.info("-" * 80)
        
        for table_name, stats in self.migration_stats.items():
            total_records += stats.get('total', 0)
            total_success += stats.get('success', 0)
            total_failed += stats.get('failed', 0)
            total_skipped += stats.get('skipped', 0)
            
            status = "✓" if stats.get('failed', 0) == 0 and stats.get('skipped', 0) == 0 else "✗"
            logger.info(
                f"{status} {table_name:30s} | "
                f"Total: {stats.get('total', 0):6d} | "
                f"Success: {stats.get('success', 0):6d} | "
                f"Failed: {stats.get('failed', 0):6d} | "
                f"Skipped: {stats.get('skipped', 0):6d}"
            )
            
            if 'error' in stats:
                logger.error(f"  └─ Error: {stats['error']}")
        
        # Overall summary
        logger.info("=" * 80)
        logger.info("Overall Statistics:")
        logger.info(f"  Total records processed:    {total_records:,}")
        logger.info(f"  Successfully migrated:      {total_success:,}")
        logger.info(f"  Failed:                     {total_failed:,}")
        logger.info(f"  Skipped:                    {total_skipped:,}")
        
        if total_records > 0:
            success_rate = (total_success / total_records) * 100
            logger.info(f"  Success rate:               {success_rate:.2f}%")
        
        logger.info("=" * 80)
        
        # Error summary
        if self.errors:
            logger.error("\nErrors Encountered:")
            logger.error("-" * 80)
            for i, error in enumerate(self.errors, 1):
                logger.error(f"{i}. {error}")
            logger.error("=" * 80)
        
        # Final status
        if self.dry_run:
            logger.info("\n✓ DRY-RUN MODE: Validation completed, no data was written to target database")
        elif total_failed > 0 or total_skipped > 0:
            logger.warning("\n⚠ Migration completed with errors. Check reverse_migration.log for details.")
            logger.warning("Some data may not have been migrated correctly.")
        else:
            logger.info("\n✓ Reverse migration completed successfully! All records migrated.")
        
        logger.info("=" * 80)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Reverse migrate data from MySQL to PostgreSQL/SQLite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Migrate from MySQL to SQLite
  python migrate_from_mysql.py \\
    --source-url mysql+pymysql://root:password@localhost:3306/recipe_saver \\
    --target-url sqlite:///recipe_saver.db

  # Dry-run mode (validate without writing)
  python migrate_from_mysql.py \\
    --source-url mysql+pymysql://root:password@localhost:3306/recipe_saver \\
    --target-url sqlite:///recipe_saver.db \\
    --dry-run

  # Migrate from MySQL to PostgreSQL
  python migrate_from_mysql.py \\
    --source-url mysql+pymysql://root:password@localhost:3306/recipe_saver \\
    --target-url postgresql://user:pass@localhost:5432/recipe_saver \\
    --incremental
        """
    )
    
    parser.add_argument(
        '--source-url',
        required=True,
        help='Source MySQL database connection string (e.g., mysql+pymysql://user:pass@host:port/db)'
    )
    
    parser.add_argument(
        '--target-url',
        required=True,
        help='Target database connection string (e.g., sqlite:///recipe_saver.db or postgresql://user:pass@host:port/db)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate migration without writing to target database'
    )
    
    parser.add_argument(
        '--incremental',
        action='store_true',
        help='Support incremental migration (resume from previous run)'
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for reverse migration script.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    args = parse_arguments()
    
    # Validate source URL is MySQL
    if not args.source_url.startswith('mysql'):
        logger.error("Source URL must be a MySQL connection string (mysql+pymysql://...)")
        return 1
    
    migrator = ReverseDatabaseMigrator(
        source_url=args.source_url,
        target_url=args.target_url,
        dry_run=args.dry_run,
        incremental=args.incremental
    )
    
    try:
        # Connect to databases
        migrator.connect()
        
        # Validate connections
        if not migrator.validate_connections():
            logger.error("Connection validation failed")
            return 1
        
        # Run migration
        migrator.migrate_all()
        
        # Check if migration was successful
        total_failed = sum(
            stats.get('failed', 0)
            for stats in migrator.migration_stats.values()
        )
        
        return 0 if total_failed == 0 else 1
        
    except Exception as e:
        logger.error(f"Reverse migration failed: {e}", exc_info=True)
        return 1
        
    finally:
        # Always disconnect
        migrator.disconnect()


if __name__ == '__main__':
    sys.exit(main())
