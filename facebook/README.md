# Facebook Pages Integration

Complete Facebook Pages management for Autohive. Manage posts, comments, insights, groups, and events from a unified interface.

## Features

| Category | Capabilities |
|----------|-------------|
| **Pages** | Discover and list all manageable pages |
| **Posts** | Create, retrieve, schedule, and delete posts (text, photo, video, link) |
| **Comments** | Read comments, reply, hide/unhide, delete |
| **Insights** | Page-level and post-level analytics |
| **Groups** | List groups and create group posts |
| **Events** | List, create, and update page events |

## Actions

### Page Discovery

#### `list_pages`
Discover all Facebook Pages you can manage.

**Outputs:** Page ID, name, category, follower count

---

### Posts

#### `get_posts`
Retrieve posts from a page. Fetch a single post or list recent posts.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `page_id` | Yes | The Facebook Page ID |
| `post_id` | No | Specific post ID (omit to list all) |
| `limit` | No | Max posts to return (default: 25) |

#### `create_post`
Publish content to a page. Supports multiple media types and scheduling.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `page_id` | Yes | The Facebook Page ID |
| `message` | Yes | Post text content |
| `media_type` | No | `text`, `photo`, `video`, or `link` (default: text) |
| `media_url` | No* | URL of media (*required for photo/video/link) |
| `scheduled_time` | No | ISO 8601 timestamp to schedule post |

#### `delete_post`
Permanently delete a post. **Cannot be undone.**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `page_id` | Yes | The Facebook Page ID |
| `post_id` | Yes | The post ID to delete |

---

### Comments

#### `get_comments`
Retrieve comments on a post.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `post_id` | Yes | The post ID |
| `limit` | No | Max comments to return (default: 25) |
| `include_hidden` | No | Include hidden comments (default: false) |

#### `manage_comment`
Interact with comments: reply, hide, or unhide.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `comment_id` | Yes | The comment ID |
| `action` | Yes | `reply`, `hide`, or `unhide` |
| `message` | No* | Reply text (*required for reply action) |

#### `delete_comment`
Permanently delete a comment. **Cannot be undone.**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `comment_id` | Yes | The comment ID to delete |

---

### Insights

#### `get_insights`
Retrieve analytics for a page or post.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `target_type` | Yes | `page` or `post` |
| `target_id` | Yes | The page or post ID |
| `metrics` | No | Specific metrics to retrieve |
| `period` | No | `day`, `week`, or `days_28` (page only) |

**Default Page Metrics:**
- `page_impressions`, `page_engaged_users`, `page_post_engagements`
- `page_fans`, `page_fan_adds`, `page_views_total`

**Default Post Metrics:**
- `post_impressions`, `post_impressions_unique`, `post_engaged_users`
- `post_clicks`, `post_reactions_by_type_total`

---

### Groups

#### `get_groups`
List Facebook Groups you can post to.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `limit` | No | Max groups to return (default: 25) |

#### `create_group_post`
Publish a post to a group.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `group_id` | Yes | The group ID |
| `message` | Yes | Post text content |
| `media_url` | No | Photo URL or link to include |

---

### Events

#### `get_events`
List events for a page.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `page_id` | Yes | The Facebook Page ID |
| `time_filter` | No | `upcoming`, `past`, or `all` (default: upcoming) |
| `limit` | No | Max events to return (default: 25) |

#### `manage_event`
Create a new event or update an existing one.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `page_id` | Yes | The Facebook Page ID |
| `event_id` | No | Event ID to update (omit to create new) |
| `name` | No* | Event name (*required for new events) |
| `start_time` | No* | ISO 8601 timestamp (*required for new events) |
| `end_time` | No | Event end time |
| `description` | No | Event description |
| `place` | No | Location name or address |
| `is_online` | No | Whether this is an online event |

---

## Required Permissions

This integration requires the following Facebook permissions:

| Scope | Purpose |
|-------|---------|
| `pages_show_list` | List manageable pages |
| `pages_read_engagement` | Read page engagement data |
| `pages_read_user_content` | Read comments |
| `pages_manage_posts` | Create and delete posts |
| `pages_manage_engagement` | Reply to and manage comments |
| `pages_manage_metadata` | Manage events |
| `read_insights` | Access page and post analytics |
| `groups_access_member_info` | List groups |
| `publish_to_groups` | Post to groups |

---

## API Version

This integration uses Facebook Graph API **v21.0**.
