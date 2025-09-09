from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler
)
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import time
from collections import defaultdict

# Create the integration using the config.json
xero = Integration.load("config.json")


# ---- Rate Limiting Classes ----

class TenantRateBucket:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.requests_per_minute = 60
        self.daily_limit = 5000
        
        # Current minute tracking
        self.current_minute_count = 0
        self.current_minute_start = time.time()
        
        # Daily tracking
        self.daily_count = 0
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        # Request timestamps for sliding window
        self.request_times = []
        
        self._lock = asyncio.Lock()
    
    async def can_make_request(self) -> bool:
        """Check if we can make a request without violating limits"""
        async with self._lock:
            now = time.time()
            
            # Reset daily counter if new day
            if datetime.now() >= self.daily_reset_time:
                self.daily_count = 0
                self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            
            # Clean old request timestamps (older than 1 minute)
            minute_ago = now - 60
            self.request_times = [t for t in self.request_times if t > minute_ago]
            
            # Check limits
            if self.daily_count >= self.daily_limit:
                return False
            
            if len(self.request_times) >= self.requests_per_minute:
                return False
            
            return True
    
    async def wait_for_availability(self):
        """Wait until we can make a request"""
        while not await self.can_make_request():
            # Calculate wait time
            now = time.time()
            
            # If we hit daily limit, wait until tomorrow
            if self.daily_count >= self.daily_limit:
                wait_time = (self.daily_reset_time - datetime.now()).total_seconds()
                await asyncio.sleep(min(wait_time, 60))  # Sleep max 1 minute at a time
                continue
            
            # If we hit minute limit, wait for the oldest request to expire
            if self.request_times:
                oldest_request = min(self.request_times)
                wait_time = 61 - (now - oldest_request)  # Wait until it's been 61 seconds
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
            else:
                await asyncio.sleep(1)
    
    async def record_request(self):
        """Record that a request was made"""
        async with self._lock:
            now = time.time()
            self.request_times.append(now)
            self.daily_count += 1
    
    def update_from_headers(self, headers: dict):
        """Update rate limits from Xero response headers"""
        # Xero rate limit headers (if present)
        if 'X-Rate-Limit-Daily-Limit' in headers:
            try:
                self.daily_limit = int(headers['X-Rate-Limit-Daily-Limit'])
            except ValueError:
                pass
        
        if 'X-Rate-Limit-Daily-Remaining' in headers:
            try:
                remaining = int(headers['X-Rate-Limit-Daily-Remaining'])
                self.daily_count = self.daily_limit - remaining
            except ValueError:
                pass
        
        if 'X-Rate-Limit-Minute-Limit' in headers:
            try:
                self.requests_per_minute = int(headers['X-Rate-Limit-Minute-Limit'])
            except ValueError:
                pass


class XeroRateLimiter:
    def __init__(self):
        self.tenant_buckets: Dict[str, TenantRateBucket] = {}
        self._lock = asyncio.Lock()
    
    async def get_bucket(self, tenant_id: str) -> TenantRateBucket:
        """Get or create a rate limiting bucket for a tenant"""
        async with self._lock:
            if tenant_id not in self.tenant_buckets:
                self.tenant_buckets[tenant_id] = TenantRateBucket(tenant_id)
            return self.tenant_buckets[tenant_id]
    
    async def make_request(self, context: ExecutionContext, url: str, tenant_id: str, **kwargs) -> Any:
        """Make a rate-limited request to Xero API"""
        bucket = await self.get_bucket(tenant_id)
        
        # Wait for rate limit availability
        await bucket.wait_for_availability()
        
        # Record the request
        await bucket.record_request()
        
        # Add tenant header to the request
        headers = kwargs.get('headers', {})
        headers['xero-tenant-id'] = tenant_id
        kwargs['headers'] = headers
        
        try:
            # Make the actual request
            response = await context.fetch(url, **kwargs)
            
            # Update rate limits from response headers if available
            if hasattr(response, 'headers') and response.headers:
                bucket.update_from_headers(response.headers)
            
            return response
        
        except Exception as e:
            # If it's a rate limit error, we might need to back off more
            if '429' in str(e) or 'rate limit' in str(e).lower():
                # Add extra delay for rate limit errors
                await asyncio.sleep(60)  # Wait 1 minute
            raise e


