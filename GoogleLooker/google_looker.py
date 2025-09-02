from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler
)
from typing import Dict, Any, List, Optional
import requests
import base64
import os
import json
from datetime import datetime, timedelta

config_path = os.path.join(os.path.dirname(__file__), "config.json")
google_looker = Integration.load(config_path)

class LookerAPIClient:
    """Helper class for Looker API operations"""
    
    def __init__(self, base_url: str, client_id: str, client_secret: str):
        self.base_url = base_url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = None
    
    def _get_access_token(self) -> str:
        """Get or refresh access token"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            print(f"[DEBUG] Using cached token, expires at: {self.token_expires_at}")
            return self.access_token
            
        print(f"[DEBUG] Requesting new token from: {self.base_url}/api/4.0/login")
        print(f"[DEBUG] Client ID: {self.client_id[:8]}...")
        
        auth_url = f"{self.base_url}/api/4.0/login"
        auth_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            response = requests.post(auth_url, data=auth_data, timeout=30)
            print(f"[DEBUG] Response status code: {response.status_code}")
            print(f"[DEBUG] Response headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                print(f"[DEBUG] Auth failed - Response body: {response.text}")
                print(f"[DEBUG] Request URL: {auth_url}")
                print(f"[DEBUG] Request data keys: {list(auth_data.keys())}")
                raise Exception(f"Authentication failed with status {response.status_code}: {response.text}")
            
            token_data = response.json()
            print(f"[DEBUG] Token response keys: {list(token_data.keys())}")
            
            self.access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            
            if not self.access_token:
                print(f"[DEBUG] No access_token in response: {token_data}")
                raise Exception("No access_token received in authentication response")
            
            print(f"[DEBUG] Successfully obtained token, expires in {expires_in} seconds")
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            print(f"[DEBUG] Network error during authentication: {str(e)}")
            raise Exception(f"Network error during authentication: {str(e)}")
        except json.JSONDecodeError as e:
            print(f"[DEBUG] Invalid JSON response: {response.text}")
            raise Exception(f"Invalid JSON response from authentication endpoint: {str(e)}")
        except Exception as e:
            print(f"[DEBUG] Unexpected error during authentication: {str(e)}")
            raise
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json"
        }
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated API request"""
        url = f"{self.base_url}/api/4.0{endpoint}"
        headers = self._get_headers()
        
        print(f"[DEBUG] Making {method} request to: {url}")
        if data:
            print(f"[DEBUG] Request data: {data}")
            print(f"[DEBUG] Request params: {params}")
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=100)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, params=params, timeout=100)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, params=params, timeout=100)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, params=params, timeout=100)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        print(f"[DEBUG] Response status: {response.status_code}")
        print(f"[DEBUG] Response headers: {dict(response.headers)}")
        
        if response.status_code not in [200, 201, 202, 204]:
            print(f"[DEBUG] Error response body: {response.text}")
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
        
        try:
            return response.json() if response.content else {}
        except json.JSONDecodeError:
            return response.text if response.content else ""

def build_looker_client(context: ExecutionContext) -> LookerAPIClient:
    """Build Looker API client from ExecutionContext or config"""
    try:
        print(f"[DEBUG] Building Looker client...")
        
        # Try to get credentials from context first (platform-provided)
        if hasattr(context, 'auth') and context.auth:
            print(f"[DEBUG] Using credentials from platform context")
            credentials = context.auth.get("credentials", {})
            base_url = credentials.get('base_url')
            client_id = credentials.get('client_id')
            client_secret = credentials.get('client_secret')
        else:
            # Fallback to config file
            print(f"[DEBUG] Using credentials from config file: {config_path}")
            with open(config_path, 'r') as f:
                config = json.load(f)
            base_url = config.get("base_url")
            client_id = config.get("client_id")
            client_secret = config.get("client_secret")
        
        print(f"[DEBUG] Base URL: {base_url}")
        print(f"[DEBUG] Client ID: {client_id[:8] if client_id else 'None'}...")
        print(f"[DEBUG] Client Secret: {'***' if client_secret else 'None'}")
        
        if not all([base_url, client_id, client_secret]):
            missing = []
            if not base_url: missing.append("base_url")
            if not client_id: missing.append("client_id")
            if not client_secret: missing.append("client_secret")
            print(f"[DEBUG] Missing configuration fields: {missing}")
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        print(f"[DEBUG] Successfully built Looker client with platform settings")
        return LookerAPIClient(base_url, client_id, client_secret)
    
    except Exception as e:
        print(f"[DEBUG] Failed to build Looker client: {str(e)}")
        raise Exception(f"Failed to build Looker client: {str(e)}")

