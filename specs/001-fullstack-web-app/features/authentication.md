# Feature Specification: User Authentication

**Feature Branch**: `001-fullstack-web-app`
**Created**: 2026-01-14
**Status**: Active Development

## Overview

This specification defines the complete user authentication system for the Todo application, including user registration (signup), user login (signin), session management, and JWT token handling using Better Auth library.

## User Stories

### US-AUTH-1: User Registration (Priority: P1)

**As a** new visitor
**I want to** create an account with my email and password
**So that** I can start managing my personal tasks

**Acceptance Criteria**:

1. **Given** I am a new user on the signup page
   **When** I enter a valid email address and password and click "Sign Up"
   **Then** my account is created and I am automatically signed in and redirected to the task dashboard

2. **Given** I am on the signup page
   **When** I enter an email that is already registered
   **Then** I see an error message "This email is already registered. Please sign in instead."

3. **Given** I am on the signup page
   **When** I enter an invalid email format (e.g., "notanemail")
   **Then** I see an error message "Please enter a valid email address"

4. **Given** I am on the signup page
   **When** I enter a password shorter than 8 characters
   **Then** I see an error message "Password must be at least 8 characters"

5. **Given** I am on the signup page
   **When** I submit the form with empty email or password
   **Then** I see error messages indicating which fields are required

6. **Given** I successfully create an account
   **When** my account is created
   **Then** my password is hashed before being stored in the database

7. **Given** I successfully create an account
   **When** the registration completes
   **Then** I receive a JWT token that is stored in my browser

8. **Given** I successfully create an account
   **When** I am redirected to the task dashboard
   **Then** I can immediately start creating tasks without additional signin

---

### US-AUTH-2: User Sign In (Priority: P1)

**As a** registered user
**I want to** sign in with my email and password
**So that** I can access my tasks

**Acceptance Criteria**:

1. **Given** I am a registered user on the signin page
   **When** I enter my correct email and password and click "Sign In"
   **Then** I am authenticated and redirected to the task dashboard

2. **Given** I am on the signin page
   **When** I enter an incorrect password
   **Then** I see an error message "Invalid email or password"

3. **Given** I am on the signin page
   **When** I enter an email that doesn't exist
   **Then** I see an error message "Invalid email or password" (same message to prevent email enumeration)

4. **Given** I am on the signin page
   **When** I submit the form with empty email or password
   **Then** I see error messages indicating which fields are required

5. **Given** I successfully sign in
   **When** the authentication completes
   **Then** I receive a JWT token that is stored in my browser

6. **Given** I successfully sign in
   **When** I am redirected to the task dashboard
   **Then** I see my existing tasks loaded

7. **Given** I am on the signin page
   **When** I enter an invalid email format
   **Then** I see an error message "Please enter a valid email address"

---

### US-AUTH-3: Session Management (Priority: P1)

**As a** signed-in user
**I want to** remain authenticated across page refreshes
**So that** I don't have to sign in repeatedly

**Acceptance Criteria**:

1. **Given** I am signed in
   **When** I refresh the page
   **Then** I remain signed in and see my tasks

2. **Given** I am signed in
   **When** I close the browser and reopen it within 7 days
   **Then** I remain signed in (token not expired)

3. **Given** I am signed in
   **When** 7 days pass without activity
   **Then** my token expires and I must sign in again

4. **Given** I am signed in
   **When** I navigate between different pages in the app
   **Then** I remain authenticated without re-entering credentials

5. **Given** I am signed in
   **When** I make API requests
   **Then** my JWT token is automatically included in the Authorization header

---

### US-AUTH-4: Sign Out (Priority: P1)

**As a** signed-in user
**I want to** sign out of my account
**So that** others cannot access my tasks on a shared device

**Acceptance Criteria**:

1. **Given** I am signed in
   **When** I click the "Sign Out" button
   **Then** my session is terminated and I am redirected to the signin page

2. **Given** I have signed out
   **When** I try to access the task dashboard
   **Then** I am redirected to the signin page

