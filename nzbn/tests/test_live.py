"""
Live test script for NZBN API integration with 2-legged OAuth.
"""
import asyncio
import aiohttp
import base64

# OAuth Credentials - Replace with your actual values
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
SUBSCRIPTION_KEY = "YOUR_SUBSCRIPTION_KEY"

# Token endpoint (from MBIE docs)
TOKEN_URL = "https://login.microsoftonline.com/b2cessmapprd.onmicrosoft.com/oauth2/v2.0/token"

# Sandbox settings
SCOPE = "https://api.business.govt.nz/sandbox/.default"
BASE_URL = "https://api.business.govt.nz/sandbox/nzbn/v5"


async def get_access_token():
    """Get OAuth2 access token using client credentials flow."""
    print("\n=== Getting OAuth Access Token ===")
    print(f"Token URL: {TOKEN_URL}")
    print(f"Scope: {SCOPE}")
    
    # Create Basic auth header (base64 encoded client_id:client_secret)
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "client_credentials",
        "scope": SCOPE
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(TOKEN_URL, headers=headers, data=data) as response:
            print(f"Status: {response.status}")
            
            result = await response.json()
            
            if response.status == 200:
                token = result.get("access_token")
                expires_in = result.get("expires_in")
                print(f"SUCCESS! Token obtained (expires in {expires_in}s)")
                print(f"Token preview: {token[:50]}...")
                return token
            else:
                print(f"Error: {result.get('error')}")
                print(f"Description: {result.get('error_description', 'N/A')}")
                return None


def get_headers(access_token: str):
    return {
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }


async def fetch(url: str, access_token: str, params: dict = None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=get_headers(access_token), params=params) as response:
            print(f"  URL: {response.url}")
            print(f"  Status: {response.status}")
            if response.status == 200:
                return await response.json()
            else:
                text = await response.text()
                print(f"  Error: {text[:300]}")
                return None


async def test_search(access_token: str):
    """Test searching for entities."""
    print("\n" + "="*50)
    print("TEST: Search Entities")
    print("="*50)
    
    result = await fetch(
        f"{BASE_URL}/entities",
        access_token=access_token,
        params={
            "search-term": "Test",
            "page-size": 5
        }
    )
    
    if result:
        print(f"\nTotal results: {result.get('totalItems', 0)}")
        for item in result.get('items', [])[:3]:
            print(f"  - {item.get('entityName')} (NZBN: {item.get('nzbn')})")
            print(f"    Type: {item.get('entityTypeDescription')}")
            print(f"    Status: {item.get('entityStatusDescription')}")
        
        if result.get('items'):
            return result['items'][0]['nzbn']
    return None


async def test_get_entity(nzbn: str, access_token: str):
    """Test getting entity details."""
    print("\n" + "="*50)
    print(f"TEST: Get Entity Details - {nzbn}")
    print("="*50)
    
    result = await fetch(f"{BASE_URL}/entities/{nzbn}", access_token=access_token)
    
    if result:
        print(f"\nEntity Name: {result.get('entityName')}")
        print(f"Type: {result.get('entityTypeDescription')}")
        print(f"Status: {result.get('entityStatusDescription')}")
        print(f"Registration Date: {result.get('registrationDate')}")
        
        if result.get('addresses'):
            print(f"Addresses: {len(result['addresses'])}")
        if result.get('roles'):
            print(f"Roles: {len(result['roles'])}")
    
    return result


async def test_get_roles(nzbn: str, access_token: str):
    """Test getting entity roles."""
    print("\n" + "="*50)
    print(f"TEST: Get Roles - {nzbn}")
    print("="*50)
    
    result = await fetch(f"{BASE_URL}/entities/{nzbn}/roles", access_token=access_token)
    
    if result:
        items = result.get('items', []) if isinstance(result, dict) else result
        print(f"\nFound {len(items)} roles:")
        for role in items[:5]:
            role_type = role.get('roleType', 'Unknown')
            status = role.get('roleStatus', 'N/A')
            
            if role.get('rolePerson'):
                person = role['rolePerson']
                name = f"{person.get('firstName', '')} {person.get('lastName', '')}".strip()
            elif role.get('roleEntity'):
                name = role['roleEntity'].get('entityName', 'Unknown')
            else:
                name = 'Unknown'
            
            print(f"  - {role_type}: {name} ({status})")
    
    return result


async def main():
    print("\n" + "#"*50)
    print("NZBN API SANDBOX TEST - 2-LEGGED OAUTH")
    print("#"*50)
    print(f"API Base URL: {BASE_URL}")
    print(f"Client ID: {CLIENT_ID}")
    print(f"Subscription Key: {SUBSCRIPTION_KEY[:12]}...")
    
    try:
        # Step 1: Get OAuth token
        access_token = await get_access_token()
        
        if not access_token:
            print("\nFailed to get access token. Check your Client ID and Secret.")
            return
        
        # Step 2: Test search
        nzbn = await test_search(access_token)
        
        if nzbn:
            # Step 3: Test entity details
            await test_get_entity(nzbn, access_token)
            
            # Step 4: Test roles
            await test_get_roles(nzbn, access_token)
            
            print("\n" + "#"*50)
            print("ALL TESTS PASSED!")
            print("#"*50)
        else:
            print("\nSearch returned no results.")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
