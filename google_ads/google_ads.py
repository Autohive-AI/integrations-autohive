import os

import logging
# Configure logging for debugging and monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Setup environment variables and throw if they don't exist
from dotenv import load_dotenv
load_dotenv()
try:
    # Google Ads API credentials from environment variables
    DEVELOPER_TOKEN = os.environ["ADWORDS_DEVELOPER_TOKEN"]
    CLIENT_ID = os.environ["ADWORDS_CLIENT_ID"]
    CLIENT_SECRET = os.environ["ADWORDS_CLIENT_SECRET"]
except KeyError as e:
    logger.error(f"Error loading environment variables: {str(e)}")
    raise

from datetime import datetime, timedelta
from typing import Dict, Any
from enum import Enum

import proto
from autohive_integrations_sdk import ActionHandler, ExecutionContext, Integration, ActionResult
from google.ads.googleads.client import GoogleAdsClient

# Load integration configuration
google_ads = Integration.load()

class AdType(Enum):
    RESPONSIVE_SEARCH_AD = 'RESPONSIVE_SEARCH_AD'
    EXPANDED_TEXT_AD = 'EXPANDED_TEXT_AD'

def micros_to_currency(micros):
    """Convert Google Ads API micros (millionths) to standard currency format."""
    return float(micros) / 1000000 if micros is not None else 'N/A'

def _get_ad_text_assets(ad_data_from_row: Dict[str, Any]) -> Dict[str, list]:
    """Extracts headlines and descriptions from the ad_data part of a Google Ads API row."""
    headlines = []
    descriptions = []
    ad_type = ad_data_from_row.get('type', 'N/A')

    # Extract text assets based on ad type
    if ad_type == AdType.RESPONSIVE_SEARCH_AD.value:
        rsa_info = ad_data_from_row.get('responsive_search_ad', {})
        headlines.extend([h.get('text', '') for h in rsa_info.get('headlines', []) if h.get('text')])
        descriptions.extend([d.get('text', '') for d in rsa_info.get('descriptions', []) if d.get('text')])
    elif ad_type == AdType.EXPANDED_TEXT_AD.value:
        eta_info = ad_data_from_row.get('expanded_text_ad', {})
        # Extract headline parts (up to 3 for expanded text ads)
        for part in ['headline_part1', 'headline_part2', 'headline_part3']:
            if eta_info.get(part):
                headlines.append(eta_info.get(part))
        # Extract description parts (up to 2 for expanded text ads)
        for part in ['description', 'description2']:
            if eta_info.get(part):
                descriptions.append(eta_info.get(part))

    return {"headlines": headlines, "descriptions": descriptions}

def _calculate_safe_rate(numerator_raw, denominator_raw, default_numerator=0.0, default_denominator=0.0):
    """Safely calculates a rate (e.g., conversion rate), handling potential non-numeric inputs."""
    try:
        numerator = float(numerator_raw)
    except (ValueError, TypeError):
        numerator = default_numerator
    try:
        denominator = float(denominator_raw)
    except (ValueError, TypeError):
        denominator = default_denominator
    
    # Avoid division by zero
    if denominator > 0:
        return numerator / denominator
    return 0.0

def _initialize_ad_group_data(row: Dict[str, Any]) -> Dict[str, Any]:
    """Initializes the data structure for a new ad group."""
    return {
        "ad_group_id": row.get('ad_group', {}).get('id', 'N/A'),
        "ad_group_name": row.get('ad_group', {}).get('name', 'N/A'),
        "ad_group_status": row.get('ad_group', {}).get('status', 'N/A'),
        "ad_group_type": row.get('ad_group', {}).get('type', 'N/A'),
        "campaign_id": row.get('campaign', {}).get('id', 'N/A'),
        "campaign_name": row.get('campaign', {}).get('name', 'N/A'),
        "campaign_bidding_strategy_type": row.get('campaign', {}).get('bidding_strategy_type', 'N/A'),
        "ads": {}  # Ads will be keyed by ad_id here
    }