3. **Given** I have signed out
   **When** I click the browser back button
   **Then** I cannot access protected pages and am redirected to signin

4. **Given** I sign out
   **When** the signout completes
   **Then** my JWT token is removed from browser storage

5. **Given** I sign out
   **When** I attempt to make API requests with the old token
   **Then** the requests are rejected with 401 Unauthorized

---

### US-AUTH-5: Protected Routes (Priority: P1)

**As a** system
**I want to** protect task-related pages from unauthenticated access
**So that** only signed-in users can manage tasks

**Acceptance Criteria**:

1. **Given** I am not signed in
   **When** I attempt to access the task dashboard URL directly
   **Then** I am redirected to the signin page

2. **Given** I am not signed in
   **When** I attempt to make API requests without a token
   **Then** I receive a 401 Unauthorized response

3. **Given** I am signed in
   **When** I access protected pages
   **Then** I can view and interact with them normally

4. **Given** my token has expired
   **When** I attempt to access protected pages
   **Then** I am redirected to the signin page with a message "Session expired. Please sign in again."

5. **Given** I have an invalid token
   **When** I attempt to make API requests
   **Then** I receive a 401 Unauthorized response

---

## JWT Token Specification

### Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "iat": 1704067200,
    "exp": 1704672000
  },
  "signature": "HMACSHA256(...)"
}
```

### Token Fields

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| user_id | UUID | Unique identifier for the user | Yes |
| email | String | User's email address | Yes |
| iat | Integer | Issued At timestamp (Unix epoch) | Yes |
| exp | Integer | Expiration timestamp (Unix epoch) | Yes |

### Token Properties

- **Algorithm**: HS256 (HMAC with SHA-256)
- **Expiration**: 7 days from issuance (604800 seconds)
- **Signing Secret**: `BETTER_AUTH_SECRET` environment variable
- **Storage**: Browser localStorage or sessionStorage (managed by Better Auth)
- **Transmission**: Authorization header: `Bearer <token>`

### Token Lifecycle

1. **Issuance**:
   - Generated by backend upon successful signup or signin
   - Signed with `BETTER_AUTH_SECRET`
   - Returned in response body: `{ token: "...", user: {...} }`

2. **Storage**:
   - Frontend stores token in browser storage
   - Better Auth library manages storage automatically
   - Token persists across page refreshes

3. **Usage**:
   - Included in every API request to protected endpoints
   - Format: `Authorization: Bearer <token>`
   - Better Auth client automatically attaches token

4. **Validation**:
   - Backend middleware extracts token from Authorization header
   - Verifies signature using `BETTER_AUTH_SECRET`
   - Checks expiration time
   - Extracts user_id from payload

5. **Expiration**:
   - Token expires 7 days after issuance
   - Expired tokens rejected with 401 Unauthorized
   - User must sign in again to obtain new token

6. **Revocation**:
   - Token removed from browser storage on signout
   - No server-side token blacklist (stateless authentication)
   - Old tokens remain valid until expiration

---

## Better Auth Integration

### Frontend Responsibilities

The Next.js frontend uses Better Auth client library for:

1. **Authentication UI**:
   - Render signup and signin forms
   - Handle form validation
   - Display error messages
   - Manage loading states

2. **Token Management**:
   - Store JWT token securely
   - Retrieve token for API requests
   - Remove token on signout
   - Handle token expiration

3. **API Client Configuration**:
   - Automatically attach token to requests
   - Intercept 401 responses
   - Redirect to signin on authentication failure

4. **Route Protection**:
   - Implement middleware to check authentication
   - Redirect unauthenticated users to signin
   - Allow access to protected routes for authenticated users

### Backend Responsibilities

The FastAPI backend uses Better Auth server library for:

1. **User Registration**:
   - Validate email format and uniqueness
   - Validate password strength
   - Hash password using bcrypt
   - Create user record in database
   - Generate JWT token
   - Return token and user data

2. **User Authentication**:
   - Validate email and password
   - Retrieve user from database
   - Verify password hash
   - Generate JWT token
   - Return token and user data

3. **Token Verification**:
   - Extract token from Authorization header
   - Verify token signature
   - Check token expiration
   - Extract user_id from payload
   - Attach user_id to request context

4. **Authorization**:
   - Verify user_id from token matches URL parameter
   - Enforce ownership rules on all operations
   - Return 403 Forbidden for unauthorized access

---

## Password Security

### Hashing Requirements

- **Algorithm**: bcrypt (industry standard)
- **Work Factor**: 12 rounds (configurable)
- **Salt**: Automatically generated per password
- **Storage**: Only hashed password stored, never plaintext

### Password Validation Rules

1. **Minimum Length**: 8 characters
2. **Maximum Length**: 128 characters (reasonable upper bound)
3. **Allowed Characters**: Any printable characters
4. **No Complexity Requirements**: No forced special characters (Phase II simplification)

### Password Comparison

```python
# Signup: Hash password
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Signin: Verify password
is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash)
```

---

## Email Validation

### Email Format Rules

1. **Format**: Standard email format (RFC 5322)
2. **Case Sensitivity**: Case-insensitive (normalized to lowercase)
3. **Uniqueness**: Each email can only be registered once
4. **Verification**: No email verification in Phase II (out of scope)

### Email Normalization

```python
# Normalize email before storage and comparison
normalized_email = email.strip().lower()
```

### Email Validation Examples

| Email | Valid | Reason |
|-------|-------|--------|
| user@example.com | ✅ | Standard format |
| User@Example.COM | ✅ | Normalized to lowercase |
| user+tag@example.com | ✅ | Plus addressing allowed |
| user@subdomain.example.com | ✅ | Subdomain allowed |
| notanemail | ❌ | Missing @ symbol |
| @example.com | ❌ | Missing local part |
| user@ | ❌ | Missing domain |
| user @example.com | ❌ | Space not allowed |

---

## Error Handling

### Authentication Errors

#### 400 Bad Request - Validation Errors

1. **Empty Email**:
   ```json
   {
     "error": "Email is required",
     "field": "email"
   }
   ```

2. **Invalid Email Format**:
   ```json
   {
     "error": "Please enter a valid email address",
     "field": "email"
   }
   ```

3. **Empty Password**:
   ```json
   {
     "error": "Password is required",
     "field": "password"
   }
   ```

4. **Password Too Short**:
   ```json
   {
     "error": "Password must be at least 8 characters",
     "field": "password"
   }
   ```

5. **Email Already Registered** (Signup):
   ```json
   {
     "error": "This email is already registered. Please sign in instead.",
     "field": "email"
   }
   ```

#### 401 Unauthorized - Authentication Errors

1. **Invalid Credentials** (Signin):
   ```json
   {
     "error": "Invalid email or password"
   }
   ```
   Note: Same message for wrong email or wrong password (security best practice)

2. **Missing Token**:
   ```json
   {
     "error": "Authentication required"
   }
   ```

3. **Invalid Token**:
   ```json
   {
     "error": "Invalid authentication token"
   }
   ```

4. **Expired Token**:
   ```json
   {
     "error": "Authentication token expired. Please sign in again."
   }
   ```

#### 500 Internal Server Error

1. **Database Error**:
   ```json
   {
     "error": "Service temporarily unavailable. Please try again."
   }
   ```

2. **Unexpected Error**:
   ```json
   {
     "error": "An unexpected error occurred. Please try again."
   }
   ```

---

## Security Considerations

### Password Security

1. **Never Log Passwords**: Passwords must never appear in logs
2. **Hash Before Storage**: Always hash passwords before database insertion
3. **Use bcrypt**: Industry-standard hashing algorithm with salt
4. **Secure Comparison**: Use constant-time comparison to prevent timing attacks

### Token Security

1. **Secure Secret**: `BETTER_AUTH_SECRET` must be:
   - At least 32 characters long
   - Randomly generated
   - Stored in environment variables only
   - Never committed to version control
   - Same secret used by frontend and backend

2. **Token Transmission**:
   - Always use HTTPS in production
   - Token sent in Authorization header (not URL)
   - Token not exposed in logs

3. **Token Storage**:
   - Stored in browser localStorage or sessionStorage
   - Not accessible to other domains (same-origin policy)
   - Cleared on signout

### Email Enumeration Prevention

- Signup and signin errors use generic messages
- "Invalid email or password" instead of "Email not found"
- Prevents attackers from discovering registered emails

### Brute Force Protection

Phase II does not include rate limiting, but production systems should implement:
- Rate limiting on authentication endpoints
- Account lockout after failed attempts
- CAPTCHA for suspicious activity

---

## API Endpoints

### POST /api/auth/signup

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Success Response (201 Created)**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "created_at": "2026-01-14T10:30:00Z"
  }
}
```

