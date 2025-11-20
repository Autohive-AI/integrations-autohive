from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler
)
from typing import Dict, Any, List, Optional
import base64
import aiohttp
from urllib.parse import urlparse

# Create the integration using the config.json
google_images = Integration.load()

# ---- Constants ----

SERPAPI_BASE_URL = "https://serpapi.com/search"
SERPAPI_ENGINE = "google_images"
DEFAULT_LANGUAGE = "en"
DEFAULT_COUNTRY = "us"
DEFAULT_RESULT_LIMIT = 10

# Response field mappings
RESPONSE_KEY_IMAGES = "images_results"
RESULT_KEY_TITLE = "title"
RESULT_KEY_SOURCE = "source"
RESULT_KEY_LINK = "link"
RESULT_KEY_ORIGINAL = "original"
RESULT_KEY_WIDTH = "original_width"
RESULT_KEY_HEIGHT = "original_height"

# ---- Helper Functions ----

def extract_image_data(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and normalize image data from a SerpApi result.
    
    Args:
        result: Raw image result dictionary from SerpApi response
        
    Returns:
        Dictionary containing normalized image data with keys:
        title, source, page_link, image_url, width, height
    """
    return {
        "title": result.get(RESULT_KEY_TITLE),
        "source": result.get(RESULT_KEY_SOURCE),
        "page_link": result.get(RESULT_KEY_LINK),
        "image_url": result.get(RESULT_KEY_ORIGINAL),
        "width": result.get(RESULT_KEY_WIDTH),
        "height": result.get(RESULT_KEY_HEIGHT),
    }


# ---- Action Handlers ----

@google_images.action("google_images_search")
class GoogleImagesSearch(ActionHandler):
    """
    Handler for searching Google Images using the SerpApi service.
    
    Searches Google Images based on a query string and returns a list
    of image results with metadata including title, source, URLs, and dimensions.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute a Google Images search query via SerpApi.
        
        Args:
            inputs: Dictionary containing:
                - q (str, required): Search query string. Supports advanced operators 
                  like inurl:, site:, intitle:
                - num (int, optional): Maximum number of results to return (1-100, default: 10)
                - location (str, optional): Geographic location for search (city level recommended, 
                  e.g., 'Austin, Texas, United States')
                - gl (str, optional): Country code for localized results (e.g., 'us', 'uk', 'fr')
                - hl (str, optional): Language code for search interface (e.g., 'en', 'fr', 'de')
                - tbs (str, optional): Advanced search filters. Image filters: 
                  isz:l (large), ic:color (color), itp:photo (photo), qdr:w (week). 
                  Combine multiple filters with commas.
                - filter (int, optional): Enable/disable 'Similar Results' and 'Omitted Results' 
                  filters (0=disable, 1=enable, default: 1)
            context: Execution context providing authentication and network capabilities
            
        Returns:
            Dictionary containing:
                - images (List[Dict]): List of image result dictionaries, each containing:
                    - title: Image title
                    - source: Source website name
                    - page_link: URL to the page containing the image
                    - image_url: Direct URL to the image
                    - width: Image width in pixels
                    - height: Image height in pixels
                - total_results (int): Number of images returned
                
        Raises:
            ValueError: If API key is missing or query is empty
            Exception: If API request fails or returns unexpected response
        """
        # Validate required inputs
        query = inputs.get("q", "").strip()
        if not query:
            raise ValueError("Search query 'q' is required and cannot be empty")
        
        # Get and validate API key
        api_key = context.auth.get("credentials", {}).get("api_key")
        if not api_key:
            raise ValueError("SerpApi API key is required in credentials")
        
        # Get result limit with validation
        limit = inputs.get("num", DEFAULT_RESULT_LIMIT)
        if not isinstance(limit, int) or limit < 1:
            limit = DEFAULT_RESULT_LIMIT
        elif limit > 100:
            limit = 100  # Enforce maximum
        
        # Build SerpApi request parameters
        params = {
            "api_key": api_key,
            "engine": SERPAPI_ENGINE,
            "q": query,
        }
        
        # Add num parameter (number of results per page)
        params["num"] = limit
        
        # Add language parameter (use provided or default)
        if inputs.get("hl"):
            params["hl"] = inputs["hl"]
        else:
            params["hl"] = DEFAULT_LANGUAGE
        
        # Add country parameter (use provided or default)
        if inputs.get("gl"):
            params["gl"] = inputs["gl"]
        else:
            params["gl"] = DEFAULT_COUNTRY
        
        # Add location parameter if provided
        if inputs.get("location"):
            params["location"] = inputs["location"]
        
        # Add tbs parameter (advanced filters) if provided
        if inputs.get("tbs"):
            params["tbs"] = inputs["tbs"]
        
        # Add filter parameter if provided (0 or 1)
        if inputs.get("filter") is not None:
            filter_value = inputs["filter"]
            # Validate filter value is 0 or 1
            if filter_value in [0, 1]:
                params["filter"] = filter_value
            # If invalid value provided, use default (1)
            else:
                params["filter"] = 1
        
        # Make API request to SerpApi
        try:
            response = await context.fetch(
                SERPAPI_BASE_URL,
                method="GET",
                params=params
            )
        except Exception as e:
            raise Exception(f"Failed to fetch results from SerpApi: {str(e)}")
        
        # Check for API errors in response
        if "error" in response:
            error_msg = response.get("error", "Unknown error")
            if "Invalid API key" in error_msg:
                raise ValueError("Invalid SerpApi API key. Please check your credentials.")
            elif "rate limit" in error_msg.lower():
                raise Exception("API rate limit exceeded. Please try again later.")
            else:
                raise Exception(f"SerpApi error: {error_msg}")
        
        # Extract and process results
        results = response.get(RESPONSE_KEY_IMAGES, [])
        if not isinstance(results, list):
            results = []
        
        # Limit results and extract image data
        images = [
            extract_image_data(result)
            for result in results[:limit]
        ]
        
        return {
            "images": images,
            "total_results": len(images)
        }

@google_images.action("download_image")
class DownloadImage(ActionHandler):
    """
    Download an image from a URL and return it as a file object.
    Useful for getting actual image data instead of just URLs.
    """
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """
        Download an image and return it as a file object.
        
        Args:
            inputs: Dictionary containing:
                - image_url (str, required): URL of the image to download
                - max_size_mb (float, optional): Maximum file size in MB (default: 10)
            context: Execution context
            
        Returns:
            Dictionary containing:
                - file: {
                    - content: Base64-encoded image data
                    - name: Filename
                    - contentType: MIME type (e.g., "image/jpeg")
                    - size: File size in bytes
                }
                - result: True if successful
        """
        image_url = inputs.get("image_url", "").strip()
        if not image_url:
            raise ValueError("Image URL is required")
        
        max_size_bytes = (inputs.get("max_size_mb", 10) * 1024 * 1024)  # Default 10MB
        
        try:
            # Download the image using aiohttp with timeout
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url, timeout=timeout) as response:
                    if response.status >= 400:
                        raise Exception(f"Failed to download image: HTTP {response.status}")
                    
                    # Check content-length if available
                    content_length = response.headers.get('content-length')
                    if content_length and int(content_length) > max_size_bytes:
                        raise ValueError(f"Image too large: {content_length} bytes (max: {max_size_bytes} bytes)")
                    
                    # Read binary content
                    image_bytes = await response.read()
                    
                    # Check actual size after download
                    if len(image_bytes) > max_size_bytes:
                        raise ValueError(f"Image too large: {len(image_bytes)} bytes (max: {max_size_bytes} bytes)")
                    
                    # Get content type from headers and strip charset
                    content_type = response.headers.get('content-type', 'image/jpeg')
                    if ';' in content_type:
                        content_type = content_type.split(';')[0].strip()
                    
                    # Extract filename from URL
                    parsed_url = urlparse(image_url)
                    filename = "image"
                    if parsed_url.path:
                        filename = parsed_url.path.split('/')[-1] or "image"
                        # Remove query parameters if they got included
                        if '?' in filename:
                            filename = filename.split('?')[0]
                    
                    # Add extension if missing
                    if '.' not in filename:
                        # Try to infer from content type
                        if 'jpeg' in content_type or 'jpg' in content_type:
                            filename += ".jpg"
                        elif 'png' in content_type:
                            filename += ".png"
                        elif 'gif' in content_type:
                            filename += ".gif"
                        elif 'webp' in content_type:
                            filename += ".webp"
                        else:
                            filename += ".jpg"
                    
                    # Encode to base64
                    content_b64 = base64.b64encode(image_bytes).decode('utf-8')
                    
                    return {
                        "file": {
                            "content": content_b64,
                            "name": filename,
                            "contentType": content_type,
                            "size": len(image_bytes)
                        },
                        "result": True
                    }
        
        except aiohttp.ClientError as e:
            raise Exception(f"Network error downloading image: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to download image: {str(e)}")