def _initialize_ad_data(row: Dict[str, Any], ad_id: str) -> Dict[str, Any]:
    """Initializes the data structure for a new ad, including text assets and base metrics."""
    ad_column_data = row.get('ad_group_ad', {}).get('ad', {})
    ad_metrics = row.get('metrics', {})
    text_assets = _get_ad_text_assets(ad_column_data)
    ad_type = ad_column_data.get('type', 'N/A')

    # Calculate overall conversion rate for the ad
    ad_conversion_rate = _calculate_safe_rate(
        ad_metrics.get('all_conversions'), 
        ad_metrics.get('clicks')
    )

    return {
        "ad_id": ad_id,
        "ad_type": ad_type,
        "ad_status": row.get('ad_group_ad', {}).get('status', 'N/A'),
        "headlines": text_assets["headlines"],
        "descriptions": text_assets["descriptions"],
        "impressions": ad_metrics.get('impressions', 'N/A'),
        "clicks": ad_metrics.get('clicks', 'N/A'),
        "cost_currency": micros_to_currency(ad_metrics.get('cost_micros')),
        "all_conversions": ad_metrics.get('all_conversions', 'N/A'),  # Total for the ad
        "interaction_rate": ad_metrics.get('interaction_rate', 'N/A'),
        "conversion_rate": ad_conversion_rate  # Overall for the ad
    }

def parse_date_range(range_name_str: str) -> Dict[str, str]:
    """
    Parses a date range string into start and end dates.
    
    Supports explicit date ranges, relative date phrases, and single dates.
    
    Args:
        range_name_str: Either an explicit date range "YYYY-MM-DD_YYYY-MM-DD",
                       a relative phrase like "last 7 days", 
                       or a single date like "16/03/2024" (DD/MM/YYYY)

    Returns:
        A dictionary with "start_date" and "end_date" in YYYY-MM-DD format.

    Raises:
        ValueError: If the string is not in a supported format.
    """
    # Handle relative date ranges
    if range_name_str.lower() == "last 7 days" or range_name_str.lower() == "last_7_days":
        # Calculate the last 7 complete days (excluding today)
        today = datetime.now().date()
        end_date = today - timedelta(days=1)  # Yesterday
        start_date = end_date - timedelta(days=6)  # 7 days total including end_date
        
        return {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d')
        }
    
    # Handle single date in DD/MM/YYYY format
    if '/' in range_name_str and '_' not in range_name_str:
        try:
            # Parse DD/MM/YYYY format
            parsed_date = datetime.strptime(range_name_str, '%d/%m/%Y').date()
            formatted_date = parsed_date.strftime('%Y-%m-%d')
            
            # Return as single-day range
            return {
                "start_date": formatted_date,
                "end_date": formatted_date
            }
        except ValueError:
            # Fall through to handle other formats or raise error
            pass
    
    # Handle explicit date range format
    if '_' in range_name_str:
        try:
            # Split the date range string on underscore
            start_str, end_str = range_name_str.split('_')
            # Validate format by attempting to parse as dates
            datetime.strptime(start_str, '%Y-%m-%d')
            datetime.strptime(end_str, '%Y-%m-%d')
            # Consider adding validation that start_date is not after end_date if necessary
            return {"start_date": start_str, "end_date": end_str}
        except ValueError:
            # Fall through to error handling
            pass
    
    # If we get here, the format wasn't recognized
    logger.error(f"Invalid date range string format: '{range_name_str}'. Expected 'YYYY-MM-DD_YYYY-MM-DD', 'DD/MM/YYYY', or 'last 7 days'.")
    raise ValueError(f"Invalid date range string format: '{range_name_str}'. Must be 'YYYY-MM-DD_YYYY-MM-DD', 'DD/MM/YYYY', or 'last 7 days'.")

