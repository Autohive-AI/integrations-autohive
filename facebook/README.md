# Facebook Pages Integration

Publish and schedule content to your Facebook Pages with this official Autohive integration. Manage your social media presence through automated posting workflows.

## What You Can Do

- **List Pages**: View all Facebook Pages you manage
- **Create Posts**: Publish content immediately to your Pages
- **Schedule Posts**: Plan content for future publication (10 minutes to 30 days ahead)

## Quick Setup

1. **Install the Integration**: Add the Facebook integration to your Autohive workspace
2. **Connect Your Account**: Authenticate with Facebook and grant Page management permissions
3. **Select Your Pages**: Choose which Pages you want to manage
4. **Start Automating**: Use the actions in your workflows immediately

## Available Actions

### List Pages

Get all Facebook Pages the authenticated user can manage.

**Parameters:** None

**Returns:**
- `pages`: Array of Page objects with `id`, `name`, `category`, and `access_token`

**Example Use Cases:**
- Display a selection of Pages for users to choose from
- Verify Page access before running post workflows
- Get Page IDs for use in other actions

### Create Post

Publish a post immediately to a Facebook Page.

**Parameters:**
- `page_id` (required): The ID of the Facebook Page to post to
- `message` (required): The text content of the post
- `link` (optional): URL to include in the post

**Returns:**
- `post_id`: The ID of the created post
- `success`: Boolean indicating success
- `permalink`: Direct URL to the post on Facebook

**Example Use Cases:**
- Share blog posts automatically when published
- Post product updates to your business Page
- Broadcast announcements to followers

### Schedule Post

Schedule a post to be published at a future time.

**Parameters:**
- `page_id` (required): The ID of the Facebook Page to post to
- `message` (required): The text content of the post
- `scheduled_time` (required): When to publish (ISO 8601 format or UNIX timestamp)
- `link` (optional): URL to include in the post

**Returns:**
- `post_id`: The ID of the scheduled post
- `success`: Boolean indicating success
- `scheduled_publish_time`: The scheduled publication time

**Scheduling Constraints:**
- Must be at least **10 minutes** in the future
- Must be within **30 days** from now

**Example Use Cases:**
- Plan weekly content calendars
- Schedule posts for optimal engagement times
- Coordinate product launch announcements

## Example Workflows

### Content Publishing Pipeline
```
1. New blog post is published on your website
2. Extract title and URL from blog post
3. Create Facebook post with blog summary and link
4. Log post ID for tracking
```

### Scheduled Content Calendar
```
1. Read content schedule from Google Sheets
2. For each scheduled item:
   - Get Page ID from list_pages
   - Schedule post for specified time
3. Send confirmation to content team
```

### Multi-Page Broadcasting
```
1. Trigger: New product announcement
2. Get all managed Pages via list_pages
3. For each Page:
   - Create post with announcement
4. Compile results and send report
```

## Authentication Setup

This integration uses Facebook OAuth:

1. The integration will redirect you to Facebook for authorization
2. Grant the following permissions:
   - `pages_show_list` - View your Pages
   - `pages_read_engagement` - Read Page content
   - `pages_manage_posts` - Create and manage posts
3. You'll be redirected back to Autohive with access granted

**Requirements:**
- You must be an admin or editor of the Pages you want to manage
- Pages must be published (not unpublished/draft)

## Best Practices

### Content Guidelines
- Follow Facebook's Community Standards
- Avoid excessive posting (respect your audience)
- Include engaging visuals when possible
- Use appropriate hashtags sparingly

### Scheduling Tips
- Schedule posts during peak engagement hours
- Spread content throughout the day
- Leave buffer time between scheduled posts
- Monitor scheduled posts regularly

### Performance Tips
- Cache Page IDs to avoid repeated list_pages calls
- Use meaningful post messages (avoid generic content)
- Include relevant links to drive traffic

## Troubleshooting

**Can't see your Pages?**
- Ensure you have admin or editor access to the Page
- Check that the Page is published (not in draft mode)
- Try disconnecting and reconnecting your Facebook account

**Posts not publishing?**
- Verify the Page ID is correct
- Check that your access token hasn't expired
- Ensure the Page isn't restricted or unpublished

**Scheduled posts failing?**
- Confirm the scheduled time is 10+ minutes in the future
- Ensure the scheduled time is within 30 days
- Use correct timestamp format (ISO 8601 or UNIX)

**Permission errors?**
- Reconnect your Facebook account
- Ensure you granted all required permissions
- Check if Page permissions have changed

## API Reference

This integration uses the Facebook Graph API v21.0:
- [Pages API Documentation](https://developers.facebook.com/docs/pages-api)
- [Publishing Posts](https://developers.facebook.com/docs/pages-api/posts)
- [Permissions Reference](https://developers.facebook.com/docs/permissions/reference)

## Support

Need help? Check out the [Autohive Documentation](https://docs.autohive.com) or contact support through your Autohive dashboard.
