import asyncio
from context import tripadvisor
from autohive_integrations_sdk import ExecutionContext

# Test configuration
# Replace these with your actual test credentials and test data
TEST_CONFIG = {
    "api_key": "YOUR_TRIPADVISOR_API_KEY_HERE",  # Replace with actual API key
    "location_id": "60745",  # Eiffel Tower
    "search_query": "Times Square",
    "latitude": 40.758896,  # Times Square coordinates
    "longitude": -73.985130,
    "language": "en",
    "currency": "USD"
}

# Authentication configuration for tests
def get_auth():
    """Get authentication configuration"""
    return {
        "auth_type": "custom",
        "credentials": {
            "api_key": TEST_CONFIG["api_key"]
        }
    }


async def test_search_locations():
    """Test searching for locations"""
    print("\n=== Testing Search Locations ===")

    auth = get_auth()
    inputs = {
        "search_query": TEST_CONFIG["search_query"],
        "category": "hotels",
        "language": TEST_CONFIG["language"]
    }

    async with ExecutionContext(auth=auth) as context:
        result = await tripadvisor.execute_action("search_locations", inputs, context)

        if result.get("error"):
            print(f"Error: {result.get('error')}")
            print(f"Message: {result.get('message')}")
            return result

        data = result.get("data", [])
        print(f"Found {len(data)} locations")
        if data:
            location = data[0]
            print(f"First location: {location.get('name')}")
            print(f"Location ID: {location.get('location_id')}")
            address = location.get('address_obj', {})
            print(f"Address: {address.get('street1', '')}, {address.get('city', '')}, {address.get('country', '')}")
        return result


async def test_get_location_details():
    """Test getting location details"""
    print("\n=== Testing Get Location Details ===")

    auth = get_auth()
    inputs = {
        "location_id": TEST_CONFIG["location_id"],
        "language": TEST_CONFIG["language"],
        "currency": TEST_CONFIG["currency"]
    }

    async with ExecutionContext(auth=auth) as context:
        result = await tripadvisor.execute_action("get_location_details", inputs, context)

        if result.get("error"):
            print(f"Error: {result.get('error')}")
            print(f"Message: {result.get('message')}")
            return result

        print(f"Name: {result.get('name')}")
        print(f"Description: {result.get('description', '')[:100]}...")
        print(f"Rating: {result.get('rating')}")
        print(f"Number of reviews: {result.get('num_reviews')}")
        print(f"Price level: {result.get('price_level', 'N/A')}")

        address = result.get('address_obj', {})
        print(f"Address: {address.get('address_string', 'N/A')}")

        category = result.get('category', {})
        print(f"Category: {category.get('localized_name', 'N/A')}")

        ranking = result.get('ranking_data', {})
        print(f"Ranking: {ranking.get('ranking_string', 'N/A')}")

        print(f"Website: {result.get('website', 'N/A')}")
        print(f"Phone: {result.get('phone', 'N/A')}")
        print(f"TripAdvisor URL: {result.get('web_url', 'N/A')}")

        return result


async def test_get_location_reviews():
    """Test getting location reviews"""
    print("\n=== Testing Get Location Reviews ===")

    auth = get_auth()
    inputs = {
        "location_id": TEST_CONFIG["location_id"],
        "language": TEST_CONFIG["language"]
    }

    async with ExecutionContext(auth=auth) as context:
        result = await tripadvisor.execute_action("get_location_reviews", inputs, context)

        if result.get("error"):
            print(f"Error: {result.get('error')}")
            print(f"Message: {result.get('message')}")
            return result

        reviews = result.get("data", [])
        print(f"Found {len(reviews)} reviews")

        if reviews:
            review = reviews[0]
            print(f"\nFirst review:")
            print(f"  Title: {review.get('title')}")
            print(f"  Rating: {review.get('rating')}/5")
            print(f"  Published: {review.get('published_date')}")
            print(f"  Travel date: {review.get('travel_date', 'N/A')}")
            print(f"  Text: {review.get('text', '')[:150]}...")

            user = review.get('user', {})
            print(f"  Reviewer: {user.get('username')}")
            user_location = user.get('user_location', {})
            print(f"  From: {user_location.get('name', 'N/A')}")
            print(f"  Helpful votes: {review.get('helpful_votes', 0)}")
            print(f"  Trip type: {review.get('trip_type', 'N/A')}")

        return result