# Global rate limiter instance
rate_limiter = XeroRateLimiter()

# ---- Helper Functions ----


async def get_all_connections(context: ExecutionContext) -> list:
    """
    Gets all tenant connections from Xero connections API
    """
    try:
        response = await context.fetch(
            "https://api.xero.com/connections",
            method="GET",
            headers={"Accept": "application/json"}
        )
        
        if not response or not isinstance(response, list) or len(response) == 0:
            raise ValueError("No Xero connections found")
        
        return response
        
    except Exception as e:
        raise Exception(f"Failed to get connections: {str(e)}")



# ---- Action Handlers ----


@xero.action("get_available_connections")
class GetAvailableConnectionsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Gets all available Xero tenant connections and returns company names
        """
        try:
            # Get all connections from Xero
            connections = await get_all_connections(context)
            
            # Extract company information
            companies = []
            for connection in connections:
                tenant_name = connection.get("tenantName")
                tenant_id = connection.get("tenantId")
                if tenant_name and tenant_id:
                    companies.append({
                        "tenant_id": tenant_id,
                        "company_name": tenant_name
                    })
            
            return {
                "success": True,
                "companies": companies
            }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to get connections: {str(e)}",
                "companies": []
            }




@xero.action("find_contact_by_name")
class FindContactByNameAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Finds contact ID by filtering contacts with matching name in Xero
        """
        # Validate required inputs
        tenant_id = inputs.get("tenant_id")
        contact_name = inputs.get("contact_name")
        
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not contact_name:
            raise ValueError("contact_name is required")
        
        try:
            
            # Build URL with where filter for contact name
            url = "https://api.xero.com/api.xro/2.0/Contacts"
            params = {
                "where": f'Name.Contains("{contact_name}")'
            }
            
            # Make rate-limited authenticated request to Xero API
            response = await rate_limiter.make_request(
                context,
                url,
                tenant_id,
                method="GET",
                params=params,
                headers={"Accept": "application/json"}
            )
            
            if not response or not response.get("Contacts"):
                return {"contacts": []}
            
            # Extract relevant contact information
            contacts = []
            for contact in response["Contacts"]:
                contacts.append({
                    "contact_id": contact.get("ContactID"),
                    "name": contact.get("Name"),
                    "contact_status": contact.get("ContactStatus")
                })
            
            return {"contacts": contacts}
                
        except Exception as e:
            raise Exception(f"Failed to find contact by name: {str(e)}")


@xero.action("get_aged_payables")
class GetAgedPayablesAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Fetches aged payables report from Xero API for a specific contact
        """
        # Validate required inputs
        tenant_id = inputs.get("tenant_id")
        contact_id = inputs.get("contact_id")
        
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not contact_id:
            raise ValueError("contact_id is required")
        
        try:
            
            # Build URL with parameters
            url = "https://api.xero.com/api.xro/2.0/Reports/AgedPayablesByContact"
            params = {
                "contactId": contact_id
            }
            
            # Add optional date parameter
            if inputs.get("date"):
                params["date"] = inputs["date"]
            
            # Make rate-limited authenticated request to Xero API
            response = await rate_limiter.make_request(
                context,
                url,
                tenant_id,
                method="GET",
                params=params,
                headers={"Accept": "application/json"}
            )
            
            # Return raw API response
            if not response:
                raise ValueError("Empty response from Xero API")
            
            return response
                
        except Exception as e:
            raise Exception(f"Failed to fetch aged payables report: {str(e)}")


@xero.action("get_aged_receivables")
class GetAgedReceivablesAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Fetches aged receivables report from Xero API for a specific contact
        """
        # Validate required inputs
        tenant_id = inputs.get("tenant_id")
        contact_id = inputs.get("contact_id")
        
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not contact_id:
            raise ValueError("contact_id is required")
        
        try:
            
            # Build URL with parameters
            url = "https://api.xero.com/api.xro/2.0/Reports/AgedReceivablesByContact"
            params = {
                "contactId": contact_id
            }
            
            # Add optional date parameter
            if inputs.get("date"):
                params["date"] = inputs["date"]
            
            # Make rate-limited authenticated request to Xero API
            response = await rate_limiter.make_request(
                context,
                url,
                tenant_id,
                method="GET",
                params=params,
                headers={"Accept": "application/json"}
            )
            
            # Return raw API response
            if not response:
                raise ValueError("Empty response from Xero API")
            
            return response
                
        except Exception as e:
            raise Exception(f"Failed to fetch aged receivables report: {str(e)}")


