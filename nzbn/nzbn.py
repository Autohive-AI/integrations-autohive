from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler, ActionResult
)
from typing import Dict, Any, List, Optional

nzbn = Integration.load()

# API base URL (production)
NZBN_API_BASE_URL = "https://api.business.govt.nz/gateway/nzbn/v5"


def get_base_url() -> str:
    return NZBN_API_BASE_URL


def get_headers() -> Dict[str, str]:
    return {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }


def validate_nzbn(nzbn_number: str) -> str:
    nzbn_number = str(nzbn_number).strip()
    if len(nzbn_number) != 13 or not nzbn_number.isdigit():
        raise ValueError("NZBN must be a 13-digit number")
    return nzbn_number


def check_api_error(response: Any) -> None:
    if isinstance(response, dict) and response.get("errorCode"):
        raise ValueError(f"API Error: {response.get('errorDescription', 'Unknown error')}")


def transform_search_entity(entity: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "nzbn": entity.get("nzbn"),
        "entity_name": entity.get("entityName"),
        "entity_type_code": entity.get("entityTypeCode"),
        "entity_type_description": entity.get("entityTypeDescription"),
        "entity_status_code": entity.get("entityStatusCode"),
        "entity_status_description": entity.get("entityStatusDescription"),
        "registration_date": entity.get("registrationDate"),
        "source_register_unique_id": entity.get("sourceRegisterUniqueId"),
        "trading_names": [
            {
                "name": tn.get("name"),
                "start_date": tn.get("startDate"),
                "end_date": tn.get("endDate")
            }
            for tn in entity.get("tradingNames", [])
        ],
        "classifications": [
            {
                "code": c.get("classificationCode"),
                "description": c.get("classificationDescription")
            }
            for c in entity.get("classifications", [])
        ],
        "previous_entity_names": entity.get("previousEntityNames", [])
    }


def transform_address(addr: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "unique_identifier": addr.get("uniqueIdentifier"),
        "address_type": addr.get("addressType"),
        "care_of": addr.get("careOf"),
        "address_line1": addr.get("address1"),
        "address_line2": addr.get("address2"),
        "address_line3": addr.get("address3"),
        "address_line4": addr.get("address4"),
        "city": addr.get("city"),
        "region": addr.get("region"),
        "postcode": addr.get("postCode"),
        "country_code": addr.get("countryCode"),
        "start_date": addr.get("startDate"),
        "end_date": addr.get("endDate")
    }


def transform_role(role: Dict[str, Any]) -> Dict[str, Any]:
    role_data = {
        "unique_identifier": role.get("uniqueIdentifier"),
        "role_type": role.get("roleType"),
        "role_status": role.get("roleStatus"),
        "start_date": role.get("startDate"),
        "end_date": role.get("endDate"),
        "role_holder_type": role.get("roleHolderType"),
        "consent_received": role.get("consentReceived")
    }
    
    if role.get("rolePerson"):
        person = role["rolePerson"]
        role_data["first_name"] = person.get("firstName")
        role_data["middle_names"] = person.get("middleNames")
        role_data["last_name"] = person.get("lastName")
        role_data["person_name"] = " ".join(filter(None, [
            person.get("firstName"),
            person.get("middleNames"),
            person.get("lastName")
        ]))
    
    if role.get("roleEntity"):
        entity_holder = role["roleEntity"]
        role_data["entity_name"] = entity_holder.get("entityName")
        role_data["entity_nzbn"] = entity_holder.get("nzbn")
    
    if role.get("addresses"):
        role_data["addresses"] = [transform_address(a) for a in role["addresses"]]
    
    return role_data


