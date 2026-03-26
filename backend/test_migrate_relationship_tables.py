#!/usr/bin/env python3
"""
Test suite for relationship table migration.

Tests the migrate_relationship_table() method with all 10 relationship tables
to ensure proper foreign key mapping and data preservation.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from sqlalchemy.exc import SQLAlchemyError
from backend.migrate_to_mysql import DatabaseMigrator


class TestRelationshipTableMigration:
    """Test suite for relationship table migration."""
    
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
        
        # Initialize ID mappings
        migrator.id_mappings = {
            'users': {1: 101, 2: 102, 3: 103},
            'recipes': {10: 1010, 20: 1020, 30: 1030},
            'collections': {5: 505, 6: 606},
            'meal_plan_templates': {7: 707},
            'shopping_lists': {8: 808}
        }
        
        return migrator
    
    def test_recipe_ratings_migration(self, migrator):
        """Test migration of recipe_ratings table."""
        # Mock source data
        mock_records = [
            Mock(_mapping={'id': 1, 'recipe_id': 10, 'user_id': 1, 'rating': 5, 'created_at': '2024-01-01', 'updated_at': '2024-01-01'}),
            Mock(_mapping={'id': 2, 'recipe_id': 20, 'user_id': 2, 'rating': 4, 'created_at': '2024-01-02', 'updated_at': '2024-01-02'}),
        ]
        
        # Mock count query
        count_result = Mock()
        count_result.scalar.return_value = 2
        migrator.source_session.execute.side_effect = [count_result, mock_records]
        
        # Mock insert result
        insert_result = Mock()
        insert_result.lastrowid = 9001
        migrator.target_session.execute.return_value = insert_result
        
        # Execute migration
        stats = migrator.migrate_relationship_table(
            'recipe_ratings',
            {'recipe_id': 'recipes', 'user_id': 'users'}
        )
        
        # Verify stats
        assert stats['total'] == 2
        assert stats['success'] == 2
        assert stats['failed'] == 0
        assert stats['skipped'] == 0
        
        # Verify foreign keys were mapped
        assert migrator.target_session.execute.call_count == 2
        
    def test_recipe_notes_migration(self, migrator):
        """Test migration of recipe_notes table."""
        mock_records = [
            Mock(_mapping={'id': 1, 'recipe_id': 10, 'user_id': 1, 'note_text': 'Great recipe!', 'created_at': '2024-01-01', 'updated_at': '2024-01-01'}),
        ]
        
        count_result = Mock()
        count_result.scalar.return_value = 1
        migrator.source_session.execute.side_effect = [count_result, mock_records]
        
        insert_result = Mock()
        insert_result.lastrowid = 9002
        migrator.target_session.execute.return_value = insert_result
        
        stats = migrator.migrate_relationship_table(
            'recipe_notes',
            {'recipe_id': 'recipes', 'user_id': 'users'}
        )
        
        assert stats['total'] == 1
        assert stats['success'] == 1
        
    def test_collections_self_referential_fk(self, migrator):
        """Test migration of collections table with self-referential foreign key."""
        mock_records = [
            Mock(_mapping={'id': 5, 'user_id': 1, 'name': 'Parent Collection', 'parent_collection_id': None, 'nesting_level': 0}),
            Mock(_mapping={'id': 6, 'user_id': 1, 'name': 'Child Collection', 'parent_collection_id': 5, 'nesting_level': 1}),
        ]
        
        count_result = Mock()
        count_result.scalar.return_value = 2
        migrator.source_session.execute.side_effect = [count_result, mock_records]
        
        insert_result = Mock()
        insert_result.lastrowid = 9003
        migrator.target_session.execute.return_value = insert_result
        
        stats = migrator.migrate_relationship_table(
            'collections',
            {'user_id': 'users', 'parent_collection_id': 'collections'}
        )
        
        assert stats['total'] == 2
        assert stats['success'] == 2
        
    def test_collection_recipes_join_table(self, migrator):
        """Test migration of collection_recipes join table."""
        mock_records = [
            Mock(_mapping={'id': 1, 'collection_id': 5, 'recipe_id': 10, 'added_at': '2024-01-01'}),
            Mock(_mapping={'id': 2, 'collection_id': 5, 'recipe_id': 20, 'added_at': '2024-01-02'}),
        ]
        
        count_result = Mock()
        count_result.scalar.return_value = 2
        migrator.source_session.execute.side_effect = [count_result, mock_records]
        
        insert_result = Mock()
        insert_result.lastrowid = 9004
        migrator.target_session.execute.return_value = insert_result
        
        stats = migrator.migrate_relationship_table(
            'collection_recipes',
            {'collection_id': 'collections', 'recipe_id': 'recipes'}
        )
        
        assert stats['total'] == 2
        assert stats['success'] == 2
        
    def test_meal_plans_migration(self, migrator):
        """Test migration of meal_plans table."""
        mock_records = [
            Mock(_mapping={'id': 1, 'user_id': 1, 'recipe_id': 10, 'meal_date': '2024-01-15', 'meal_time': 'dinner', 'created_at': '2024-01-01'}),
        ]
        
        count_result = Mock()
        count_result.scalar.return_value = 1
        migrator.source_session.execute.side_effect = [count_result, mock_records]
        
        insert_result = Mock()
        insert_result.lastrowid = 9005
        migrator.target_session.execute.return_value = insert_result
        
        stats = migrator.migrate_relationship_table(
            'meal_plans',
            {'user_id': 'users', 'recipe_id': 'recipes'}
        )
        
        assert stats['total'] == 1
        assert stats['success'] == 1
        
    def test_shopping_list_items_optional_fk(self, migrator):
        """Test migration of shopping_list_items with optional recipe_id."""
        mock_records = [
            Mock(_mapping={'id': 1, 'shopping_list_id': 8, 'ingredient_name': 'Milk', 'recipe_id': 10, 'is_custom': False}),
            Mock(_mapping={'id': 2, 'shopping_list_id': 8, 'ingredient_name': 'Eggs', 'recipe_id': None, 'is_custom': True}),
        ]
        
        count_result = Mock()
        count_result.scalar.return_value = 2
        migrator.source_session.execute.side_effect = [count_result, mock_records]
        
        insert_result = Mock()
        insert_result.lastrowid = 9006
        migrator.target_session.execute.return_value = insert_result
        
        stats = migrator.migrate_relationship_table(
            'shopping_list_items',
            {'shopping_list_id': 'shopping_lists', 'recipe_id': 'recipes'}
        )
        
        assert stats['total'] == 2
        assert stats['success'] == 2
        
    def test_user_follows_self_referential(self, migrator):
        """Test migration of user_follows with self-referential foreign keys."""
        mock_records = [
            Mock(_mapping={'id': 1, 'follower_id': 1, 'following_id': 2, 'created_at': '2024-01-01'}),
            Mock(_mapping={'id': 2, 'follower_id': 2, 'following_id': 3, 'created_at': '2024-01-02'}),
        ]
        
        count_result = Mock()
        count_result.scalar.return_value = 2
        migrator.source_session.execute.side_effect = [count_result, mock_records]
        
        insert_result = Mock()
        insert_result.lastrowid = 9007
        migrator.target_session.execute.return_value = insert_result
        
        stats = migrator.migrate_relationship_table(
            'user_follows',
            {'follower_id': 'users', 'following_id': 'users'}
        )
        
        assert stats['total'] == 2
        assert stats['success'] == 2
        
    def test_recipe_likes_migration(self, migrator):
        """Test migration of recipe_likes table."""
        mock_records = [
            Mock(_mapping={'id': 1, 'recipe_id': 10, 'user_id': 2, 'created_at': '2024-01-01'}),
        ]
        
        count_result = Mock()
        count_result.scalar.return_value = 1
        migrator.source_session.execute.side_effect = [count_result, mock_records]
        
        insert_result = Mock()
        insert_result.lastrowid = 9008
        migrator.target_session.execute.return_value = insert_result
        
        stats = migrator.migrate_relationship_table(
            'recipe_likes',
            {'recipe_id': 'recipes', 'user_id': 'users'}
        )
        
        assert stats['total'] == 1
        assert stats['success'] == 1
        
    def test_recipe_comments_migration(self, migrator):
        """Test migration of recipe_comments table."""
        mock_records = [
            Mock(_mapping={'id': 1, 'recipe_id': 10, 'user_id': 2, 'comment_text': 'Delicious!', 'created_at': '2024-01-01', 'updated_at': '2024-01-01'}),
        ]
        
        count_result = Mock()
        count_result.scalar.return_value = 1
        migrator.source_session.execute.side_effect = [count_result, mock_records]
        
        insert_result = Mock()
        insert_result.lastrowid = 9009
        migrator.target_session.execute.return_value = insert_result
        
        stats = migrator.migrate_relationship_table(
            'recipe_comments',
            {'recipe_id': 'recipes', 'user_id': 'users'}
        )
        
        assert stats['total'] == 1
        assert stats['success'] == 1
        
    def test_missing_foreign_key_reference(self, migrator):
        """Test that records with missing foreign key references are skipped."""
        mock_records = [
            Mock(_mapping={'id': 1, 'recipe_id': 999, 'user_id': 1, 'rating': 5}),  # recipe_id 999 doesn't exist
        ]
        
        count_result = Mock()
        count_result.scalar.return_value = 1
        migrator.source_session.execute.side_effect = [count_result, mock_records]
        
        stats = migrator.migrate_relationship_table(
            'recipe_ratings',
            {'recipe_id': 'recipes', 'user_id': 'users'}
        )
        
        assert stats['total'] == 1
        assert stats['success'] == 0
        assert stats['skipped'] == 1
        
    def test_empty_table(self, migrator):
        """Test migration of an empty table."""
        count_result = Mock()
        count_result.scalar.return_value = 0
        migrator.source_session.execute.return_value = count_result
        
        stats = migrator.migrate_relationship_table(
            'recipe_ratings',
            {'recipe_id': 'recipes', 'user_id': 'users'}
        )
        
        assert stats['total'] == 0
        assert stats['success'] == 0
        
    def test_dry_run_mode(self, migrator):
        """Test that dry-run mode doesn't write to target database."""
        migrator.dry_run = True
        
        mock_records = [
            Mock(_mapping={'id': 1, 'recipe_id': 10, 'user_id': 1, 'rating': 5}),
        ]
        
        count_result = Mock()
        count_result.scalar.return_value = 1
        migrator.source_session.execute.side_effect = [count_result, mock_records]
        
        stats = migrator.migrate_relationship_table(
            'recipe_ratings',
            {'recipe_id': 'recipes', 'user_id': 'users'}
        )
        
        assert stats['total'] == 1
        assert stats['success'] == 1
        # Verify no writes to target
        migrator.target_session.execute.assert_not_called()
        migrator.target_session.commit.assert_not_called()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