def fetch_campaign_data(client, customer_id, date_ranges_input):
    """Fetches campaign performance data from Google Ads API."""
    ga_service = client.get_service("GoogleAdsService")

    # GAQL query template for campaign metrics
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
    
    # Parse date ranges from input strings to structured dictionaries
    parsed_date_ranges = []
    if isinstance(date_ranges_input, str): # Handle single string date range
        date_ranges_input = [date_ranges_input]
    
    for dr_input in date_ranges_input:
        parsed_date_ranges.append(parse_date_range(dr_input))

    # Process each date range separately
    for date_range in parsed_date_ranges:
        query = query_template.format(start_date=date_range['start_date'], end_date=date_range['end_date'])
        
        # Wrap API calls in try-except for error handling
        try:
            response = ga_service.search(customer_id=customer_id, query=query)
        except Exception as e:
            logger.error(f"Error during Google Ads API call for date range {date_range}: {str(e)}")
            # Add error placeholder and continue to next date range
            all_results.append({
                'date_range': f"{date_range['start_date']} to {date_range['end_date']}",
                'error': f"Failed to retrieve data: {str(e)}",
                'data': []
            })
            continue # Move to the next date range

        # Initialize result structure for this date range
        date_range_result = {
            'date_range': f"{date_range['start_date']} to {date_range['end_date']}",
            'data': []
        }

        # Process each row returned by the API
        for row in response:
            # Convert protobuf response to dictionary
            row_dict = proto.Message.to_dict(row, use_integers_for_enums=False)

            # Extract data sections from the row
            campaign = row_dict.get('campaign', {})
            metrics = row_dict.get('metrics', {})
            customer = row_dict.get('customer', {})
            budget = row_dict.get('campaign_budget', {})

            # Calculate ROAS (Return on Ad Spend)
            conversions_value = metrics.get('conversions_value', 0.0) # Ensure float for division
            cost_micros = metrics.get('cost_micros', 1) 
            cost = micros_to_currency(cost_micros)
            
            # Ensure cost is a number and not 'N/A' before division
            roas = 0
            if isinstance(cost, (int, float)) and cost != 0:
                 roas = conversions_value / cost
            elif cost == 'N/A' or cost == 0: # if cost is N/A or 0, ROAS is 0 or undefined. Let's use 0.
                 roas = 0

            # Calculate All Conversions Rate safely
            raw_all_conversions = metrics.get('all_conversions')
            raw_interactions = metrics.get('interactions')

            # Convert to numeric values with error handling
            try:
                numeric_all_conversions = float(raw_all_conversions)
            except (ValueError, TypeError): # Handles None and non-numeric strings like 'N/A'
                numeric_all_conversions = 0.0

            try:
                numeric_interactions = float(raw_interactions)
            except (ValueError, TypeError): # Handles None and non-numeric strings like 'N/A'
                numeric_interactions = 0.0

            # Calculate conversion rate with division by zero protection
            all_conversions_rate = 0.0 # Default to 0.0
            if numeric_interactions > 0: # Check for > 0 to avoid division by zero and ensure meaningful rate
                all_conversions_rate = numeric_all_conversions / numeric_interactions

            # Structure the campaign data for output
            data = {
                "Campaign ID" : campaign.get('id', 'N/A'),
                "Campaign status": campaign.get('status', 'N/A'),
                "Campaign": campaign.get('name', 'N/A'),
                "Currency code": customer.get('currency_code', 'N/A'),
                "Budget": micros_to_currency(budget.get('amount_micros')), # Removed default 0
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
                "Cost / conv.": micros_to_currency(metrics.get('cost_per_conversion')),
                "All Conversions Rate": all_conversions_rate # Calculated numeric value
            }
            date_range_result['data'].append(data)
        all_results.append(date_range_result)
    return all_results