def transform_entity_detail(entity: Dict[str, Any]) -> Dict[str, Any]:
    result = {
        "nzbn": entity.get("nzbn"),
        "entity_name": entity.get("entityName"),
        "entity_type_code": entity.get("entityTypeCode"),
        "entity_type_description": entity.get("entityTypeDescription"),
        "entity_status_code": entity.get("entityStatusCode"),
        "entity_status_description": entity.get("entityStatusDescription"),
        "registration_date": entity.get("registrationDate"),
        "source_register": entity.get("sourceRegister"),
        "source_register_unique_id": entity.get("sourceRegisterUniqueId"),
        "trading_names": [],
        "classifications": [],
        "addresses": [],
        "phone_numbers": [],
        "email_addresses": [],
        "websites": [],
        "gst_numbers": [],
        "roles": [],
        "trading_areas": []
    }
    
    for tn in entity.get("tradingNames", []):
        result["trading_names"].append({
            "unique_identifier": tn.get("uniqueIdentifier"),
            "name": tn.get("name"),
            "start_date": tn.get("startDate"),
            "end_date": tn.get("endDate")
        })
    
    for c in entity.get("classifications", []):
        result["classifications"].append({
            "unique_identifier": c.get("uniqueIdentifier"),
            "code": c.get("classificationCode"),
            "description": c.get("classificationDescription")
        })
    
    for addr in entity.get("addresses", []):
        result["addresses"].append(transform_address(addr))
    
    for phone in entity.get("phoneNumbers", []):
        result["phone_numbers"].append({
            "unique_identifier": phone.get("uniqueIdentifier"),
            "phone_type": phone.get("phoneType"),
            "phone_country_code": phone.get("phoneCountryCode"),
            "phone_area_code": phone.get("phoneAreaCode"),
            "phone_number": phone.get("phoneNumber"),
            "start_date": phone.get("startDate"),
            "end_date": phone.get("endDate")
        })
    
    for email in entity.get("emailAddresses", []):
        result["email_addresses"].append({
            "unique_identifier": email.get("uniqueIdentifier"),
            "email_type": email.get("emailAddressType"),
            "email": email.get("emailAddress"),
            "start_date": email.get("startDate"),
            "end_date": email.get("endDate")
        })
    
    for website in entity.get("websites", []):
        result["websites"].append({
            "unique_identifier": website.get("uniqueIdentifier"),
            "url": website.get("url"),
            "website_type": website.get("websiteType"),
            "start_date": website.get("startDate"),
            "end_date": website.get("endDate")
        })
    
    for gst in entity.get("gstNumbers", []):
        result["gst_numbers"].append({
            "unique_identifier": gst.get("uniqueIdentifier"),
            "gst_number": gst.get("gstNumber"),
            "start_date": gst.get("startDate"),
            "end_date": gst.get("endDate")
        })
    
    for role in entity.get("roles", []):
        result["roles"].append(transform_role(role))
    
    for area in entity.get("tradingAreas", []):
        result["trading_areas"].append({
            "unique_identifier": area.get("uniqueIdentifier"),
            "trading_area_code": area.get("tradingAreaCode"),
            "trading_area_description": area.get("tradingAreaDescription"),
            "start_date": area.get("startDate"),
            "end_date": area.get("endDate")
        })
    
    return result


async def make_api_request(context: ExecutionContext, url: str, params: dict = None):
    """Make an authenticated API request. Platform OAuth handles authentication automatically."""
    headers = get_headers()
    
    response = await context.fetch(
        url,
        method="GET",
        headers=headers,
        params=params
    )
    
    check_api_error(response)
    return response


@nzbn.action("search_entities")
class SearchEntitiesAction(ActionHandler):
    """Search the NZBN directory by name, trading name, NZBN, or company number."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        search_term = inputs.get("search_term")
        if not search_term:
            raise ValueError("search_term is required")
        
        base_url = get_base_url()
        
        params = {"search-term": search_term}
        
        if inputs.get("entity_status"):
            params["entity-status"] = inputs["entity_status"]
        if inputs.get("entity_type"):
            params["entity-type"] = inputs["entity_type"]
        if inputs.get("industry_code"):
            params["industry-code"] = inputs["industry_code"]
        if inputs.get("page") is not None:
            params["page"] = inputs["page"]
        if inputs.get("page_size"):
            params["page-size"] = inputs["page_size"]
        
        try:
            response = await make_api_request(context, f"{base_url}/entities", params)
            
            items = response.get("items", [])
            transformed_items = [transform_search_entity(item) for item in items]
            
            return ActionResult(
                data={
                    "total_items": response.get("totalItems", 0),
                    "page": response.get("page", 0),
                    "page_size": response.get("pageSize", 0),
                    "items": transformed_items
                },
                cost_usd=0.0
            )
            
        except Exception as e:
            raise Exception(f"Failed to search NZBN entities: {str(e)}")


@nzbn.action("get_entity")
class GetEntityAction(ActionHandler):
    """Get full details about a specific business entity by NZBN."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        nzbn_number = validate_nzbn(inputs.get("nzbn", ""))
        base_url = get_base_url()
        
        try:
            response = await make_api_request(context, f"{base_url}/entities/{nzbn_number}")
            return ActionResult(
                data=transform_entity_detail(response),
                cost_usd=0.0
            )
        except Exception as e:
            raise Exception(f"Failed to get NZBN entity details: {str(e)}")


