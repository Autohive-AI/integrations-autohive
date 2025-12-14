---
api: shopify-customer-account
type: authentication-guide
format: llm-optimized
---

# OAuth 2.0 + PKCE Implementation Guide

## OVERVIEW

The Customer Account API uses OAuth 2.0 with PKCE (Proof Key for Code Exchange) for authentication. PKCE protects against authorization code interception attacks, making it safe for public clients (mobile apps, SPAs).

---

## PKCE_FLOW_DIAGRAM

```
┌──────────┐                                    ┌─────────────┐
│  Client  │                                    │   Shopify   │
└────┬─────┘                                    └──────┬──────┘
     │                                                 │
     │ 1. Generate code_verifier & code_challenge      │
     │ ─────────────────────────────────────────────>  │
     │                                                 │
     │ 2. Authorization Request                        │
     │    (client_id, code_challenge, scope, etc.)     │
     │ ─────────────────────────────────────────────>  │
     │                                                 │
     │                  3. User Login & Consent        │
     │ <─────────────────────────────────────────────  │
     │                                                 │
     │ 4. Authorization Code (via redirect)            │
     │ <─────────────────────────────────────────────  │
     │                                                 │
     │ 5. Token Request                                │
     │    (code, code_verifier)                        │
     │ ─────────────────────────────────────────────>  │
     │                                                 │
     │ 6. Access Token + Refresh Token + ID Token      │
     │ <─────────────────────────────────────────────  │
     │                                                 │
     │ 7. API Request with Access Token                │
     │ ─────────────────────────────────────────────>  │
     │                                                 │
```

---

## STEP_1_GENERATE_PKCE

### Code Verifier
A cryptographically random string between 43-128 characters.

```python
import secrets

def generate_code_verifier():
    """Generate a secure random code verifier."""
    return secrets.token_urlsafe(32)  # 43 characters
```

### Code Challenge
SHA-256 hash of code_verifier, base64url encoded.

```python
import hashlib
import base64

def generate_code_challenge(code_verifier: str) -> str:
    """Generate code challenge from verifier using S256."""
    digest = hashlib.sha256(code_verifier.encode('ascii')).digest()
    challenge = base64.urlsafe_b64encode(digest).decode('ascii')
    return challenge.rstrip('=')  # Remove padding
```

### Complete PKCE Generation
```python
def generate_pkce_pair():
    """Generate code_verifier and code_challenge pair."""
    code_verifier = secrets.token_urlsafe(32)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip('=')
    return code_verifier, code_challenge

# Usage
code_verifier, code_challenge = generate_pkce_pair()
# Store code_verifier securely - needed for token exchange
```

---

## STEP_2_AUTHORIZATION_REQUEST

### Build Authorization URL

```python
from urllib.parse import urlencode

def build_authorization_url(
    shop: str,
    client_id: str,
    redirect_uri: str,
    scopes: list,
    state: str,
    code_challenge: str
) -> str:
    """Build the Shopify authorization URL."""
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': ' '.join(scopes),
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    base_url = f"https://{shop}/account/authorize"
    return f"{base_url}?{urlencode(params)}"
```

### Parameters Explained

```yaml
client_id:
  description: Your OAuth client ID from Shopify
  source: Shopify Admin > Apps > Headless channel

redirect_uri:
  description: Where Shopify sends the user after auth
  must_match: Exactly match registered URI
  example: "https://myapp.com/auth/callback"

response_type:
  value: "code"
  description: Request authorization code

scope:
  description: Space-separated list of scopes
  example: "customer_read_customers customer_read_orders"

state:
  description: Random string to prevent CSRF
  generate: secrets.token_urlsafe(16)
  verify: Must match on callback

code_challenge:
  description: Base64url(SHA256(code_verifier))
  method: S256

code_challenge_method:
  value: "S256"
  description: SHA-256 challenge method
```

