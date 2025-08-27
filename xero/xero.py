from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler
)
from typing import Dict, Any, Optional
from datetime import datetime

# Create the integration using the config.json
xero = Integration.load("config.json")
Xero = Integration.load("config.json")

# ---- Helper Functions ----


async def get_tenant_by_company_name(context: ExecutionContext, company_name: str) -> Dict[str, str]:
async def get_all_connections(context: ExecutionContext) -> list:
    """
    Gets tenant ID and name by company name from Xero connections API
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
        
        # Search for tenant with matching company name (case insensitive)
        for connection in response:
            tenant_name = connection.get("tenantName", "")
            if tenant_name.lower() == company_name.lower():
                tenant_id = connection.get("tenantId")
                if tenant_id:
                    return {
                        "tenant_id": tenant_id,
                        "tenant_name": tenant_name
                    }
        
        raise ValueError(f"No tenant found with company name: {company_name}")
        return response
        
    except Exception as e:
        raise Exception(f"Failed to get tenant by company name: {str(e)}")
        raise Exception(f"Failed to get connections: {str(e)}")

# ---- Action Handlers ----


@xero.action("get_tenant_by_company_name")
class GetTenantByCompanyNameAction(ActionHandler):
@Xero.action("get_available_connections")
class GetAvailableConnectionsAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Fetches tenant information (ID and name) by company name from Xero connections
        Gets all available Xero tenant connections and returns company names
        """
        # Validate required inputs
        company_name = inputs.get("company_name")
        if not company_name:
            raise ValueError("company_name is required")
        
        try:
            # Get tenant information by company name
            tenant_info = await get_tenant_by_company_name(context, company_name)
            return tenant_info
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
            raise Exception(f"Failed to get tenant by company name: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to get connections: {str(e)}",
                "companies": []
            }




@xero.action("find_contact_by_name")
@Xero.action("find_contact_by_name")
class FindContactByNameAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Finds contact ID by searching for contacts with matching name in Xero
        Finds contact ID by filtering contacts with matching name in Xero
        """
        # Validate required inputs
        company_name = inputs.get("company_name")
        tenant_id = inputs.get("tenant_id")
        contact_name = inputs.get("contact_name")
        
        if not company_name:
            raise ValueError("company_name is required")
            raise ValueError("tenant_id is required")
        if not contact_name:
            raise ValueError("contact_name is required")
        
        try:
            # Get tenant information by company name
            tenant_info = await get_tenant_by_company_name(context, company_name)
            tenant_id = tenant_info["tenant_id"]
            
            # Build URL with where filter for contact name
            url = "https://api.xero.com/api.xro/2.0/Contacts"
            params = {
                "where": f'Name.Contains("{contact_name}")'
            }
            
            # Make authenticated request to Xero API
            response = await context.fetch(
                url,
                method="GET",
                params=params,
                headers={
                    "Accept": "application/json",
                    "xero-tenant-id": tenant_id
                }
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
@Xero.action("get_aged_payables")
class GetAgedPayablesAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Fetches aged payables report from Xero API for a specific contact
        """
        # Validate required inputs
        company_name = inputs.get("company_name")
        tenant_id = inputs.get("tenant_id")
        contact_id = inputs.get("contact_id")
        
        if not company_name:
            raise ValueError("company_name is required")
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not contact_id:
            raise ValueError("contact_id is required")
        
        try:
            # Get tenant information by company name
            tenant_info = await get_tenant_by_company_name(context, company_name)
            tenant_id = tenant_info["tenant_id"]
            
            # Build URL with parameters
            url = "https://api.xero.com/api.xro/2.0/Reports/AgedPayablesByContact"
            params = {
                "contactId": contact_id
            }
            
            # Add optional date parameter
            if inputs.get("date"):
                params["date"] = inputs["date"]
            
            # Make authenticated request to Xero API
            response = await context.fetch(
                url,
                method="GET",
                params=params,
                headers={
                    "Accept": "application/json",
                    "xero-tenant-id": tenant_id
                }
            )
            
            # Return raw API response
            if not response:
                raise ValueError("Empty response from Xero API")
            
            return response
                
        except Exception as e:
            raise Exception(f"Failed to fetch aged payables report: {str(e)}")


