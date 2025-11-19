from autohive_integrations_sdk import (
    Integration, ExecutionContext, ActionHandler
)
from typing import Dict, Any, List, Optional

# Create the integration using the config.json
google_images = Integration.load()

@google_images.action("google_images_search")
class GoogleImagesSearch(ActionHandler):
    """Takes in a query and searches the google images engine for results."""
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext):
        api_key = context.auth.get("credentials", {}).get("api_key", {})
        
        # Build SerpApi request parameters for google images search
        params = {
            "api_key": api_key,
            "engine": "google_images",
            "q": inputs["q"],
            "hl": "en",
            "gl": "us"
        }
        
        # Make API request to SerpApi
        response = await context.fetch(
            "https://serpapi.com/search",
            method="GET",
            params=params
        )
        
        # Extract results
        results = response.get("images_results", [])
        limit = inputs.get("num", 10)
        images = []
        
        for result in results[:limit]:
            image = {
                "title": result.get("title"),
                "source": result.get("source"),
                "page_link": result.get("link"),
                "image_url": result.get("original"),
                "width": result.get("original_width"),
                "height": result.get("original_height"),
            }
            images.append(image)
            
        return {
            "images": images,
            "total_results": len(images)   
        }