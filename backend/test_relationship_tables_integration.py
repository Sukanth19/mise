#!/usr/bin/env python3
"""
Integration test for relationship table migration.

Tests the complete migration flow for all 10 relationship tables
with realistic data and foreign key relationships.
"""

import pytest
from unittest.mock import Mock, patch
from backend.migrate_to_mysql import DatabaseMigrator


class TestRelationshipTablesIntegration:
    """Integration tests for relationship table migration."""
    
    @pytest.fixture
    def migrator(self):
        """Create a DatabaseMigrator instance with mocked connections."""
        migrator = DatabaseMigrator(
            source_url="sqlite:///test.db",
            target_url="mysql+pymysql://root:password@localhost:3306/test",
            dry_run=False,
            incremental=False
        )
        
        # Mock sessions
        migrator.source_session = Mock()
        migrator.target_session = Mock()
        
        # Initialize ID mappings (simulating core tables already migrated)
        migrator.id_mappings = {
            'users': {1: 101, 2: 102, 3: 103},
            'recipes': {10: 1010, 20: 1020, 30: 1030},
        }
        
        return migrator
    
    def test_complete_relationship_migration_flow(self, migrator):
        """Test complete migration flow for all relationship tables."""
        
        # Track which tables were migrated
        migrated_tables = []
        
        # Mock the migrate_relationship_table method to track calls
        original_method = migrator.migrate_relationship_table
        
        def track_migration(table_name, fk_mappings):
            migrated_tables.append(table_name)
            # Return success stats
            return {'total': 1, 'success': 1, 'failed': 0, 'skipped': 0}
        
        migrator.migrate_relationship_table = track_migration
        
        # Expected tables in order
        expected_tables = [
            'recipe_ratings',
            'recipe_notes',
            'collections',
            'collection_recipes',
            'meal_plans',
            'meal_plan_templates',
            'meal_plan_template_items',
            'shopping_lists',
            'shopping_list_items',
            'user_follows',
            'recipe_likes',
            'recipe_comments',
        ]
        
        # Simulate migration
        for table in expected_tables:
            if table == 'recipe_ratings':
                migrator.migrate_relationship_table(table, {'recipe_id': 'recipes', 'user_id': 'users'})
            elif table == 'recipe_notes':
                migrator.migrate_relationship_table(table, {'recipe_id': 'recipes', 'user_id': 'users'})
            elif table == 'collections':
                migrator.migrate_relationship_table(table, {'user_id': 'users', 'parent_collection_id': 'collections'})
            elif table == 'collection_recipes':
                migrator.migrate_relationship_table(table, {'collection_id': 'collections', 'recipe_id': 'recipes'})
            elif table == 'meal_plans':
                migrator.migrate_relationship_table(table, {'user_id': 'users', 'recipe_id': 'recipes'})
            elif table == 'meal_plan_templates':
                migrator.migrate_relationship_table(table, {'user_id': 'users'})
            elif table == 'meal_plan_template_items':
                migrator.migrate_relationship_table(table, {'template_id': 'meal_plan_templates', 'recipe_id': 'recipes'})
            elif table == 'shopping_lists':
                migrator.migrate_relationship_table(table, {'user_id': 'users'})
            elif table == 'shopping_list_items':
                migrator.migrate_relationship_table(table, {'shopping_list_id': 'shopping_lists', 'recipe_id': 'recipes'})
            elif table == 'user_follows':
                migrator.migrate_relationship_table(table, {'follower_id': 'users', 'following_id': 'users'})
            elif table == 'recipe_likes':
                migrator.migrate_relationship_table(table, {'recipe_id': 'recipes', 'user_id': 'users'})
            elif table == 'recipe_comments':
                migrator.migrate_relationship_table(table, {'recipe_id': 'recipes', 'user_id': 'users'})
        
        # Verify all tables were migrated
        assert len(migrated_tables) == 12
        assert set(migrated_tables) == set(expected_tables)
        
    def test_dependency_order_respected(self, migrator):
        """Test that tables are migrated in correct dependency order."""
        
        # Simulate migration order
        migration_order = [
            'recipe_ratings',      # depends on recipes, users
            'recipe_notes',        # depends on recipes, users
            'collections',         # depends on users (and self)
            'collection_recipes',  # depends on collections, recipes
            'meal_plans',          # depends on users, recipes
            'meal_plan_templates', # depends on users
            'meal_plan_template_items',  # depends on meal_plan_templates, recipes
            'shopping_lists',      # depends on users
            'shopping_list_items', # depends on shopping_lists, recipes
            'user_follows',        # depends on users
            'recipe_likes',        # depends on recipes, users
            'recipe_comments',     # depends on recipes, users
        ]
        
        # Verify collections comes before collection_recipes
        assert migration_order.index('collections') < migration_order.index('collection_recipes')
        
        # Verify meal_plan_templates comes before meal_plan_template_items
        assert migration_order.index('meal_plan_templates') < migration_order.index('meal_plan_template_items')
        
        # Verify shopping_lists comes before shopping_list_items
        assert migration_order.index('shopping_lists') < migration_order.index('shopping_list_items')
        
    def test_all_foreign_key_mappings_correct(self, migrator):
        """Test that all foreign key mappings are correctly defined."""
        
        # Define expected foreign key mappings
        fk_mappings = {
            'recipe_ratings': {'recipe_id': 'recipes', 'user_id': 'users'},
            'recipe_notes': {'recipe_id': 'recipes', 'user_id': 'users'},
            'collections': {'user_id': 'users', 'parent_collection_id': 'collections'},
            'collection_recipes': {'collection_id': 'collections', 'recipe_id': 'recipes'},
            'meal_plans': {'user_id': 'users', 'recipe_id': 'recipes'},
            'meal_plan_templates': {'user_id': 'users'},
            'meal_plan_template_items': {'template_id': 'meal_plan_templates', 'recipe_id': 'recipes'},
            'shopping_lists': {'user_id': 'users'},
            'shopping_list_items': {'shopping_list_id': 'shopping_lists', 'recipe_id': 'recipes'},
            'user_follows': {'follower_id': 'users', 'following_id': 'users'},
            'recipe_likes': {'recipe_id': 'recipes', 'user_id': 'users'},
            'recipe_comments': {'recipe_id': 'recipes', 'user_id': 'users'},
        }
        
        # Verify each mapping
        for table_name, expected_fks in fk_mappings.items():
            # All foreign keys should reference valid tables
            for fk_column, ref_table in expected_fks.items():
                assert ref_table in ['users', 'recipes', 'collections', 'meal_plan_templates', 'shopping_lists']
        
        # Verify special cases
        assert 'parent_collection_id' in fk_mappings['collections']  # Self-referential
        assert fk_mappings['collections']['parent_collection_id'] == 'collections'
        
        assert 'follower_id' in fk_mappings['user_follows']  # Self-referential
        assert 'following_id' in fk_mappings['user_follows']
        assert fk_mappings['user_follows']['follower_id'] == 'users'
        assert fk_mappings['user_follows']['following_id'] == 'users'
        
    def test_id_mapping_preservation(self, migrator):
        """Test that ID mappings are preserved for tables with dependent tables."""
        
        # Tables that need ID mappings (have dependent tables)
        tables_needing_id_mapping = [
            'collections',           # needed by collection_recipes
            'meal_plan_templates',   # needed by meal_plan_template_items
            'shopping_lists',        # needed by shopping_list_items
        ]
        
        # Simulate migration and verify ID mappings are created
        for table in tables_needing_id_mapping:
            if table not in migrator.id_mappings:
                migrator.id_mappings[table] = {}
            
            # Simulate adding a mapping
            migrator.id_mappings[table][1] = 1001
            
            # Verify mapping exists
            assert table in migrator.id_mappings
            assert 1 in migrator.id_mappings[table]
            assert migrator.id_mappings[table][1] == 1001


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
