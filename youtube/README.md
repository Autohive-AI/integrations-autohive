# YouTube Integration for Autohive

Complete YouTube Data API v3 integration that enables full management of videos, channels, playlists, comments, and more directly from Autohive workflows.

## Description

This integration provides comprehensive access to YouTube's features through the Data API v3, allowing users to search content, manage videos and playlists, interact with comments, and access detailed channel analytics. It uses Google's OAuth2 authentication to securely access YouTube with appropriate permissions.

Key features:
- Search videos, channels, and playlists with advanced filtering
- Get detailed video information including views, likes, duration, and statistics
- Update video metadata (title, description, tags, privacy settings)
- Upload custom thumbnails
- Complete playlist management (create, update, delete, add/remove videos)
- Full comment functionality (read, post, reply, update, delete, moderate)
- Access channel analytics (subscribers, total views, video count)
- Moderation tools for channel owners

## Setup & Authentication

The integration uses Google's OAuth2 platform authentication for YouTube access. Users need to authenticate through Google's OAuth flow within Autohive to grant YouTube permissions.

**Authentication Type:** Platform (YouTube)

**Required Scopes:**
- `https://www.googleapis.com/auth/youtube` - Full YouTube access
- `https://www.googleapis.com/auth/youtube.upload` - Upload thumbnails
- `https://www.googleapis.com/auth/youtube.force-ssl` - Secure SSL access

No additional configuration fields are required as authentication is handled through Google's OAuth2 flow.

## Quota Information

YouTube Data API v3 uses a quota system (default: 10,000 units/day). Different operations have different costs:

- **Read operations** (list, get): 1 unit
- **Search**: 100 units
- **Write operations** (insert, update, delete): 50 units

Plan your automation workflows accordingly to stay within quota limits.

## Actions

### Search & Discovery

#### Action: `search`

Search for videos, channels, or playlists on YouTube with advanced filtering options.

**Inputs:**
- `query` *(required)*: Search query term
- `type`: Filter by resource type (video, channel, playlist)
- `max_results`: Maximum results per request (1-50, default 5)
- `order`: Sort order (relevance, date, rating, viewCount, title)
- `published_after`: Filter content published after this date (RFC 3339)
- `published_before`: Filter content published before this date (RFC 3339)
- `channel_id`: Search within a specific channel
- `region_code`: Geographic location code (e.g., US, GB)
- `page_token`: Pagination token

**Outputs:**
- `items`: Array of search results with id, title, description, thumbnail, published date
- `next_page_token`: Token for next page of results
- `total_results`: Total number of results available
- `result`: Success status
- `error`: Error message if failed

**Quota Cost:** 100 units

---

### Video Management

#### Action: `get_video`

Get detailed information about a specific YouTube video.

**Inputs:**
- `video_id` *(required)*: YouTube video ID

**Outputs:**
- `video`: Complete video details including:
  - Basic info (id, title, description, channel info)
  - Statistics (view_count, like_count, comment_count)
  - Content details (duration)
  - Tags and thumbnails
- `result`: Success status
- `error`: Error message if failed

**Quota Cost:** 1 unit

---

#### Action: `update_video`

Update video metadata including title, description, tags, privacy status, and more.

**Inputs:**
- `video_id` *(required)*: YouTube video ID
- `title`: Updated video title
- `description`: Updated video description
- `category_id`: Video category ID
- `tags`: Array of video tags
- `privacy_status`: Privacy setting (private, public, unlisted)
- `made_for_kids`: Boolean indicating if video is made for kids

**Outputs:**
- `video`: Updated video details
- `result`: Success status
- `error`: Error message if failed

**Quota Cost:** 50 units

---

#### Action: `upload_thumbnail`

Upload a custom thumbnail image for a video.

**Inputs:**
- `video_id` *(required)*: YouTube video ID
- `image_url` *(required)*: URL or path to thumbnail image (JPEG/PNG, max 2MB)

**Outputs:**
- `thumbnail`: Thumbnail details
- `result`: Success status
- `error`: Error message if failed

**Quota Cost:** 50 units

**Note:** Thumbnail uploads require multipart form data upload. May need platform-specific implementation.

---

### Channel Management

#### Action: `get_channel`

Get channel information including subscriber count, video count, and total views.

**Inputs:**
- `channel_id`: YouTube channel ID
- `channel_handle`: Channel handle (e.g., @username)
- `mine`: Boolean to get authenticated user's channel

**Note:** Must provide one of: channel_id, channel_handle, or mine=true

