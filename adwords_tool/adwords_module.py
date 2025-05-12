import json
import proto
import logging
from datetime import datetime, timedelta

from google.ads.googleads.client import GoogleAdsClient
from autohive_integrations_sdk import ActionHandler, ExecutionContext # Assuming this is how ActionHandler is imported

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
    def __init__(self):
        # Assuming google-ads.yaml is in the same directory or accessible path
        # The SDK might provide a way to manage credentials/config files,
        # which would be better than hardcoding the path here.
        # For now, we keep the original loading mechanism.
        # This client initialization might be better done lazily if the action is called infrequently
        # or if the SDK manages the lifecycle of handlers.
        try:
            # You'll need to ensure 'google-ads.yaml' is packaged with your integration
            # and its path is correctly resolved here.
            self.client = GoogleAdsClient.load_from_storage("google-ads.yaml")
        except Exception as e:
            logger.error(f"Failed to load GoogleAdsClient from google-ads.yaml: {str(e)}")
            # This is a critical failure for the action. How to handle depends on SDK.
            # Raising an exception here might prevent the integration from loading.
            self.client = None # Or raise an error to be caught by the SDK

    def execute(self, context: ExecutionContext, action_inputs: dict):
        logger.info(f"Executing AdwordsCampaignAction with inputs: {action_inputs}")

        if not self.client:
            logger.error("GoogleAdsClient not initialized. Cannot execute action.")
            # The SDK should define how errors are returned.
            # This might involve raising a specific exception or returning an error structure.
            return {"error": "GoogleAdsClient not initialized. Check google-ads.yaml."}


        customer_id = action_inputs.get('customer_id')
        date_ranges_input = action_inputs.get('date_ranges', ["last_7_days", "prev_7_days"]) # Default from old lambda

        if not customer_id:
            logger.error("Customer ID is missing in action_inputs")
            return {"error": "Customer ID is required"} # Or raise appropriate error

        try:
            results = get_campaign_data_logic(self.client, customer_id, date_ranges_input)
            logger.info("Successfully retrieved campaign data.")
            return results # The SDK will handle serializing this to JSON if needed
        except ValueError as ve: # Catch specific errors like malformed date ranges
            logger.error(f"ValueError in AdwordsCampaignAction: {str(ve)}")
            return {"error": str(ve)}
        except Exception as e:
            logger.error(f"Exception in AdwordsCampaignAction: {str(e)}")
            # Depending on SDK, might need to return a specific error format or raise an SDK-specific exception
            return {"error": f"An unexpected error occurred: {str(e)}"}

# Example of how you might register this with the SDK (actual registration depends on the SDK)
# This part would typically go into the main integration file, like 'my_integration.py' from the template.
# from autohive_integrations_sdk import Integration
# my_integration = Integration.load() # Loads config.json
# my_integration.add_action_handler("get_adwords_campaign_data", AdwordsCampaignAction())
#
# If this file IS the entry point defined in config.json, then the SDK might auto-discover handlers
# or you might need a specific function for the SDK to call to initialize. 