### Example URL
```
https://my-store.myshopify.com/account/authorize?
  client_id=abc123
  &redirect_uri=https://myapp.com/callback
  &response_type=code
  &scope=customer_read_customers%20customer_read_orders
  &state=xyz789
  &code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM
  &code_challenge_method=S256
```

---

## STEP_3_USER_AUTHORIZATION

The user is redirected to Shopify where they:
1. Log in to their customer account
2. Review requested permissions
3. Approve or deny access

---

## STEP_4_CALLBACK_HANDLING

### Successful Callback
```
https://myapp.com/callback?
  code=authorization_code_here
  &state=xyz789
```

### Handle Callback
```python
def handle_oauth_callback(callback_url: str, expected_state: str) -> str:
    """Extract and validate authorization code from callback."""
    from urllib.parse import urlparse, parse_qs

    parsed = urlparse(callback_url)
    params = parse_qs(parsed.query)

    # Verify state to prevent CSRF
    received_state = params.get('state', [None])[0]
    if received_state != expected_state:
        raise ValueError("State mismatch - possible CSRF attack")

    # Check for errors
    if 'error' in params:
        error = params['error'][0]
        description = params.get('error_description', ['Unknown'])[0]
        raise ValueError(f"OAuth error: {error} - {description}")

    # Extract code
    code = params.get('code', [None])[0]
    if not code:
        raise ValueError("No authorization code received")

    return code
```

---

## STEP_5_TOKEN_EXCHANGE

### Exchange Code for Tokens
```python
import aiohttp

async def exchange_code_for_tokens(
    shop: str,
    client_id: str,
    code: str,
    redirect_uri: str,
    code_verifier: str
) -> dict:
    """Exchange authorization code for access tokens."""
    url = f"https://{shop}/account/oauth/token"

    data = {
        'client_id': client_id,
        'code': code,
        'redirect_uri': redirect_uri,
        'code_verifier': code_verifier,
        'grant_type': 'authorization_code'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            if response.status != 200:
                error = await response.text()
                raise ValueError(f"Token exchange failed: {error}")
            return await response.json()
```