@xero.action("get_balance_sheet")
class GetBalanceSheetAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Fetches balance sheet report from Xero API
        """
        # Validate required inputs
        tenant_id = inputs.get("tenant_id")
        if not tenant_id:
            raise ValueError("tenant_id is required")
        
        try:
            
            # Build URL with parameters
            url = "https://api.xero.com/api.xro/2.0/Reports/BalanceSheet"
            params = {}
            
            # Add optional date parameter
            if inputs.get("date"):
                params["date"] = inputs["date"]
            
            # Add optional periods parameter
            if inputs.get("periods"):
                params["periods"] = str(inputs["periods"])
            
            # Make rate-limited authenticated request to Xero API
            response = await rate_limiter.make_request(
                context,
                url,
                tenant_id,
                method="GET",
                params=params,
                headers={"Accept": "application/json"}
            )
            
            # Return raw API response
            if not response:
                raise ValueError("Empty response from Xero API")
            
            return response
                
        except Exception as e:
            raise Exception(f"Failed to fetch balance sheet report: {str(e)}")


@xero.action("get_profit_and_loss")
class GetProfitAndLossAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Fetches profit and loss report from Xero API
        """
        # Validate required inputs
        tenant_id = inputs.get("tenant_id")
        if not tenant_id:
            raise ValueError("tenant_id is required")
        
        try:
            
            # Build URL with parameters
            url = "https://api.xero.com/api.xro/2.0/Reports/ProfitAndLoss"
            params = {}
            
            # Add optional date parameter
            if inputs.get("date"):
                params["date"] = inputs["date"]
            
            # Add optional from_date parameter
            if inputs.get("from_date"):
                params["fromDate"] = inputs["from_date"]
            
            # Add optional to_date parameter
            if inputs.get("to_date"):
                params["toDate"] = inputs["to_date"]
            
            # Add optional timeframe parameter
            if inputs.get("timeframe"):
                params["timeframe"] = inputs["timeframe"]
            
            # Add optional periods parameter
            if inputs.get("periods"):
                params["periods"] = str(inputs["periods"])
            
            # Make rate-limited authenticated request to Xero API
            response = await rate_limiter.make_request(
                context,
                url,
                tenant_id,
                method="GET",
                params=params,
                headers={"Accept": "application/json"}
            )
            
            # Return raw API response
            if not response:
                raise ValueError("Empty response from Xero API")
            
            return response
                
        except Exception as e:
            raise Exception(f"Failed to fetch profit and loss report: {str(e)}")