**Error Responses**: See Error Handling section

---

### POST /api/auth/signin

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Success Response (200 OK)**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "created_at": "2026-01-14T10:30:00Z"
  }
}
```

**Error Responses**: See Error Handling section

---

### POST /api/auth/signout

**Request**:
```
Authorization: Bearer <token>
```

**Success Response (200 OK)**:
```json
{
  "message": "Successfully signed out"
}
```

Note: Frontend is responsible for removing token from storage. Backend response is informational only (stateless authentication).

---

## Testing Scenarios

### Signup Tests

1. ✅ Valid email and password → Account created, token returned
2. ✅ Duplicate email → Error "Email already registered"
3. ✅ Invalid email format → Error "Invalid email address"
4. ✅ Password too short → Error "Password must be at least 8 characters"
5. ✅ Empty email → Error "Email is required"
6. ✅ Empty password → Error "Password is required"
7. ✅ Password is hashed → Plaintext password not in database

### Signin Tests

1. ✅ Valid credentials → Token returned, user authenticated
2. ✅ Wrong password → Error "Invalid email or password"
3. ✅ Non-existent email → Error "Invalid email or password"
4. ✅ Empty email → Error "Email is required"
5. ✅ Empty password → Error "Password is required"

### Token Tests

1. ✅ Valid token → API requests succeed
2. ✅ Expired token → 401 Unauthorized
3. ✅ Invalid signature → 401 Unauthorized
4. ✅ Missing token → 401 Unauthorized
5. ✅ Malformed token → 401 Unauthorized

### Session Tests

1. ✅ Refresh page while signed in → Remain authenticated
2. ✅ Close and reopen browser → Remain authenticated (within 7 days)
3. ✅ Sign out → Token removed, cannot access protected routes
4. ✅ Token expires → Redirected to signin on next request

### Route Protection Tests

1. ✅ Access protected route without token → Redirected to signin
2. ✅ Access protected route with valid token → Access granted
3. ✅ Access protected route with expired token → Redirected to signin

---

## Success Criteria

### Functional Success

- ✅ Users can create accounts with email and password
- ✅ Users can sign in with registered credentials
- ✅ Users remain authenticated across page refreshes
- ✅ Users can sign out and terminate their session
- ✅ Protected routes require valid authentication
- ✅ JWT tokens are issued and validated correctly

### Security Success

- ✅ Passwords are hashed with bcrypt before storage
- ✅ JWT tokens are signed with secure secret
- ✅ Token expiration is enforced (7 days)
- ✅ Invalid/expired tokens are rejected
- ✅ Email enumeration is prevented
- ✅ Plaintext passwords never logged or stored

### User Experience Success

- ✅ Signup completes in under 5 seconds
- ✅ Signin completes in under 5 seconds
- ✅ Clear error messages for all validation failures
- ✅ Automatic redirect after successful authentication
- ✅ Seamless session management (no repeated signin)

---

## References

- **Main Specification**: `specs/001-fullstack-web-app/spec.md`
- **API Endpoints**: `specs/001-fullstack-web-app/api/rest-endpoints.md`
- **Database Schema**: `specs/001-fullstack-web-app/database/schema.md`
- **Task CRUD**: `specs/001-fullstack-web-app/features/task-crud.md`
- **Architecture**: `specs/001-fullstack-web-app/architecture.md`
