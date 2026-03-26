"""
Unit tests for application startup, shutdown, and health check endpoints.

Validates Requirements 1.4, 1.5
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


class TestStartupShutdown:
    """Test application startup and shutdown lifecycle events."""
    
    def test_startup_event_success(self):
        """
        Test that startup event successfully connects to database.
        
        Validates: Requirement 1.4
        """
        with patch('app.main.health_check') as mock_health_check:
            mock_health_check.return_value = True
            
            # Create a new test client which triggers startup event
            with TestClient(app) as client:
                # If we get here without exception, startup succeeded
                response = client.get("/")
                assert response.status_code == 200
    
    def test_startup_event_failure(self):
        """
        Test that startup event raises error when database connection fails.
        
        Validates: Requirement 1.4
        """
        with patch('app.main.health_check') as mock_health_check:
            mock_health_check.return_value = False
            
            # Startup should raise RuntimeError
            with pytest.raises(RuntimeError, match="Failed to connect to database"):
                with TestClient(app):
                    pass
    
    def test_shutdown_event_closes_connections(self):
        """
        Test that shutdown event closes database connections gracefully.
        
        Validates: Requirement 1.5
        """
        with patch('app.main.engine') as mock_engine:
            mock_engine.dispose = MagicMock()
            
            # Create and close client to trigger shutdown
            with TestClient(app):
                pass
            
            # Verify engine.dispose() was called
            mock_engine.dispose.assert_called_once()


class TestHealthCheckEndpoint:
    """Test health check endpoint for database connectivity."""
    
    def test_health_check_endpoint_healthy(self, client):
        """
        Test health check endpoint returns healthy status when database is connected.
        
        Validates: Requirement 1.4
        """
        with patch('app.main.health_check') as mock_health_check:
            mock_health_check.return_value = True
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"] == "connected"
    
    def test_health_check_endpoint_unhealthy(self, client):
        """
        Test health check endpoint returns unhealthy status when database is disconnected.
        
        Validates: Requirement 1.4
        """
        with patch('app.main.health_check') as mock_health_check:
            mock_health_check.return_value = False
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["database"] == "disconnected"
