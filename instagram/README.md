# Instagram Integration for Autohive

Connects Autohive to the Instagram Graph API to allow users to retrieve posts and media from Instagram Business and Creator accounts.

## Description

This integration enables Autohive workflows to access Instagram content from Business and Creator accounts. It leverages the Instagram Graph API (via Facebook's Graph API) to retrieve recent posts, including media URLs, captions, timestamps, and permalinks.

The integration is designed for:
- Retrieving recent Instagram posts for content analysis
- Accessing post metadata (captions, media types, timestamps)
- Integrating Instagram content into automated workflows
- Supporting business and creator account management

This integration requires an Instagram Business or Creator account connected to a Facebook Page, as mandated by Meta's API requirements.

## Setup & Authentication

This integration uses **Platform Authentication** via Facebook OAuth. The authentication is handled automatically by Autohive's platform authentication system.

### Prerequisites

Before using this integration, ensure you have:

1. **Instagram Business or Creator Account**: Personal Instagram accounts are not supported by the Instagram Graph API. You must convert your account to a Business or Creator account.

2. **Facebook Page Connection**: Your Instagram Business/Creator account must be connected to a Facebook Page. This is a requirement from Meta to access the Instagram Graph API.

3. **Page Admin Access**: You must be an admin of the Facebook Page connected to your Instagram account.

### Authentication Method

**Type:** Platform Authentication (OAuth)
**Provider:** Facebook
**Required Scopes:**
- `instagram_basic`: Access to Instagram business account data
- `pages_read_engagement`: Read access to Facebook Page content

When you authenticate this integration in Autohive, you'll be redirected to Facebook to authorize access. The system will automatically:
1. Retrieve your Facebook Pages
2. Identify the Instagram Business Account connected to your page
3. Grant access to retrieve Instagram media

**Note:** Access tokens for Instagram expire every 60-90 days and will need to be refreshed periodically.

## Actions

### Action: `get_recent_posts`

**Description:** Retrieves recent Instagram posts from your Business or Creator account, including media URLs, captions, and engagement metadata.

**Inputs:**
- `limit` (optional): Number of posts to retrieve
  - Type: Number
  - Default: 10
  - Minimum: 1
  - Maximum: 25
  - Description: Specifies how many recent posts to fetch from your Instagram account

**Outputs:**
- `posts`: Array of post objects, where each post contains:
  - `id` (string): Unique Instagram post ID
  - `media_type` (string): Type of media (IMAGE, VIDEO, or CAROUSEL_ALBUM)
  - `media_url` (string): Direct URL to the media file
  - `caption` (string): Post caption text
  - `timestamp` (string): ISO 8601 timestamp of when the post was published
  - `permalink` (string): Direct Instagram link to the post

**Example Output:**
```json
{
  "posts": [
    {
      "id": "17895695668004550",
      "media_type": "IMAGE",
      "media_url": "https://scontent.cdninstagram.com/...",
      "caption": "Check out our latest product launch!",
      "timestamp": "2024-10-10T14:30:00+0000",
      "permalink": "https://www.instagram.com/p/ABC123xyz/"
    },
    {
      "id": "17895695668004551",
      "media_type": "VIDEO",
      "media_url": "https://scontent.cdninstagram.com/...",
      "caption": "Behind the scenes video",
      "timestamp": "2024-10-09T10:15:00+0000",
      "permalink": "https://www.instagram.com/p/DEF456abc/"
    }
  ]
}
```

## Requirements

This integration requires the following dependencies:

- `autohive-integrations-sdk`: Core SDK for building Autohive integrations

## Usage Examples

**Example 1: Retrieve Last 10 Posts**

Use the `get_recent_posts` action with default settings to fetch your 10 most recent Instagram posts:

```json
{
  "limit": 10
}
```

This is useful for creating workflows that monitor recent content or generate reports on posting activity.

**Example 2: Retrieve Last 5 Posts for Quick Updates**

Fetch only the 5 most recent posts for faster processing:

```json
{
  "limit": 5
}
```

Ideal for real-time notifications or quick content checks.

**Example 3: Maximum Posts (25)**

Retrieve the maximum allowed posts in a single request:

```json
{
  "limit": 25
}
```

Useful for comprehensive content analysis or bulk processing workflows.

## Testing

To test this integration locally:

1. Navigate to the integration's directory:
   ```bash
   cd instagram
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up test authentication credentials in `tests/test_integration.py`

4. Run the tests:
   ```bash
   python tests/test_integration.py
   ```

**Note:** Testing requires valid Instagram Business Account credentials and a Facebook Page connection. Mock authentication data can be used for basic structural tests, but actual API calls require valid tokens.

## API Rate Limits

Instagram Graph API enforces rate limits:
- **200 API calls per user per hour**
- The integration respects these limits but does not currently implement rate limit handling
- Plan your workflow execution frequency accordingly

## Known Limitations

- **Account Type**: Only Instagram Business and Creator accounts are supported (personal accounts are not supported)
- **Facebook Page Requirement**: Instagram account must be connected to a Facebook Page
- **Post Limit**: Maximum 25 posts per request (pagination not currently implemented)
- **Token Expiration**: Access tokens expire every 60-90 days and require re-authentication
- **Media Access**: Some video media URLs may require additional processing

## Troubleshooting

**No posts returned:**
- Verify your Instagram account is a Business or Creator account
- Ensure your Instagram account is connected to a Facebook Page
- Check that you're an admin of the connected Facebook Page
- Confirm you have published posts on your Instagram account

**Authentication errors:**
- Re-authenticate the integration in Autohive
- Verify the required scopes (`instagram_basic`, `pages_read_engagement`) are granted
- Check that your Facebook Page has an Instagram account connected

**Empty media_url fields:**
- Some media types (especially videos) may have delayed media_url availability
- The `thumbnail_url` field can be used as an alternative for videos

## Additional Resources

- [Instagram Graph API Documentation](https://developers.facebook.com/docs/instagram-api)
- [Set up Instagram Business Account](https://help.instagram.com/502981923235522)
- [Connect Instagram to Facebook Page](https://www.facebook.com/business/help/connect-instagram-to-page)
