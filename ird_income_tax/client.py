import os
import requests
from zeep import Client, Transport, xsd
from zeep.plugins import HistoryPlugin
from typing import Dict, Any, Optional

class IRDClient:
    # This should be the actual URL for the IRD Gateway Service WSDL
    # For now, we'll use a placeholder or the Production/Test endpoint
    WSDL_URL = os.environ.get("IRD_WSDL_URL", "https://services.ird.govt.nz/gateway/returns/v2?wsdl")
    
    def __init__(self, access_token: str, cert_path: str, key_path: str):
        self.access_token = access_token
        self.cert_path = cert_path
        self.key_path = key_path
        self.history = HistoryPlugin()
        self._client = self._init_client()

    def _init_client(self) -> Client:
        session = requests.Session()
        
        # Mutual TLS
        if os.path.exists(self.cert_path) and os.path.exists(self.key_path):
            session.cert = (self.cert_path, self.key_path)
        
        # OAuth 2.0 Header
        session.headers["Authorization"] = f"Bearer {self.access_token}"
        
        transport = Transport(session=session)
        
        # We might need to point to local XSDs if WSDL is not available or for strict validation
        # For now, we rely on the WSDL
        client = Client(
            wsdl=self.WSDL_URL, 
            transport=transport,
            plugins=[self.history]
        )
        return client

    def retrieve_filing_obligations(self, ird_number: str, from_date: str, to_date: str, tax_type: str = "INC"):
        """
        Calls the RetrieveFilingObligations operation.
        """
        # The structure here depends heavily on the exact WSDL/XSD structure.
        # This is a generic representation based on standard IRD patterns.
        
        request_data = {
            "Audio": {
                "id": ird_number,
                "idType": "IRD"
            },
            "PeriodFrom": from_date,
            "PeriodTo": to_date,
            "RevenueType": tax_type
        }
        
        # Assuming the service has a method named 'RetrieveFilingObligations'
        # In reality, it might be nested under a specific service port.
        response = self._client.service.RetrieveFilingObligations(**request_data)
        return response

    def retrieve_return(self, ird_number: str, period_end_date: str, tax_type: str = "INC"):
        """
        Calls the RetrieveReturn operation.
        """
        request_data = {
            "Audio": {
                "id": ird_number,
                "idType": "IRD"
            },
            "PeriodEndDate": period_end_date,
            "RevenueType": tax_type
        }
        
        response = self._client.service.RetrieveReturn(**request_data)
        return response