**Outputs:**
- `channel`: Complete channel details including:
  - Basic info (id, title, description, custom_url)
  - Statistics (subscriber_count, video_count, view_count)
  - Thumbnails and publication date
- `result`: Success status
- `error`: Error message if failed

**Quota Cost:** 1 unit

---

### Playlist Management

#### Action: `list_playlists`

List playlists from a channel or authenticated user.

**Inputs:**
- `channel_id`: Channel ID to list playlists from
- `mine`: Boolean to list authenticated user's playlists
- `max_results`: Maximum results (1-50, default 5)
- `page_token`: Pagination token

**Outputs:**
- `playlists`: Array of playlist objects
- `next_page_token`: Token for next page
- `result`: Success status
- `error`: Error message if failed

**Quota Cost:** 1 unit

---

#### Action: `create_playlist`

Create a new YouTube playlist.

**Inputs:**
- `title` *(required)*: Playlist title
- `description`: Playlist description
- `privacy_status` *(required)*: Privacy setting (private, public, unlisted)

**Outputs:**
- `playlist`: Created playlist details
- `result`: Success status
- `error`: Error message if failed

**Quota Cost:** 50 units

---

#### Action: `update_playlist`

Update playlist title, description, or privacy status.

**Inputs:**
- `playlist_id` *(required)*: Playlist ID
- `title`: Updated playlist title
- `description`: Updated playlist description
- `privacy_status`: Updated privacy setting (private, public, unlisted)

**Outputs:**
- `playlist`: Updated playlist details
- `result`: Success status
- `error`: Error message if failed

**Quota Cost:** 50 units

---

#### Action: `delete_playlist`

Delete a YouTube playlist permanently.

**Inputs:**
- `playlist_id` *(required)*: Playlist ID to delete

**Outputs:**
- `result`: Success status
- `error`: Error message if failed

**Quota Cost:** 50 units

---

#### Action: `list_playlist_items`

List all videos in a playlist.

**Inputs:**
- `playlist_id` *(required)*: Playlist ID
- `max_results`: Maximum results (1-50, default 5)
- `page_token`: Pagination token

**Outputs:**
- `items`: Array of playlist items with video details
- `next_page_token`: Token for next page
- `result`: Success status
- `error`: Error message if failed

**Quota Cost:** 1 unit

---

#### Action: `add_video_to_playlist`

Add a video to a playlist.

**Inputs:**
- `playlist_id` *(required)*: Playlist ID
- `video_id` *(required)*: Video ID to add
- `position`: Position in playlist (0-based, optional)

**Outputs:**
- `playlist_item`: Added playlist item details
- `result`: Success status
- `error`: Error message if failed

**Quota Cost:** 50 units

---

#### Action: `remove_video_from_playlist`

Remove a video from a playlist.

**Inputs:**
- `playlist_item_id` *(required)*: Playlist item ID to remove (not video ID)

**Outputs:**
- `result`: Success status
- `error`: Error message if failed

**Quota Cost:** 50 units

---

### Comment Management

#### Action: `list_comments`

List top-level comments for a video.

**Inputs:**
- `video_id` *(required)*: Video ID
- `max_results`: Maximum results (1-100, default 20)
- `order`: Sort order (time, relevance)
- `page_token`: Pagination token

**Outputs:**
- `comments`: Array of comment objects with text, author, likes, timestamps
- `next_page_token`: Token for next page
- `result`: Success status
- `error`: Error message if failed

**Quota Cost:** 1 unit

---

#### Action: `list_comment_replies`

List all replies to a specific comment.

**Inputs:**
- `parent_comment_id` *(required)*: Parent comment ID
- `max_results`: Maximum results (1-100, default 20)
- `page_token`: Pagination token

**Outputs:**
- `replies`: Array of reply comments
- `next_page_token`: Token for next page
- `result`: Success status
- `error`: Error message if failed

**Quota Cost:** 1 unit

---

#### Action: `post_comment`

Post a top-level comment on a video.

**Inputs:**
- `video_id` *(required)*: Video ID
- `text` *(required)*: Comment text

**Outputs:**
- `comment`: Posted comment details
- `result`: Success status
- `error`: Error message if failed

**Quota Cost:** 50 units

---

#### Action: `reply_to_comment`

Reply to an existing comment.

**Inputs:**
- `parent_comment_id` *(required)*: Parent comment ID
- `text` *(required)*: Reply text

**Outputs:**
- `comment`: Posted reply details
- `result`: Success status
- `error`: Error message if failed

