"""
Tests for authentication functionality.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from src.api.main import app
from src.api.auth.utils import create_access_token

client = TestClient(app)

def test_create_user():
    """Test user creation endpoint."""
    response = client.post(
        "/auth/users",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "password" not in data

def test_login():
    """Test login endpoint."""
    # First create a user
    client.post(
        "/auth/users",
        json={
            "email": "login@example.com",
            "username": "logintest",
            "password": "testpass123"
        }
    )
    
    # Try to login
    response = client.post(
        "/auth/token",
        data={
            "username": "logintest",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_invalid_login():
    """Test login with invalid credentials."""
    response = client.post(
        "/auth/token",
        data={
            "username": "nonexistent",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401

def test_get_current_user():
    """Test getting current user info."""
    # Create user
    client.post(
        "/auth/users",
        json={
            "email": "current@example.com",
            "username": "currentuser",
            "password": "testpass123"
        }
    )
    
    # Login
    response = client.post(
        "/auth/token",
        data={
            "username": "currentuser",
            "password": "testpass123"
        }
    )
    token = response.json()["access_token"]
    
    # Get user info
    response = client.get(
        "/auth/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "currentuser"
    assert data["email"] == "current@example.com"

def test_update_user():
    """Test updating user information."""
    # Create and login user
    client.post(
        "/auth/users",
        json={
            "email": "update@example.com",
            "username": "updateuser",
            "password": "testpass123"
        }
    )
    response = client.post(
        "/auth/token",
        data={
            "username": "updateuser",
            "password": "testpass123"
        }
    )
    token = response.json()["access_token"]
    
    # Update user info
    response = client.put(
        "/auth/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "updated@example.com",
            "password": "newpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "updated@example.com"

    # Verify can login with new password
    response = client.post(
        "/auth/token",
        data={
            "username": "updateuser",
            "password": "newpass123"
        }
    )
    assert response.status_code == 200

def test_protected_route():
    """Test accessing protected route."""
    response = client.get("/api/deals")
    assert response.status_code == 401
    
    # Create and login user
    client.post(
        "/auth/users",
        json={
            "email": "protected@example.com",
            "username": "protecteduser",
            "password": "testpass123"
        }
    )
    response = client.post(
        "/auth/token",
        data={
            "username": "protecteduser",
            "password": "testpass123"
        }
    )
    token = response.json()["access_token"]
    
    # Access protected route with token
    response = client.get(
        "/api/deals",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200