async def test_get_location_photos():
    """Test getting location photos"""
    print("\n=== Testing Get Location Photos ===")

    auth = get_auth()
    inputs = {
        "location_id": TEST_CONFIG["location_id"],
        "language": TEST_CONFIG["language"]
    }

    async with ExecutionContext(auth=auth) as context:
        result = await tripadvisor.execute_action("get_location_photos", inputs, context)

        if result.get("error"):
            print(f"Error: {result.get('error')}")
            print(f"Message: {result.get('message')}")
            return result

        photos = result.get("data", [])
        print(f"Found {len(photos)} photos")

        if photos:
            photo = photos[0]
            print(f"\nFirst photo:")
            print(f"  ID: {photo.get('id')}")
            print(f"  Caption: {photo.get('caption', 'N/A')}")
            print(f"  Published: {photo.get('published_date')}")
            print(f"  Album: {photo.get('album', 'N/A')}")
            print(f"  Is blessed: {photo.get('is_blessed', False)}")

            user = photo.get('user', {})
            print(f"  Uploaded by: {user.get('username', 'N/A')}")

            images = photo.get('images', {})
            if images.get('large'):
                large = images['large']
                print(f"  Large image: {large.get('url')}")
                print(f"  Dimensions: {large.get('width')}x{large.get('height')}")

        return result


async def test_search_nearby_locations():
    """Test searching for nearby locations"""
    print("\n=== Testing Search Nearby Locations ===")

    auth = get_auth()
    inputs = {
        "latitude": TEST_CONFIG["latitude"],
        "longitude": TEST_CONFIG["longitude"],
        "category": "restaurants",
        "radius": 2,
        "radius_unit": "km",
        "language": TEST_CONFIG["language"]
    }

    async with ExecutionContext(auth=auth) as context:
        result = await tripadvisor.execute_action("search_nearby_locations", inputs, context)

        if result.get("error"):
            print(f"Error: {result.get('error')}")
            print(f"Message: {result.get('message')}")
            return result

        locations = result.get("data", [])
        print(f"Found {len(locations)} nearby locations")

        if locations:
            for i, location in enumerate(locations[:3], 1):
                print(f"\nLocation {i}:")
                print(f"  Name: {location.get('name')}")
                print(f"  Location ID: {location.get('location_id')}")
                print(f"  Distance: {location.get('distance', 'N/A')}")
                print(f"  Rating: {location.get('rating', 'N/A')}")
                print(f"  Bearing: {location.get('bearing', 'N/A')}")

                address = location.get('address_obj', {})
                print(f"  Address: {address.get('street1', '')}, {address.get('city', '')}")

        return result


async def test_workflow():
    """Test a complete workflow: search -> details -> reviews -> photos"""
    print("\n=== Testing Complete Workflow ===")

    # 1. Search for locations
    print("\n1. Searching for locations...")
    search_results = await test_search_locations()

    # 2. Get details for first location (if available)
    if search_results and search_results.get('data') and not search_results.get('error'):
        location_id = search_results['data'][0].get('location_id')
        if location_id:
            TEST_CONFIG["location_id"] = location_id
            print(f"\n2. Getting details for location {location_id}...")
            await test_get_location_details()

            # 3. Get reviews
            print(f"\n3. Getting reviews for location {location_id}...")
            await test_get_location_reviews()

            # 4. Get photos
            print(f"\n4. Getting photos for location {location_id}...")
            await test_get_location_photos()

    # 5. Search nearby locations
    print("\n5. Searching nearby locations...")
    await test_search_nearby_locations()

    print("\n=== Workflow Complete ===")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("TripAdvisor Integration Tests")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Location ID: {TEST_CONFIG['location_id']}")
    print(f"  Search Query: {TEST_CONFIG['search_query']}")
    print(f"  Coordinates: {TEST_CONFIG['latitude']}, {TEST_CONFIG['longitude']}")
    print(f"  Language: {TEST_CONFIG['language']}")
    print(f"  Currency: {TEST_CONFIG['currency']}")
    print("\nNote: Update TEST_CONFIG with your API key and test data")
    print("=" * 60)

    try:
        # Run individual tests
        await test_search_locations()
        await test_get_location_details()
        await test_get_location_reviews()
        await test_get_location_photos()
        await test_search_nearby_locations()

        # Run workflow test
        # await test_workflow()

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n!!! Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