@xero.action("get_trial_balance")
class GetTrialBalanceAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Fetches trial balance report from Xero API
        """
        # Validate required inputs
        tenant_id = inputs.get("tenant_id")
        if not tenant_id:
            raise ValueError("tenant_id is required")
        
        try:
            
            # Build URL with parameters
            url = "https://api.xero.com/api.xro/2.0/Reports/TrialBalance"
            params = {}
            
            # Add optional date parameter
            if inputs.get("date"):
                params["date"] = inputs["date"]
            
            # Add optional payments_only parameter
            if inputs.get("payments_only") is not None:
                params["paymentsOnly"] = str(inputs["payments_only"]).lower()
            
            # Make rate-limited authenticated request to Xero API
            response = await rate_limiter.make_request(
                context,
                url,
                tenant_id,
                method="GET",
                params=params,
                headers={"Accept": "application/json"}
            )
            
            # Return raw API response
            if not response:
                raise ValueError("Empty response from Xero API")
            
            return response
                
        except Exception as e:
            raise Exception(f"Failed to fetch trial balance report: {str(e)}")


@xero.action("get_accounts")
class GetAccountsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Fetches accounts from Xero API to classify line items (revenue, expenses, fixed assets, loans, equity/dividends, GST)
        """
        # Validate required inputs
        tenant_id = inputs.get("tenant_id")
        if not tenant_id:
            raise ValueError("tenant_id is required")
        
        try:
            
            # Build URL with parameters
            url = "https://api.xero.com/api.xro/2.0/Accounts"
            params = {}
            
            # Add optional where parameter for filtering
            if inputs.get("where"):
                params["where"] = inputs["where"]
            
            # Add optional order parameter
            if inputs.get("order"):
                params["order"] = inputs["order"]
            
            # Make rate-limited authenticated request to Xero API
            response = await rate_limiter.make_request(
                context,
                url,
                tenant_id,
                method="GET",
                params=params,
                headers={"Accept": "application/json"}
            )
            
            # Return raw API response
            if not response:
                raise ValueError("Empty response from Xero API")
            
            return response
                
        except Exception as e:
            raise Exception(f"Failed to fetch accounts: {str(e)}")


@xero.action("get_payments")
class GetPaymentsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Fetches payments from Xero API for cash on invoices/bills (customer receipts, supplier payments, cash refunds)
        Supports date filtering with where clause
        """
        # Validate required inputs
        tenant_id = inputs.get("tenant_id")
        if not tenant_id:
            raise ValueError("tenant_id is required")
        
        try:
            
            # Build URL with parameters
            url = "https://api.xero.com/api.xro/2.0/Payments"
            params = {}
            
            # Add optional where parameter for date filtering
            if inputs.get("where"):
                params["where"] = inputs["where"]
            
            # Add optional order parameter
            if inputs.get("order"):
                params["order"] = inputs["order"]
            
            # Make rate-limited authenticated request to Xero API
            response = await rate_limiter.make_request(
                context,
                url,
                tenant_id,
                method="GET",
                params=params,
                headers={"Accept": "application/json"}
            )
            
            # Return raw API response
            if not response:
                raise ValueError("Empty response from Xero API")
            
            return response
                
        except Exception as e:
            raise Exception(f"Failed to fetch payments: {str(e)}")


@xero.action("get_bank_transactions")
class GetBankTransactionsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Fetches bank transactions from Xero API for Receive/Spend Money not tied to invoices (CapEx, financing, other operating)
        Supports date filtering with where clause and pagination
        """
        # Validate required inputs
        tenant_id = inputs.get("tenant_id")
        if not tenant_id:
            raise ValueError("tenant_id is required")
        
        try:
            
            # Build URL with parameters
            url = "https://api.xero.com/api.xro/2.0/BankTransactions"
            params = {}
            
            # Add optional where parameter for date filtering
            if inputs.get("where"):
                params["where"] = inputs["where"]
            
            # Add optional order parameter
            if inputs.get("order"):
                params["order"] = inputs["order"]
            
            # Add optional page parameter for pagination
            if inputs.get("page"):
                params["page"] = str(inputs["page"])
            
            # Make rate-limited authenticated request to Xero API
            response = await rate_limiter.make_request(
                context,
                url,
                tenant_id,
                method="GET",
                params=params,
                headers={"Accept": "application/json"}
            )
            
            # Return raw API response
            if not response:
                raise ValueError("Empty response from Xero API")
            
            return response
                
        except Exception as e:
            raise Exception(f"Failed to fetch bank transactions: {str(e)}")