@nzbn.action("get_entity_changes")
class GetEntityChangesAction(ActionHandler):
    """Search for entities that have been updated within a time period."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        change_event_type = inputs.get("change_event_type")
        if not change_event_type:
            raise ValueError("change_event_type is required")
        
        base_url = get_base_url()
        
        params = {"change-event-type": change_event_type}
        
        if inputs.get("start_date"):
            params["start-date"] = inputs["start_date"]
        if inputs.get("end_date"):
            params["end-date"] = inputs["end_date"]
        if inputs.get("entity_type"):
            params["entity-type"] = inputs["entity_type"]
        if inputs.get("page") is not None:
            params["page"] = inputs["page"]
        if inputs.get("page_size"):
            params["page-size"] = inputs["page_size"]
        
        try:
            response = await make_api_request(context, f"{base_url}/entities/changes", params)
            
            return ActionResult(
                data={
                    "total_items": response.get("totalItems", 0),
                    "page": response.get("page", 0),
                    "page_size": response.get("pageSize", 0),
                    "items": response.get("items", [])
                },
                cost_usd=0.0
            )
        except Exception as e:
            raise Exception(f"Failed to get NZBN entity changes: {str(e)}")


@nzbn.action("get_entity_roles")
class GetEntityRolesAction(ActionHandler):
    """Get roles (directors, shareholders, partners) for a business entity."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        nzbn_number = validate_nzbn(inputs.get("nzbn", ""))
        base_url = get_base_url()
        
        try:
            response = await make_api_request(context, f"{base_url}/entities/{nzbn_number}/roles")
            
            items = response.get("items", []) if isinstance(response, dict) else response
            roles = [transform_role(role) for role in items]
            
            return ActionResult(
                data={
                    "nzbn": nzbn_number,
                    "roles": roles
                },
                cost_usd=0.0
            )
        except Exception as e:
            raise Exception(f"Failed to get NZBN entity roles: {str(e)}")


@nzbn.action("get_entity_addresses")
class GetEntityAddressesAction(ActionHandler):
    """Get addresses for a business entity."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        nzbn_number = validate_nzbn(inputs.get("nzbn", ""))
        base_url = get_base_url()
        
        params = {}
        if inputs.get("address_type"):
            params["address-type"] = inputs["address_type"]
        
        try:
            response = await make_api_request(
                context, 
                f"{base_url}/entities/{nzbn_number}/addresses",
                params if params else None
            )
            
            items = response.get("items", []) if isinstance(response, dict) else response
            addresses = [transform_address(addr) for addr in items]
            
            return ActionResult(
                data={
                    "nzbn": nzbn_number,
                    "addresses": addresses
                },
                cost_usd=0.0
            )
        except Exception as e:
            raise Exception(f"Failed to get NZBN entity addresses: {str(e)}")


@nzbn.action("get_entity_trading_names")
class GetEntityTradingNamesAction(ActionHandler):
    """Get trading names for a business entity."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        nzbn_number = validate_nzbn(inputs.get("nzbn", ""))
        base_url = get_base_url()
        
        try:
            response = await make_api_request(context, f"{base_url}/entities/{nzbn_number}/trading-names")
            
            items = response.get("items", []) if isinstance(response, dict) else response
            trading_names = [
                {
                    "unique_identifier": tn.get("uniqueIdentifier"),
                    "name": tn.get("name"),
                    "start_date": tn.get("startDate"),
                    "end_date": tn.get("endDate")
                }
                for tn in items
            ]
            
            return ActionResult(
                data={
                    "nzbn": nzbn_number,
                    "trading_names": trading_names
                },
                cost_usd=0.0
            )
        except Exception as e:
            raise Exception(f"Failed to get NZBN entity trading names: {str(e)}")


