# Integration Test Guide

## Prerequisites
1. Backend server running on http://localhost:8000
2. PostgreSQL database running and configured
3. Frontend dependencies installed

## Manual Testing Steps

### Test Registration Flow
1. Start the frontend dev server: `npm run dev`
2. Navigate to http://localhost:3000/register
3. Enter a username and password (8+ characters)
4. Click "Register"
5. Should redirect to /dashboard with token stored

### Test Login Flow
1. Navigate to http://localhost:3000
2. Enter registered username and password
3. Click "Log In"
4. Should redirect to /dashboard with token stored

### Test Validation
1. Try registering with password < 8 characters
2. Try logging in with wrong credentials
3. Try submitting empty forms
4. Verify error messages display correctly

### Test Token Storage
1. Open browser DevTools > Application > Local Storage
2. After login, verify `auth_token` is stored
3. Refresh the page - token should persist

### Test 401 Handling
1. Log in successfully
2. Manually delete the token from localStorage
3. Try to access an authenticated endpoint
4. Should redirect to login page
