from autohive_integrations_sdk import Integration, ExecutionContext, ActionHandler, ActionResult
from typing import Dict, Any, List
import os
from .client import IRDClient

# Load integration configuration
_config_path = os.path.join(os.path.dirname(__file__), 'config.json')
ird_income_tax = Integration.load(_config_path)

def get_client(context: ExecutionContext) -> IRDClient:
    """
    Factory to create an authenticated IRDClient from the context.
    """
    # Secrets management handles the token storage
    # In a real scenario, we would retrieve the user's stored access token
    # context.auth contains the auth info provided by the platform
    
    # Placeholder for certificate paths - these would likely be stored securely or 
    # part of the container environment
    cert_path = os.environ.get("IRD_CLIENT_CERT_PATH", "/etc/certs/client.crt")
    key_path = os.environ.get("IRD_CLIENT_KEY_PATH", "/etc/certs/client.key")
    
    # We assume the OAuth access token is available in credentials
    credentials = context.auth.get("credentials", {})
    access_token = credentials.get("access_token", "")
    
    return IRDClient(access_token, cert_path, key_path)

@ird_income_tax.action("retrieve_filing_obligations")
class RetrieveFilingObligations(ActionHandler):
    """
    Action to retrieve filing obligations from IRD.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        client = get_client(context)
        
        # Determine parameters
        ird_number = inputs["ird_number"]
        from_date = inputs["from_date"]
        to_date = inputs["to_date"]
        tax_type = inputs.get("tax_type", "INC")
        
        # Execute the operation (synchronously for now, as zeep is blocking)
        # In a full async environment, we might run this in an executor
        result = client.retrieve_filing_obligations(ird_number, from_date, to_date, tax_type)
        
        # Transform the result (Zeep returns objects) into a JSON-serializable dict
        # This is a simplified transformation
        obligations = []
        if result and hasattr(result, 'obligation'):
             for ob in result.obligation:
                 obligations.append({
                     "periodEndDate": str(ob.periodEndDate) if hasattr(ob, 'periodEndDate') else None,
                     "status": str(ob.status) if hasattr(ob, 'status') else None,
                     "dueDate": str(ob.dueDate) if hasattr(ob, 'dueDate') else None
                 })
        
        return ActionResult(data=obligations)

@ird_income_tax.action("retrieve_return")
class RetrieveReturn(ActionHandler):
    """
    Action to retrieve a specific return.
    """
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        client = get_client(context)
        
        ird_number = inputs["ird_number"]
        period_end_date = inputs["period_end_date"]
        tax_type = inputs.get("tax_type", "INC")
        
        result = client.retrieve_return(ird_number, period_end_date, tax_type)
        
        # Transform result
        data = {
            "returnId": str(result.returnId) if hasattr(result, 'returnId') else None,
            "status": str(result.status) if hasattr(result, 'status') else None,
            # Add more fields as needed from the XSD schema
        }
        
        return ActionResult(data=data)