@google_looker.action("test_connection")
class TestConnection(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Test the connection to Looker API"""
        try:
            client = build_looker_client(context)
            result = client.make_request("GET", "/user")
            
            return {
                "status": "success",
                "message": "Connection successful!",
                "user_info": result,
                "result": True
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection test failed: {str(e)}",
                "result": False
            }

@google_looker.action("list_dashboards")
class ListDashboards(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """List all dashboards"""
        try:
            client = build_looker_client(context)
            
            params = {}
            if 'fields' in inputs:
                params['fields'] = inputs['fields']
            if 'page' in inputs:
                params['page'] = inputs['page']
            if 'per_page' in inputs:
                params['per_page'] = inputs['per_page']
            
            dashboards = client.make_request("GET", "/dashboards", params=params)
            
            return {
                "dashboards": dashboards,
                "result": True
            }
            
        except Exception as e:
            return {
                "dashboards": [],
                "result": False,
                "error": str(e)
            }

@google_looker.action("get_dashboard")
class GetDashboard(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Get a specific dashboard by ID"""
        try:
            client = build_looker_client(context)
            dashboard_id = inputs['dashboard_id']
            
            params = {}
            if 'fields' in inputs:
                params['fields'] = inputs['fields']
            
            dashboard = client.make_request("GET", f"/dashboards/{dashboard_id}", params=params)
            
            return {
                "dashboard": dashboard,
                "result": True
            }
            
        except Exception as e:
            return {
                "dashboard": {},
                "result": False,
                "error": str(e)
            }

@google_looker.action("run_query")
class RunQuery(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Run a query and get results"""
        try:
            client = build_looker_client(context)
            query_id = inputs['query_id']
            result_format = inputs.get('result_format', 'json')
            
            params = {
                'result_format': result_format
            }
            if 'limit' in inputs:
                params['limit'] = inputs['limit']
            if 'apply_formatting' in inputs:
                params['apply_formatting'] = inputs['apply_formatting']
            if 'apply_vis' in inputs:
                params['apply_vis'] = inputs['apply_vis']
            
            results = client.make_request("GET", f"/queries/{query_id}/run/{result_format}", params=params)
            
            return {
                "query_results": json.dumps(results) if isinstance(results, (dict, list)) else str(results),
                "result": True
            }
            
        except Exception as e:
            return {
                "query_results": "[]",
                "result": False,
                "error": str(e)
            }

@google_looker.action("create_query")
class CreateQuery(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Create a new query"""
        try:
            client = build_looker_client(context)
            
            query_data = {
                "model": inputs['model'],
                "explore": inputs['explore']
            }
            
            if 'dimensions' in inputs:
                query_data['dimensions'] = inputs['dimensions']
            if 'measures' in inputs:
                query_data['measures'] = inputs['measures']
            if 'filters' in inputs:
                query_data['filters'] = inputs['filters']
            if 'sorts' in inputs:
                query_data['sorts'] = inputs['sorts']
            if 'limit' in inputs:
                query_data['limit'] = inputs['limit']
            
            query = client.make_request("POST", "/queries", data=query_data)
            
            return {
                "query": query,
                "result": True
            }
            
        except Exception as e:
            return {
                "query": {},
                "result": False,
                "error": str(e)
            }

@google_looker.action("list_looks")
class ListLooks(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """List all looks"""
        try:
            client = build_looker_client(context)
            
            params = {}
            if 'fields' in inputs:
                params['fields'] = inputs['fields']
            if 'page' in inputs:
                params['page'] = inputs['page']
            if 'per_page' in inputs:
                params['per_page'] = inputs['per_page']
            
            looks = client.make_request("GET", "/looks", params=params)
            
            return {
                "looks": looks,
                "result": True
            }
            
        except Exception as e:
            return {
                "looks": [],
                "result": False,
                "error": str(e)
            }

@google_looker.action("get_look")
class GetLook(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Get a specific look by ID"""
        try:
            client = build_looker_client(context)
            look_id = inputs['look_id']
            
            params = {}
            if 'fields' in inputs:
                params['fields'] = inputs['fields']
            
            look = client.make_request("GET", f"/looks/{look_id}", params=params)
            
            return {
                "look": look,
                "result": True
            }
            
        except Exception as e:
            return {
                "look": {},
                "result": False,
                "error": str(e)
            }

@google_looker.action("run_look")
class RunLook(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Run a look and get results"""
        try:
            client = build_looker_client(context)
            look_id = inputs['look_id']
            result_format = inputs.get('result_format', 'json')
            
            params = {
                'result_format': result_format
            }
            if 'limit' in inputs:
                params['limit'] = inputs['limit']
            if 'apply_formatting' in inputs:
                params['apply_formatting'] = inputs['apply_formatting']
            if 'apply_vis' in inputs:
                params['apply_vis'] = inputs['apply_vis']
            
            results = client.make_request("GET", f"/looks/{look_id}/run/{result_format}", params=params)
            
            return {
                "look_results": json.dumps(results) if isinstance(results, (dict, list)) else str(results),
                "result": True
            }
            
        except Exception as e:
            return {
                "look_results": "[]",
                "result": False,
                "error": str(e)
            }

@google_looker.action("list_models")
class ListModels(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """List all LookML models"""
        try:
            client = build_looker_client(context)
            
            params = {}
            if 'fields' in inputs:
                params['fields'] = inputs['fields']
            
            models = client.make_request("GET", "/lookml_models", params=params)
            
            return {
                "models": models,
                "result": True
            }
            
        except Exception as e:
            return {
                "models": [],
                "result": False,
                "error": str(e)
            }

@google_looker.action("get_model")
class GetModel(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Get a specific LookML model"""
        try:
            client = build_looker_client(context)
            model_name = inputs['model_name']
            
            params = {}
            if 'fields' in inputs:
                params['fields'] = inputs['fields']
            
            model = client.make_request("GET", f"/lookml_models/{model_name}", params=params)
            
            return {
                "model": model,
                "result": True
            }
            
        except Exception as e:
            return {
                "model": {},
                "result": False,
                "error": str(e)
            }

@google_looker.action("create_sql_query")
class CreateSQLQuery(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Create a SQL Runner Query"""
        try:
            client = build_looker_client(context)
            
            # Required: Either connection_name or model_name must be provided
            sql_query_data = {
                "sql": inputs['sql']
            }
            
            # Add required connection_name or model_name
            if 'connection_name' in inputs:
                sql_query_data['connection_name'] = inputs['connection_name']
            elif 'model_name' in inputs:
                sql_query_data['model_name'] = inputs['model_name']
            else:
                # If no connection_name or model_name provided, we need to get one
                raise ValueError("Either 'connection_name' or 'model_name' must be provided. Use list_connections or list_models to find available options.")
            
            # Optional parameters
            if 'vis_config' in inputs:
                sql_query_data['vis_config'] = inputs['vis_config']
            if 'slug' in inputs:
                sql_query_data['slug'] = inputs['slug']
            
            print(f"[DEBUG] Creating SQL query with data: {sql_query_data}")
            sql_query = client.make_request("POST", "/sql_queries", data=sql_query_data)
            
            return {
                "sql_query": sql_query,
                "result": True
            }
            
        except Exception as e:
            print(f"[DEBUG] Error creating SQL query: {str(e)}")
            return {
                "sql_query": {},
                "result": False,
                "error": str(e)
            }

@google_looker.action("list_connections")
class ListConnections(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """List all database connections"""
        try:
            client = build_looker_client(context)
            
            params = {}
            if 'fields' in inputs:
                params['fields'] = inputs['fields']
            
            connections = client.make_request("GET", "/connections", params=params)
            
            return {
                "connections": connections,
                "result": True
            }
            
        except Exception as e:
            return {
                "connections": [],
                "result": False,
                "error": str(e)
            }

@google_looker.action("run_sql_query")
class RunSQLQuery(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """Run SQL Runner Query"""
        try:
            client = build_looker_client(context)
            slug = inputs['slug']
            result_format = inputs.get('result_format', 'json')
            
            params = {}
            if 'download' in inputs:
                params['download'] = inputs['download']
            
            results = client.make_request("POST", f"/sql_queries/{slug}/run/{result_format}", params=params)
            
            return {
                "query_results": json.dumps(results) if isinstance(results, (dict, list)) else str(results),
                "result": True
            }
            
        except Exception as e:
            return {
                "query_results": "",
                "result": False,
                "error": str(e)
            }

