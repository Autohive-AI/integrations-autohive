import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any

import proto
from autohive_integrations_sdk import ActionHandler, ExecutionContext, Integration
from google.ads.googleads.client import GoogleAdsClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(current_dir, "config.json")

adwords = Integration.load(config_file_path)

def micros_to_currency(micros):
    return float(micros) / 1000000 if micros is not None else 'N/A'

# Replace these with the real values
DEVELOPER_TOKEN = "DEVELOPER_TOKEN"
CLIENT_ID = "CLIENT_ID"
CLIENT_SECRET = "CLIENT_SECRET"

# TODO: Can likely make this be an input from the LLM, this was more a hack that was done in the old platform as LLMs didn't know what the time was
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
            datetime.strptime(start_str, '%Y-%m-%d')
            datetime.strptime(end_str, '%Y-%m-%d')
            start_date = start_str
            end_date = end_str
        except ValueError:
            logger.error(f"Unsupported or malformed date range: {range_name}")
            raise ValueError(f"Unsupported or malformed date range: {range_name}. Expected 'last_7_days', 'prev_7_days', or 'YYYY-MM-DD_YYYY-MM-DD'.")

    return {"start_date": start_date, "end_date": end_date}


# TODO: Likely need to make this a lot more generic, as this is more focused around what we ourselves used
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

# ---- Action Handlers ----
@adwords.action("get_campaign_data")
class AdwordsCampaignAction(ActionHandler):
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            refresh_token = context.auth.get("credentials", {}).get("refresh_token")
            
            if not refresh_token:
                logger.error("Refresh token is missing in auth credentials")
                return {"error": "Refresh token is required for authentication with Google Ads API"}

            # Get login_customer_id (Manager account) from inputs
            login_customer_id = inputs.get('login_customer_id')
            
            # Get customer_id (Account to query) from inputs
            customer_id = inputs.get('customer_id')
            
            if not login_customer_id:
                logger.error("Manager Account ID (login_customer_id) is missing in action_inputs")
                return {"error": "Manager Account ID (login_customer_id) is required"}
                
            if not customer_id:
                logger.error("Customer ID is missing in action_inputs")
                return {"error": "Customer ID is required"}

            credentials = {
                "developer_token": DEVELOPER_TOKEN,
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "refresh_token": refresh_token,
                "login_customer_id": login_customer_id,
                "use_proto_plus": True
            }

            client = GoogleAdsClient.load_from_dict(credentials)

            print("\nGoogle Ads API Test Results:")

        except Exception as e:
            logger.exception(f"Failed to initialize GoogleAdsClient: {str(e)}")
            return {"error": f"Failed to initialize Google Ads client: {str(e)}"}

        date_ranges_input = inputs.get('date_ranges', ["last_7_days", "prev_7_days"])

        try:
            results = get_campaign_data_logic(client, customer_id, date_ranges_input)
            logger.info("Successfully retrieved campaign data.")
            return results
        except ValueError as ve:
            logger.error(f"ValueError in AdwordsCampaignAction: {str(ve)}")
            return {"error": str(ve)}
        except Exception as e:
            logger.exception(f"Exception during campaign data retrieval: {str(e)}")
            return {"error": f"An unexpected error occurred during data retrieval: {str(e)}"}