### Token Response
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6...",
  "refresh_token": "def50200...",
  "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "customer_read_customers customer_read_orders"
}
```

---

## STEP_6_USE_ACCESS_TOKEN

### Make API Requests
```python
async def customer_api_request(
    shop: str,
    access_token: str,
    query: str,
    variables: dict = None
) -> dict:
    """Make authenticated request to Customer Account API."""
    url = f"https://{shop}/account/customer/api/2024-10/graphql"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    payload = {'query': query}
    if variables:
        payload['variables'] = variables

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            return await response.json()
```

---

## STEP_7_TOKEN_REFRESH

### Refresh Access Token
```python
async def refresh_access_token(
    shop: str,
    client_id: str,
    refresh_token: str
) -> dict:
    """Get new access token using refresh token."""
    url = f"https://{shop}/account/oauth/token"

    data = {
        'client_id': client_id,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            if response.status != 200:
                error = await response.text()
                raise ValueError(f"Token refresh failed: {error}")
            return await response.json()
```

### Refresh Response
```json
{
  "access_token": "new_access_token...",
  "refresh_token": "new_refresh_token...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

**Note:** Refresh token rotation - you receive a new refresh_token with each refresh. Store the new one.

---

## ID_TOKEN_VALIDATION

### ID Token Structure (JWT)
```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "key-id"
  },
  "payload": {
    "iss": "https://my-store.myshopify.com",
    "sub": "gid://shopify/Customer/12345",
    "aud": "your-client-id",
    "exp": 1234567890,
    "iat": 1234567800,
    "nonce": "optional-nonce",
    "email": "customer@example.com"
  }
}
```

### Validation Steps
```python
import jwt
from jwt import PyJWKClient

def validate_id_token(id_token: str, shop: str, client_id: str) -> dict:
    """Validate and decode ID token."""
    # Get Shopify's public keys
    jwks_url = f"https://{shop}/.well-known/jwks.json"
    jwks_client = PyJWKClient(jwks_url)
    signing_key = jwks_client.get_signing_key_from_jwt(id_token)

    # Decode and validate
    payload = jwt.decode(
        id_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=client_id,
        issuer=f"https://{shop}"
    )

    return payload
```

---

## COMPLETE_FLOW_EXAMPLE

```python
import secrets
import hashlib
import base64
import aiohttp
from urllib.parse import urlencode, urlparse, parse_qs

class ShopifyCustomerOAuth:
    def __init__(self, shop: str, client_id: str, redirect_uri: str):
        self.shop = shop
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self._code_verifier = None
        self._state = None

    def generate_pkce(self):
        """Generate PKCE code verifier and challenge."""
        self._code_verifier = secrets.token_urlsafe(32)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(self._code_verifier.encode()).digest()
        ).decode().rstrip('=')
        return code_challenge

    def get_authorization_url(self, scopes: list) -> str:
        """Build authorization URL."""
        self._state = secrets.token_urlsafe(16)
        code_challenge = self.generate_pkce()

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': ' '.join(scopes),
            'state': self._state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }

        return f"https://{self.shop}/account/authorize?{urlencode(params)}"

    def parse_callback(self, callback_url: str) -> str:
        """Parse callback URL and extract authorization code."""
        parsed = urlparse(callback_url)
        params = parse_qs(parsed.query)

        # Verify state
        if params.get('state', [None])[0] != self._state:
            raise ValueError("State mismatch")

        if 'error' in params:
            raise ValueError(f"OAuth error: {params['error'][0]}")

        return params['code'][0]

    async def exchange_code(self, code: str) -> dict:
        """Exchange authorization code for tokens."""
        url = f"https://{self.shop}/account/oauth/token"

        data = {
            'client_id': self.client_id,
            'code': code,
            'redirect_uri': self.redirect_uri,
            'code_verifier': self._code_verifier,
            'grant_type': 'authorization_code'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                return await response.json()

    async def refresh_token(self, refresh_token: str) -> dict:
        """Refresh access token."""
        url = f"https://{self.shop}/account/oauth/token"

        data = {
            'client_id': self.client_id,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                return await response.json()


# Usage Example
async def main():
    oauth = ShopifyCustomerOAuth(
        shop="my-store.myshopify.com",
        client_id="your-client-id",
        redirect_uri="https://myapp.com/callback"
    )

    # Step 1: Get authorization URL
    auth_url = oauth.get_authorization_url([
        'customer_read_customers',
        'customer_read_orders'
    ])
    print(f"Redirect user to: {auth_url}")

    # Step 2: User authorizes, you receive callback
    callback = input("Paste callback URL: ")

    # Step 3: Parse callback and exchange code
    code = oauth.parse_callback(callback)
    tokens = await oauth.exchange_code(code)

    print(f"Access Token: {tokens['access_token'][:50]}...")
    print(f"Refresh Token: {tokens['refresh_token'][:20]}...")
```

---

## SECURITY_CHECKLIST

```yaml
code_verifier:
  - Generate per authorization request
  - Store securely during flow
  - Never expose to browser/client
  - Delete after token exchange

state:
  - Generate random value per request
  - Store before redirect
  - Verify on callback
  - Prevents CSRF attacks

tokens:
  - Store access_token in memory
  - Store refresh_token encrypted
  - Refresh before expiry
  - Clear all on logout

id_token:
  - Validate signature
  - Check issuer (iss)
  - Check audience (aud)
  - Check expiration (exp)
```

---

## TROUBLESHOOTING

### Common Errors

```yaml
invalid_request:
  cause: Missing or invalid parameter
  fix: Check all required params are present

invalid_grant:
  cause: Code expired or already used
  fix: Restart OAuth flow

invalid_client:
  cause: Wrong client_id or redirect_uri
  fix: Verify values match Shopify config

access_denied:
  cause: User denied permissions
  fix: Handle gracefully, explain why access is needed
```