@nzbn.action("get_entity_phone_numbers")
class GetEntityPhoneNumbersAction(ActionHandler):
    """Get phone numbers for a business entity."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        nzbn_number = validate_nzbn(inputs.get("nzbn", ""))
        base_url = get_base_url()
        
        try:
            response = await make_api_request(context, f"{base_url}/entities/{nzbn_number}/phone-numbers")
            
            items = response.get("items", []) if isinstance(response, dict) else response
            phone_numbers = [
                {
                    "unique_identifier": p.get("uniqueIdentifier"),
                    "phone_type": p.get("phoneType"),
                    "phone_country_code": p.get("phoneCountryCode"),
                    "phone_area_code": p.get("phoneAreaCode"),
                    "phone_number": p.get("phoneNumber"),
                    "start_date": p.get("startDate"),
                    "end_date": p.get("endDate")
                }
                for p in items
            ]
            
            return ActionResult(
                data={
                    "nzbn": nzbn_number,
                    "phone_numbers": phone_numbers
                },
                cost_usd=0.0
            )
        except Exception as e:
            raise Exception(f"Failed to get NZBN entity phone numbers: {str(e)}")


@nzbn.action("get_entity_email_addresses")
class GetEntityEmailAddressesAction(ActionHandler):
    """Get email addresses for a business entity."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        nzbn_number = validate_nzbn(inputs.get("nzbn", ""))
        base_url = get_base_url()
        
        try:
            response = await make_api_request(context, f"{base_url}/entities/{nzbn_number}/email-addresses")
            
            items = response.get("items", []) if isinstance(response, dict) else response
            email_addresses = [
                {
                    "unique_identifier": e.get("uniqueIdentifier"),
                    "email_type": e.get("emailAddressType"),
                    "email": e.get("emailAddress"),
                    "start_date": e.get("startDate"),
                    "end_date": e.get("endDate")
                }
                for e in items
            ]
            
            return ActionResult(
                data={
                    "nzbn": nzbn_number,
                    "email_addresses": email_addresses
                },
                cost_usd=0.0
            )
        except Exception as e:
            raise Exception(f"Failed to get NZBN entity email addresses: {str(e)}")


@nzbn.action("get_entity_websites")
class GetEntityWebsitesAction(ActionHandler):
    """Get websites for a business entity."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        nzbn_number = validate_nzbn(inputs.get("nzbn", ""))
        base_url = get_base_url()
        
        try:
            response = await make_api_request(context, f"{base_url}/entities/{nzbn_number}/websites")
            
            items = response.get("items", []) if isinstance(response, dict) else response
            websites = [
                {
                    "unique_identifier": w.get("uniqueIdentifier"),
                    "url": w.get("url"),
                    "website_type": w.get("websiteType"),
                    "start_date": w.get("startDate"),
                    "end_date": w.get("endDate")
                }
                for w in items
            ]
            
            return ActionResult(
                data={
                    "nzbn": nzbn_number,
                    "websites": websites
                },
                cost_usd=0.0
            )
        except Exception as e:
            raise Exception(f"Failed to get NZBN entity websites: {str(e)}")


@nzbn.action("get_entity_gst_numbers")
class GetEntityGstNumbersAction(ActionHandler):
    """Get GST registration numbers for a business entity."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        nzbn_number = validate_nzbn(inputs.get("nzbn", ""))
        base_url = get_base_url()
        
        try:
            response = await make_api_request(context, f"{base_url}/entities/{nzbn_number}/gst-numbers")
            
            items = response.get("items", []) if isinstance(response, dict) else response
            gst_numbers = [
                {
                    "unique_identifier": g.get("uniqueIdentifier"),
                    "gst_number": g.get("gstNumber"),
                    "start_date": g.get("startDate"),
                    "end_date": g.get("endDate")
                }
                for g in items
            ]
            
            return ActionResult(
                data={
                    "nzbn": nzbn_number,
                    "gst_numbers": gst_numbers
                },
                cost_usd=0.0
            )
        except Exception as e:
            raise Exception(f"Failed to get NZBN entity GST numbers: {str(e)}")


