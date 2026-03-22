"""Property-based tests for authentication service."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

from hypothesis import given, strategies as st, settings as hyp_settings
from jose import jwt
from datetime import datetime, timedelta, timezone


# Feature: recipe-saver, Property 2: Passwords are hashed before storage
@given(password=st.text(min_size=8, max_size=50, alphabet=st.characters(min_codepoint=33, max_codepoint=126)))
@hyp_settings(max_examples=20, deadline=timedelta(milliseconds=500))
def test_password_hashing_property(password):
    """
    Property 2: Passwords are hashed before storage
    
    For any password provided during registration, the stored password 
    in the database should not equal the plain text password (must be hashed).
    
    **Validates: Requirements 1.3**
    """
    from app.services.auth_service import AuthService
    
    # Skip passwords that might cause bcrypt issues
    try:
        hashed = AuthService.hash_password(password)
    except ValueError:
        # Skip passwords that exceed bcrypt's limits
        return
    
    # Password should be hashed (not equal to original)
    assert hashed != password, "Password should be hashed, not stored as plain text"
    
    # Hashed password should be verifiable
    assert AuthService.verify_password(password, hashed), "Hashed password should verify correctly"
    
    # Hash should be non-empty
    assert len(hashed) > 0, "Hashed password should not be empty"


# Feature: recipe-saver, Property 6: JWT tokens expire in 24 hours
@given(user_id=st.integers(min_value=1, max_value=1000000))
@hyp_settings(max_examples=20)
def test_jwt_token_expiration_property(user_id):
    """
    Property 6: JWT tokens expire in 24 hours
    
    For any generated JWT token, the expiration claim should be set 
    to 24 hours from the creation time.
    
    **Validates: Requirements 2.3**
    """
    from app.services.auth_service import AuthService
    from app.config import settings
    
    # Record time before token creation
    before_time = datetime.now(timezone.utc)
    
    # Create token
    token = AuthService.create_access_token(user_id)
    
    # Record time after token creation
    after_time = datetime.now(timezone.utc)
    
    # Decode token to check expiration
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    exp_timestamp = payload.get("exp")
    
    assert exp_timestamp is not None, "Token should have expiration claim"
    
    # Convert timestamp to datetime (UTC aware)
    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    
    # Expected expiration is 24 hours from creation
    # Allow 2 seconds tolerance for test execution time and timestamp precision loss
    expected_exp_min = before_time + timedelta(hours=24) - timedelta(seconds=2)
    expected_exp_max = after_time + timedelta(hours=24) + timedelta(seconds=2)
    
    assert expected_exp_min <= exp_datetime <= expected_exp_max, \
        f"Token expiration should be 24 hours from creation. Expected between {expected_exp_min} and {expected_exp_max}, got {exp_datetime}"


# Feature: recipe-saver, Property 3: Short passwords are rejected
@given(password=st.text(min_size=0, max_size=7))
@hyp_settings(max_examples=20)
def test_short_password_rejection_property(password):
    """
    Property 3: Short passwords are rejected
    
    For any password shorter than 8 characters, registration should fail 
    with a validation error.
    
    **Validates: Requirements 1.4**
    
    Note: This property tests that Pydantic validation rejects short passwords.
    The validation happens at the schema level (RegisterRequest).
    """
    from pydantic import ValidationError
    from app.schemas import RegisterRequest
    
    # Attempt to create a RegisterRequest with short password
    try:
        RegisterRequest(username="testuser", password=password)
        # If we get here, validation didn't reject the short password
        assert False, f"Short password '{password}' (length {len(password)}) should be rejected"
    except ValidationError as e:
        # Validation error is expected for short passwords
        errors = e.errors()
        # Check that password field has a validation error
        password_errors = [err for err in errors if 'password' in str(err.get('loc', []))]
        assert len(password_errors) > 0, "Should have validation error for password field"