def fetch_keyword_data(client, customer_id, date_ranges_input, campaign_ids=None, ad_group_ids=None):
    """Fetches keyword performance data from Google Ads API with optional filtering."""
    ga_service = client.get_service("GoogleAdsService")
    all_results = []

    # Parse date ranges from input strings
    parsed_date_ranges = []
    if isinstance(date_ranges_input, str):
        date_ranges_input = [date_ranges_input]
    for dr_input in date_ranges_input:
        parsed_date_ranges.append(parse_date_range(dr_input))

    # Define base GAQL query template for keyword data
    query_template = """
        SELECT
        ad_group_criterion.keyword.text,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros
        FROM keyword_view
        WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        AND ad_group_criterion.status != 'REMOVED'
    """

    # Add optional campaign filter
    if campaign_ids and len(campaign_ids) > 0:
        campaign_filter = ", ".join([f"'{cid}'" for cid in campaign_ids])
        query_template += f" AND campaign.id IN ({campaign_filter})"

    # Add optional ad group filter
    if ad_group_ids and len(ad_group_ids) > 0:
        ad_group_filter = ", ".join([f"'{agid}'" for agid in ad_group_ids])
        query_template += f" AND ad_group.id IN ({ad_group_filter})"
    
    # Remove the LIMIT clause - process all available data
    # query_template += " LIMIT 20"
        
    logger.info(f"Constructed GAQL Query Template for keywords: {query_template}")

    # Process each date range
    for date_range in parsed_date_ranges:
        query = query_template.format(start_date=date_range['start_date'], end_date=date_range['end_date'])
        logger.info(f"Executing GAQL Query for keyword data, date range {date_range['start_date']} to {date_range['end_date']}")

        # Initialize result structure for this date range
        current_range_results = {
            'date_range': f"{date_range['start_date']} to {date_range['end_date']}",
            'error': None,
            'data': []
        }

        try:
            # Execute the Google Ads API search
            response = ga_service.search(customer_id=customer_id, query=query)
            
            # Process each keyword row returned
            for row in response:
                # Convert protobuf response to dictionary
                row_dict = proto.Message.to_dict(row, use_integers_for_enums=False)
                
                # Extract data sections from the row
                campaign = row_dict.get('campaign', {})
                ad_group = row_dict.get('ad_group', {})
                criterion = row_dict.get('ad_group_criterion', {})
                keyword = criterion.get('keyword', {})
                metrics = row_dict.get('metrics', {})
                quality_info = criterion.get('quality_info', {})
                
                # Get conversion rate with safe default
                conversion_rate = metrics.get('conversion_rate', 0.0)
                
                # Structure the keyword data for output
                keyword_data = {
                    "Campaign ID": campaign.get('id', 'N/A'),
                    "Campaign": campaign.get('name', 'N/A'),
                    "Ad Group ID": ad_group.get('id', 'N/A'),
                    "Ad Group": ad_group.get('name', 'N/A'),
                    "Keyword ID": criterion.get('criterion_id', 'N/A'),
                    "Keyword": keyword.get('text', 'N/A'),
                    "Match Type": keyword.get('match_type', 'N/A'),
                    "Status": criterion.get('status', 'N/A'),
                    "Quality Score": quality_info.get('quality_score', 'N/A'),
                    "Impressions": metrics.get('impressions', 'N/A'),
                    "Clicks": metrics.get('clicks', 'N/A'),
                    "Cost": micros_to_currency(metrics.get('cost_micros')),
                    "Conversions": metrics.get('all_conversions', 'N/A'),
                    "Conversion Rate": conversion_rate,
                    "Interaction Rate": metrics.get('interaction_rate', 'N/A'),
                    "Avg. CPC": micros_to_currency(metrics.get('average_cpc'))
                }
                
                current_range_results['data'].append(keyword_data)

        except Exception as e:
            logger.error(f"Error during Google Ads API call for keyword data, range {date_range}: {str(e)}")
            current_range_results['error'] = f"Failed to retrieve keyword data: {str(e)}"
        
        all_results.append(current_range_results)

    return all_results


