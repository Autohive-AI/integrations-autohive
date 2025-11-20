# TripAdvisor Integration

This integration provides access to TripAdvisor's Content API, allowing you to retrieve location details, reviews, photos, and search for hotels, restaurants, and attractions.

## Features

- **Search Locations**: Search for hotels, restaurants, or attractions by query
- **Location Details**: Get comprehensive information about a specific location including ratings, address, contact info
- **Location Reviews**: Retrieve up to 5 most recent reviews for any location
- **Location Photos**: Get up to 5 most recent photos for any location
- **Nearby Search**: Find locations near specific coordinates (latitude/longitude)

## Setup

### 1. Get API Key

1. Visit the [TripAdvisor Developer Portal](https://www.tripadvisor.com/developers)
2. Sign up or log in to your account
3. Navigate to the credentials section
4. Generate a new API key for the Content API

### 2. Configure Integration

Edit `tripadvisor.py` and replace the API key placeholder:

```python
API_KEY = "YOUR_TRIPADVISOR_API_KEY_HERE"
```

Replace `YOUR_TRIPADVISOR_API_KEY_HERE` with your actual TripAdvisor API key.

## Available Actions

### search_locations

Search for hotels, restaurants, or attractions on TripAdvisor.

**Input:**
- `search_query` (required): Search query string (e.g., "Hilton Paris", "Pizza restaurants NYC")
- `category` (optional): Filter by category - "hotels", "restaurants", "attractions", or "geos" (default: "hotels")
- `language` (optional): Language code for results (e.g., "en", "es", "fr", "de") (default: "en")

**Example:**
```json
{
  "search_query": "Eiffel Tower",
  "category": "attractions",
  "language": "en"
}
```

### get_location_details

Get detailed information about a specific TripAdvisor location.

**Input:**
- `location_id` (required): TripAdvisor location ID (e.g., "60745" for Eiffel Tower)
- `language` (optional): Language code (default: "en")
- `currency` (optional): Currency code for prices (e.g., "USD", "EUR", "GBP") (default: "USD")

**Output includes:**
- Name, description, web URL
- Address details
- Rating and number of reviews
- Price level
- Category and subcategories
- Contact information (phone, email, website)
- Ranking data

**Example:**
```json
{
  "location_id": "60745",
  "language": "en",
  "currency": "USD"
}
```

### get_location_reviews

Get up to 5 most recent reviews for a specific TripAdvisor location.

**Input:**
- `location_id` (required): TripAdvisor location ID
- `language` (optional): Language code for reviews (default: "en")

**Output includes:**
- Review ID, rating, title, and text
- Published date and travel date
- Trip type
- User information (username, location, avatar)
- Helpful votes count

**Example:**
```json
{
  "location_id": "60745",
  "language": "en"
}
```

### get_location_photos

Get up to 5 most recent photos for a specific TripAdvisor location.

**Input:**
- `location_id` (required): TripAdvisor location ID
- `language` (optional): Language code for captions (default: "en")

**Output includes:**
- Photo ID and caption
- Published date
- Multiple image sizes (thumbnail, small, medium, large, original)
- Album and source information
- User information

**Example:**
```json
{
  "location_id": "60745",
  "language": "en"
}
```

### search_nearby_locations

Search for locations near specified geographic coordinates.

**Input:**
- `latitude` (required): Latitude coordinate
- `longitude` (required): Longitude coordinate
- `category` (optional): Filter by category - "hotels", "restaurants", or "attractions" (default: "hotels")
- `radius` (optional): Search radius (default: 5)
- `radius_unit` (optional): Unit for radius - "km" or "mi" (default: "km")
- `language` (optional): Language code (default: "en")

**Example:**
```json
{
  "latitude": 48.8584,
  "longitude": 2.2945,
  "category": "restaurants",
  "radius": 2,
  "radius_unit": "km"
}
```

## Use Cases

### For Your Listings

1. **Monitor Your Reviews**: Use `get_location_reviews` with your location ID to retrieve and monitor recent customer reviews
2. **Track Rating Changes**: Use `get_location_details` to track your overall rating and review count over time
3. **Manage Photos**: Use `get_location_photos` to see what photos customers are sharing
4. **Find Your Location ID**: Use `search_locations` with your business name to find your TripAdvisor location ID

### For Competitive Analysis

1. **Competitor Reviews**: Get reviews from competing businesses in your area
2. **Market Research**: Search nearby locations to understand the competitive landscape
3. **Rating Benchmarking**: Compare your ratings against competitors
4. **Photo Insights**: See what type of content works well for similar businesses

## API Limits

- **Rate Limit**: Up to 50 calls per second
- **Reviews**: Up to 5 reviews per location per request
- **Photos**: Up to 5 photos per location per request
- **Pricing**: Pay-as-you-go monthly billing with optional daily spending limits

## Important Notes

1. **Display Requirements**: When displaying TripAdvisor content, you must follow their [display requirements](https://www.tripadvisor.com/developers) and attribution guidelines
2. **Caching**: Implement appropriate caching policies to minimize API calls
3. **Location IDs**: Save location IDs for your listings and competitors to avoid repeated searches
4. **Language Support**: The API supports multiple languages - use appropriate language codes for your target audience

## Error Handling

All actions include error handling and will return an error object if something goes wrong:

```json
{
  "error": "Error message",
  "message": "User-friendly description"
}
```

## Support

For issues with the integration, check:
- Your API key is valid and active
- You haven't exceeded rate limits
- Location IDs are correct
- Required parameters are provided

For TripAdvisor API documentation and support, visit the [TripAdvisor Developer Portal](https://www.tripadvisor.com/developers).