@xero.action("get_aged_receivables")
@Xero.action("get_aged_receivables")
class GetAgedReceivablesAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Fetches aged receivables report from Xero API for a specific contact
        """
        # Validate required inputs
        company_name = inputs.get("company_name")
        tenant_id = inputs.get("tenant_id")
        contact_id = inputs.get("contact_id")
        
        if not company_name:
            raise ValueError("company_name is required")
        if not tenant_id:
            raise ValueError("tenant_id is required")
        if not contact_id:
            raise ValueError("contact_id is required")
        
        try:
            # Get tenant information by company name
            tenant_info = await get_tenant_by_company_name(context, company_name)
            tenant_id = tenant_info["tenant_id"]
            
            # Build URL with parameters
            url = "https://api.xero.com/api.xro/2.0/Reports/AgedReceivablesByContact"
            params = {
                "contactId": contact_id
            }
            
            # Add optional date parameter
            if inputs.get("date"):
                params["date"] = inputs["date"]
            
            # Make authenticated request to Xero API
            response = await context.fetch(
                url,
                method="GET",
                params=params,
                headers={
                    "Accept": "application/json",
                    "xero-tenant-id": tenant_id
                }
            )
            
            # Return raw API response
            if not response:
                raise ValueError("Empty response from Xero API")
            
            return response
                
        except Exception as e:
            raise Exception(f"Failed to fetch aged receivables report: {str(e)}")


@xero.action("get_balance_sheet")
@Xero.action("get_balance_sheet")
class GetBalanceSheetAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Fetches balance sheet report from Xero API
        """
        # Validate required inputs
        company_name = inputs.get("company_name")
        if not company_name:
            raise ValueError("company_name is required")
        tenant_id = inputs.get("tenant_id")
        if not tenant_id:
            raise ValueError("tenant_id is required")
        
        try:
            # Get tenant information by company name
            tenant_info = await get_tenant_by_company_name(context, company_name)
            tenant_id = tenant_info["tenant_id"]
            
            # Build URL with parameters
            url = "https://api.xero.com/api.xro/2.0/Reports/BalanceSheet"
            params = {}
            
            # Add optional date parameter
            if inputs.get("date"):
                params["date"] = inputs["date"]
            
            # Add optional periods parameter
            if inputs.get("periods"):
                params["periods"] = str(inputs["periods"])
            
            # Make authenticated request to Xero API
            response = await context.fetch(
                url,
                method="GET",
                params=params,
                headers={
                    "Accept": "application/json",
                    "xero-tenant-id": tenant_id
                }
            )
            
            # Return raw API response
            if not response:
                raise ValueError("Empty response from Xero API")
            
            return response
                
        except Exception as e:
            raise Exception(f"Failed to fetch balance sheet report: {str(e)}")


@xero.action("get_profit_and_loss")
@Xero.action("get_profit_and_loss")
class GetProfitAndLossAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Fetches profit and loss report from Xero API
        """
        # Validate required inputs
        company_name = inputs.get("company_name")
        if not company_name:
            raise ValueError("company_name is required")
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
            
            # Make authenticated request to Xero API
            response = await context.fetch(
                url,
                method="GET",
                params=params,
                headers={
                    "Accept": "application/json",
                    "xero-tenant-id": tenant_id
                }
            )
            
            # Return raw API response
            if not response:
                raise ValueError("Empty response from Xero API")
            
            return response
                
        except Exception as e:
            raise Exception(f"Failed to fetch profit and loss report: {str(e)}")


@xero.action("get_trial_balance")
@Xero.action("get_trial_balance")
class GetTrialBalanceAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        """
        Fetches trial balance report from Xero API
        """
        # Validate required inputs
        company_name = inputs.get("company_name")
        if not company_name:
            raise ValueError("company_name is required")
        tenant_id = inputs.get("tenant_id")
        if not tenant_id:
            raise ValueError("tenant_id is required")
        
        try:
            # Get tenant information by company name
            tenant_info = await get_tenant_by_company_name(context, company_name)
            tenant_id = tenant_info["tenant_id"]
            
            # Build URL with parameters
            url = "https://api.xero.com/api.xro/2.0/Reports/TrialBalance"
            params = {}
            
            # Add optional date parameter
            if inputs.get("date"):
                params["date"] = inputs["date"]
            
            # Add optional payments_only parameter
            if inputs.get("payments_only") is not None:
                params["paymentsOnly"] = str(inputs["payments_only"]).lower()
            
            # Make authenticated request to Xero API
            response = await context.fetch(
                url,
                method="GET",
                params=params,
                headers={
                    "Accept": "application/json",
                    "xero-tenant-id": tenant_id
                }
            )
            
            # Return raw API response
            if not response:
                raise ValueError("Empty response from Xero API")
            
            return response
                
        except Exception as e:
            raise Exception(f"Failed to fetch trial balance report: {str(e)}")