**Quota Cost:** 50 units

---

#### Action: `update_comment`

Update your own comment text.

**Inputs:**
- `comment_id` *(required)*: Comment ID
- `text` *(required)*: Updated comment text

**Outputs:**
- `comment`: Updated comment details
- `result`: Success status
- `error`: Error message if failed

**Quota Cost:** 50 units

---

#### Action: `delete_comment`

Delete a comment (owner only).

**Inputs:**
- `comment_id` *(required)*: Comment ID to delete

**Outputs:**
- `result`: Success status
- `error`: Error message if failed

**Quota Cost:** 50 units

---

#### Action: `moderate_comment`

Set comment moderation status (channel owner only).

**Inputs:**
- `comment_id` *(required)*: Comment ID
- `moderation_status` *(required)*: Moderation status (published, heldForReview, rejected)
- `ban_author`: Boolean to ban comment author from channel

**Outputs:**
- `result`: Success status
- `error`: Error message if failed

**Quota Cost:** 50 units

---

## Usage Examples

### Example 1: Search for videos about Python programming

```json
{
  "query": "Python programming tutorial",
  "type": "video",
  "max_results": 10,
  "order": "relevance"
}
```

### Example 2: Update video metadata

```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Updated Video Title",
  "description": "This is my updated video description with more details",
  "tags": ["tutorial", "howto", "educational"],
  "privacy_status": "public"
}
```

### Example 3: Create a new playlist and add videos

First, create the playlist:
```json
{
  "title": "My Favorite Tutorials",
  "description": "A collection of helpful tutorial videos",
  "privacy_status": "public"
}
```

Then add videos to it:
```json
{
  "playlist_id": "PLxxxxxxxxxxxxxxxx",
  "video_id": "dQw4w9WgXcQ"
}
```

### Example 4: Post a comment on a video

```json
{
  "video_id": "dQw4w9WgXcQ",
  "text": "Great video! This was really helpful, thanks for sharing."
}
```

### Example 5: Moderate comments (channel owners)

```json
{
  "comment_id": "UgzXXXXXXXXXXXXXXXX",
  "moderation_status": "rejected",
  "ban_author": false
}
```

### Example 6: Get channel analytics

```json
{
  "mine": true
}
```

Returns your channel's subscriber count, total views, and video count.

## Requirements

- Python dependencies are handled by the Autohive platform
- YouTube Data API v3 access
- Valid Google account with YouTube access
- Appropriate OAuth2 permissions granted

## Limitations & Notes

1. **Quota Limits**: Default quota is 10,000 units/day. Monitor usage carefully.
2. **Thumbnail Uploads**: Image uploads require multipart form data support.
3. **Moderation**: Comment moderation features only work for channel owners.
4. **Private Videos**: Some operations may fail on private videos you don't own.
5. **Rate Limiting**: Implement exponential backoff for API errors.

## Error Handling

All actions return a consistent error structure:
- `result`: false when an error occurs
- `error`: Descriptive error message

Common errors:
- `quotaExceeded`: Daily quota limit reached
- `forbidden`: Insufficient permissions
- `videoNotFound`: Video ID doesn't exist
- `invalidValue`: Invalid parameter value
- `commentDisabled`: Comments are disabled for this video

## Best Practices

1. **Minimize Quota Usage**:
   - Use specific filters to reduce search results
   - Cache frequently accessed data
   - Use pagination wisely

2. **Error Handling**:
   - Always check the `result` field
   - Implement retry logic with exponential backoff
   - Log errors for debugging

3. **Privacy & Compliance**:
   - Respect user privacy settings
   - Follow YouTube's Terms of Service
   - Handle sensitive data appropriately
   - Comply with COPPA for kids' content

4. **Performance**:
   - Batch operations when possible
   - Use appropriate `max_results` values
   - Implement caching strategies

## Testing

To test the integration:

1. Navigate to the integration's directory: `cd youtube`
2. Install dependencies: `pip install -r requirements.txt`
3. Configure your OAuth2 credentials
4. Run test actions through the Autohive platform

## Support

For issues or questions:
- Review YouTube Data API v3 documentation: https://developers.google.com/youtube/v3
- Check quota usage in Google Cloud Console
- Verify OAuth2 scopes are correctly configured

## Version History

- **v1.0.1** - Current version with complete YouTube Data API v3 support
  - Search functionality
  - Video management (get, update)
  - Playlist management
  - Comment management and moderation
  - Channel analytics
  - Thumbnail uploads