# ---- Action Handlers ----
@google_ads.action("retrieve_campaign_metrics")
class AdwordsCampaignAction(ActionHandler):
    """Action handler for retrieving campaign performance metrics from Google Ads."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            # Extract authentication token from context
            refresh_token = context.auth.get("credentials", {}).get("refresh_token")
            
            if not refresh_token:
                logger.error("Refresh token is missing in auth credentials")
                raise Exception("Refresh token is required for authentication with Google Ads API")

            # Extract required input parameters
            login_customer_id = inputs.get('login_customer_id')
            customer_id = inputs.get('customer_id')
            
            # Validate required parameters
            if not login_customer_id:
                logger.error("Manager Account ID (login_customer_id) is missing in inputs")
                raise Exception("Manager Account ID (login_customer_id) is required")
                
            if not customer_id:
                logger.error("Customer ID is missing in inputs")
                raise Exception("Customer ID is required")

            # Build Google Ads API client credentials
            credentials = {
                "developer_token": DEVELOPER_TOKEN,
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "refresh_token": refresh_token,
                "login_customer_id": login_customer_id,
                "use_proto_plus": True
            }

            # Initialize the Google Ads API client
            client = GoogleAdsClient.load_from_dict(credentials)

        except Exception as e:
            logger.exception(f"Failed to initialize GoogleAdsClient: {str(e)}")
            raise Exception(f"Failed to initialize Google Ads client: {str(e)}")

        # Get date ranges input parameter
        date_ranges_input = inputs.get('date_ranges')

        # Validate date ranges parameter
        if not date_ranges_input: # Catches None, empty list, empty string.
            logger.error("'date_ranges' is a required input and was not provided or is empty.")
            raise Exception("'date_ranges' is required. Provide a date range string like 'YYYY-MM-DD_YYYY-MM-DD' or a list of such strings.")

        try:
            # Fetch campaign data using the API client
            results = fetch_campaign_data(client, customer_id, date_ranges_input)
            logger.info("Successfully retrieved campaign data.")
            return ActionResult(data=results, cost_usd=0.01)
        except ValueError as ve:
            logger.error(f"ValueError in AdwordsCampaignAction: {str(ve)}")
            raise Exception(str(ve))
        except Exception as e:
            logger.exception(f"Exception during campaign data retrieval: {str(e)}")
            raise Exception(f"An unexpected error occurred during data retrieval: {str(e)}")

@google_ads.action("retrieve_keyword_metrics")
class AdwordsKeywordAction(ActionHandler):
    """Action handler for retrieving keyword performance metrics from Google Ads."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        try:
            # Extract authentication token from context
            refresh_token = context.auth.get("credentials", {}).get("refresh_token")
            
            if not refresh_token:
                logger.error("Refresh token is missing in auth credentials")
                raise Exception("Refresh token is required for authentication with Google Ads API")

            # Extract required input parameters
            login_customer_id = inputs.get('login_customer_id')
            customer_id = inputs.get('customer_id')
            
            # Validate required parameters
            if not login_customer_id:
                logger.error("Manager Account ID (login_customer_id) is missing in inputs")
                raise Exception("Manager Account ID (login_customer_id) is required")
                
            if not customer_id:
                logger.error("Customer ID is missing in inputs")
                raise Exception("Customer ID is required")

            # Build Google Ads API client credentials
            credentials = {
                "developer_token": DEVELOPER_TOKEN,
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "refresh_token": refresh_token,
                "login_customer_id": login_customer_id,
                "use_proto_plus": True
            }

            # Initialize the Google Ads API client
            client = GoogleAdsClient.load_from_dict(credentials)

        except Exception as e:
            logger.exception(f"Failed to initialize GoogleAdsClient: {str(e)}")
            raise Exception(f"Failed to initialize Google Ads client: {str(e)}")

        # Extract input parameters for filtering
        date_ranges_input = inputs.get('date_ranges')
        campaign_ids = inputs.get('campaign_ids', [])
        ad_group_ids = inputs.get('ad_group_ids', [])

        # Validate required date ranges parameter
        if not date_ranges_input:
            logger.error("'date_ranges' is a required input and was not provided or is empty.")
            raise Exception("'date_ranges' is required. Provide a date range string like 'YYYY-MM-DD_YYYY-MM-DD' or a list of such strings.")

        try:
            # Fetch keyword data using the API client with optional filters
            results = fetch_keyword_data(client, customer_id, date_ranges_input, campaign_ids, ad_group_ids)
            logger.info("Successfully retrieved keyword data.")
            return ActionResult(data=results, cost_usd=0.01)
        except ValueError as ve:
            logger.error(f"ValueError in AdwordsKeywordAction: {str(ve)}")
            raise Exception(str(ve))
        except Exception as e:
            logger.exception(f"Exception during keyword data retrieval: {str(e)}")
            raise Exception(f"An unexpected error occurred during data retrieval: {str(e)}")