@nzbn.action("get_entity_industry_classifications")
class GetEntityIndustryClassificationsAction(ActionHandler):
    """Get BIC industry classifications for a business entity."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        nzbn_number = validate_nzbn(inputs.get("nzbn", ""))
        base_url = get_base_url()
        
        try:
            response = await make_api_request(context, f"{base_url}/entities/{nzbn_number}/industry-classifications")
            
            items = response.get("items", []) if isinstance(response, dict) else response
            classifications = [
                {
                    "unique_identifier": c.get("uniqueIdentifier"),
                    "code": c.get("classificationCode"),
                    "description": c.get("classificationDescription"),
                    "start_date": c.get("startDate"),
                    "end_date": c.get("endDate")
                }
                for c in items
            ]
            
            return ActionResult(
                data={
                    "nzbn": nzbn_number,
                    "classifications": classifications
                },
                cost_usd=0.0
            )
        except Exception as e:
            raise Exception(f"Failed to get NZBN entity industry classifications: {str(e)}")


@nzbn.action("get_entity_company_details")
class GetEntityCompanyDetailsAction(ActionHandler):
    """Get company-specific details (for NZ companies only)."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        nzbn_number = validate_nzbn(inputs.get("nzbn", ""))
        base_url = get_base_url()
        
        try:
            response = await make_api_request(context, f"{base_url}/entities/{nzbn_number}/company-details")
            
            return ActionResult(
                data={
                    "nzbn": nzbn_number,
                    "company_details": {
                        "constitution_filed": response.get("constitutionFiled"),
                        "annual_return_filing_month": response.get("annualReturnFilingMonth"),
                        "annual_return_last_filed_date": response.get("annualReturnLastFiledDate"),
                        "country_of_origin": response.get("countryOfOrigin"),
                        "extensive_shareholders": response.get("extensiveShareholders"),
                        "ultimate_holding_company": response.get("ultimateHoldingCompany")
                    }
                },
                cost_usd=0.0
            )
        except Exception as e:
            raise Exception(f"Failed to get NZBN company details: {str(e)}")


@nzbn.action("get_entity_history")
class GetEntityHistoryAction(ActionHandler):
    """Get change history for a business entity."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        nzbn_number = validate_nzbn(inputs.get("nzbn", ""))
        base_url = get_base_url()
        
        try:
            response = await make_api_request(context, f"{base_url}/entities/{nzbn_number}/history")
            
            items = response.get("items", []) if isinstance(response, dict) else response
            
            return ActionResult(
                data={
                    "nzbn": nzbn_number,
                    "history": items
                },
                cost_usd=0.0
            )
        except Exception as e:
            raise Exception(f"Failed to get NZBN entity history: {str(e)}")


@nzbn.action("get_entity_trading_areas")
class GetEntityTradingAreasAction(ActionHandler):
    """Get geographic trading areas for a business entity."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> ActionResult:
        nzbn_number = validate_nzbn(inputs.get("nzbn", ""))
        base_url = get_base_url()
        
        try:
            response = await make_api_request(context, f"{base_url}/entities/{nzbn_number}/trading-areas")
            
            items = response.get("items", []) if isinstance(response, dict) else response
            trading_areas = [
                {
                    "unique_identifier": a.get("uniqueIdentifier"),
                    "trading_area_code": a.get("tradingAreaCode"),
                    "trading_area_description": a.get("tradingAreaDescription"),
                    "start_date": a.get("startDate"),
                    "end_date": a.get("endDate")
                }
                for a in items
            ]
            
            return ActionResult(
                data={
                    "nzbn": nzbn_number,
                    "trading_areas": trading_areas
                },
                cost_usd=0.0
            )
        except Exception as e:
            raise Exception(f"Failed to get NZBN entity trading areas: {str(e)}")
