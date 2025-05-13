import json
import proto
import logging
from datetime import datetime, timedelta

from google.ads.googleads.client import GoogleAdsClient
from autohive_integrations_sdk import ActionHandler, ExecutionContext
from autohive_integrations_sdk.auth import get_integration_auth # Assuming this is the way to get auth
from autohive_integrations_sdk.config import get_integration_config # Assuming this is the way to get config

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def micros_to_currency(micros):
    return float(micros) / 1000000 if micros is not None else 'N/A'


def parse_date_range(range_name):
    now = datetime.now()
    if range_name == "last_7_days":
        start_date = (now - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = now.strftime('%Y-%m-%d')
    elif range_name == "prev_7_days":
        start_date = (now - timedelta(days=14)).strftime('%Y-%m-%d')
        end_date = (now - timedelta(days=7)).strftime('%Y-%m-%d')
    else:
        # For custom date ranges, expect "YYYY-MM-DD_YYYY-MM-DD"
        try:
            start_str, end_str = range_name.split('_')
            datetime.strptime(start_str, '%Y-%m-%d') # Validate format
            datetime.strptime(end_str, '%Y-%m-%d')   # Validate format
            start_date = start_str
            end_date = end_str
        except ValueError:
            logger.error(f"Unsupported or malformed date range: {range_name}")
            raise ValueError(f"Unsupported or malformed date range: {range_name}. Expected 'last_7_days', 'prev_7_days', or 'YYYY-MM-DD_YYYY-MM-DD'.")

    return {"start_date": start_date, "end_date": end_date}


def get_campaign_data_logic(client, customer_id, date_ranges_input):
    ga_service = client.get_service("GoogleAdsService")

    query_template = """
    SELECT
        campaign.id,
        campaign.status,
        campaign.name,
        campaign_budget.amount_micros,
        customer.currency_code,
        campaign.bidding_strategy_system_status,
        campaign.optimization_score,
        customer.descriptive_name,
        campaign.advertising_channel_type,
        metrics.average_cpv,
        metrics.interactions,
        metrics.interaction_rate,
        metrics.average_cost,
        metrics.cost_micros,
        metrics.impressions,
        campaign.bidding_strategy_type,
        metrics.clicks,
        metrics.conversions_value,
        metrics.cost_per_all_conversions,
        metrics.all_conversions,
        metrics.average_cpc,
        metrics.cost_per_conversion
    FROM campaign
    WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND campaign.status = 'ENABLED'
        AND campaign.bidding_strategy_system_status != 'PAUSED'
    """

    all_results = []
    
    # Parse date ranges from input strings to dicts
    parsed_date_ranges = []
    if isinstance(date_ranges_input, str): # Handle single string date range
        date_ranges_input = [date_ranges_input]
    
    for dr_input in date_ranges_input:
        parsed_date_ranges.append(parse_date_range(dr_input))

    for date_range in parsed_date_ranges:
        query = query_template.format(start_date=date_range['start_date'], end_date=date_range['end_date'])
        
        # It's good practice to wrap API calls in try-except blocks
        try:
            response = ga_service.search(customer_id=customer_id, query=query)
        except Exception as e:
            logger.error(f"Error during Google Ads API call for date range {date_range}: {str(e)}")
            # Depending on requirements, you might want to skip this range or stop entirely
            # For now, let's add a placeholder for this error in the results.
            all_results.append({
                'date_range': f"{date_range['start_date']} to {date_range['end_date']}",
                'error': f"Failed to retrieve data: {str(e)}",
                'data': []
            })
            continue # Move to the next date range


        date_range_result = {
            'date_range': f"{date_range['start_date']} to {date_range['end_date']}",
            'data': []
        }

        for row in response:
            row_dict = proto.Message.to_dict(row, use_integers_for_enums=False)

            campaign = row_dict.get('campaign', {})
            metrics = row_dict.get('metrics', {})
            customer = row_dict.get('customer', {})
            budget = row_dict.get('campaign_budget', {})

            conversions_value = metrics.get('conversions_value', 0.0) # Ensure float for division
            cost_micros = metrics.get('cost_micros', 1) 
            cost = micros_to_currency(cost_micros)
            
            # Ensure cost is a number and not 'N/A' before division
            roas = 0
            if isinstance(cost, (int, float)) and cost != 0:
                 roas = conversions_value / cost
            elif cost == 'N/A' or cost == 0: # if cost is N/A or 0, ROAS is 0 or undefined. Let's use 0.
                 roas = 0


            data = {
                "Campaign ID" : campaign.get('id', 'N/A'),
                "Campaign status": campaign.get('status', 'N/A'),
                "Campaign": campaign.get('name', 'N/A'),
                # "Budget name": 'N/A', # This was N/A in original, consider if it can be fetched
                "Currency code": customer.get('currency_code', 'N/A'),
                "Budget": micros_to_currency(budget.get('amount_micros')), # Removed default 0
                # "Budget type": 'N/A', # This was N/A in original
                "Status": campaign.get('bidding_strategy_system_status', 'N/A'),
                "Optimization score": campaign.get('optimization_score', 'N/A'),
                "Account": customer.get('descriptive_name', 'N/A'),
                "Campaign type": campaign.get('advertising_channel_type', 'N/A'),
                "Avg. CPV": micros_to_currency(metrics.get('average_cpv')),
                "Interactions": metrics.get('interactions', 'N/A'),
                "Interaction rate": metrics.get('interaction_rate', 'N/A'), # Convert to percentage if it's a decimal
                "Avg. cost": micros_to_currency(metrics.get('average_cost')),
                "Cost": cost, # Use the calculated cost
                "Impr.": metrics.get('impressions', 'N/A'),
                "Bid strategy type": campaign.get('bidding_strategy_type', 'N/A'),
                "Clicks": metrics.get('clicks', 'N/A'),
                "Conv. value": conversions_value, # Use the float value
                "Conv. value / cost": roas,
                "Conversions": metrics.get('all_conversions', 'N/A'),
                "Avg. CPC": micros_to_currency(metrics.get('average_cpc')),
                "Cost / conv.": micros_to_currency(metrics.get('cost_per_conversion'))
            }
            date_range_result['data'].append(data)
        all_results.append(date_range_result)
    return all_results


class AdwordsCampaignAction(ActionHandler):
    # Remove __init__ or leave it empty if base class requires it
    # def __init__(self):
    #     pass

    def execute(self, context: ExecutionContext, action_inputs: dict):
        logger.info(f"Executing AdwordsCampaignAction with inputs: {action_inputs}")

        try:
            # Fetch platform auth credentials
            # Adapt this based on actual SDK methods. Assumes dictionary-like return.
            auth_details = get_integration_auth()
            if not auth_details or 'refresh_token' not in auth_details or 'client_id' not in auth_details or 'client_secret' not in auth_details:
                logger.error("Failed to retrieve valid authentication details from platform.")
                return {"error": "Platform authentication failed or incomplete."}

            # Fetch integration configuration
            # Adapt this based on actual SDK methods. Assumes dictionary-like return.
            config = get_integration_config()
            developer_token = config.get('developer_token')
            login_customer_id = config.get('login_customer_id') # Optional

            if not developer_token:
                logger.error("Developer Token is missing in integration configuration.")
                return {"error": "Developer Token configuration is missing."}

            # Construct credentials dictionary for GoogleAdsClient
            credentials = {
                "developer_token": developer_token,
                "client_id": auth_details['client_id'],
                "client_secret": auth_details['client_secret'],
                "refresh_token": auth_details['refresh_token'],
                "use_proto_plus": True # Keep this for better usability
            }

            # Add login_customer_id if provided in config
            if login_customer_id:
                credentials["login_customer_id"] = login_customer_id

            # Initialize the Google Ads client using the fetched credentials
            client = GoogleAdsClient.load_from_dict(credentials)

        except Exception as e:
            logger.exception(f"Failed to initialize GoogleAdsClient: {str(e)}")
            return {"error": f"Failed to initialize Google Ads client: {str(e)}"}

        customer_id = action_inputs.get('customer_id')
        # Default date ranges can be defined in config.json action schema if needed
        date_ranges_input = action_inputs.get('date_ranges', ["last_7_days", "prev_7_days"])

        if not customer_id:
            logger.error("Customer ID is missing in action_inputs")
            return {"error": "Customer ID is required"}

        try:
            # Pass the initialized client to the logic function
            results = get_campaign_data_logic(client, customer_id, date_ranges_input)
            logger.info("Successfully retrieved campaign data.")
            return results
        except ValueError as ve:
            logger.error(f"ValueError in AdwordsCampaignAction: {str(ve)}")
            return {"error": str(ve)}
        except Exception as e:
            logger.exception(f"Exception during campaign data retrieval: {str(e)}")
            return {"error": f"An unexpected error occurred during data retrieval: {str(e)}"}

# Example of how you might register this with the SDK (actual registration depends on the SDK)
# This part would typically go into the main integration file, like 'my_integration.py' from the template.
# from autohive_integrations_sdk import Integration
# my_integration = Integration.load() # Loads config.json
# my_integration.add_action_handler("get_adwords_campaign_data", AdwordsCampaignAction())
#
# If this file IS the entry point defined in config.json, then the SDK might auto-discover handlers
# or you might need a specific function for the SDK to call to initialize. 