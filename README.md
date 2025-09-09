# Integrations by Autohive
This repository hosts Autohive integrations made and maintained by the Autohive team.

## Integrations

### Notion

[notion](notion): Enhanced integration with Notion API featuring comprehensive workspace management capabilities. Supports searching pages and databases, querying database entries with advanced filtering, creating and managing pages, updating page properties, retrieving and modifying block content, and managing database schemas. Includes robust error handling and pagination support for large datasets.

### RSS Reader 

[rss-reader-feedparser](rss-reader-feedparser): Reads RSS feeds using the `feedparser` library.

[rss-reader-feedparser-ah-fetch](rss-reader-feedparser-ah-fetch): Reads RSS feeds using `feedparser` and the `autohive-integration-sdk`'s `fetch()` method for HTTP requests. 

Supports basic HTTP authentication and Bearer token authentication via the SDK.

### Google Ads

[adwords_tool](adwords_tool): Fetches campaign data from the Google Ads API using the `google-ads` library. The scope can currently perform all CRUD operations. 

### Box

[box](box): Manages files and folders in Box cloud storage. Supports listing shared folders, searching files, downloading file contents, uploading files, and browsing folder contents with recursive support.

### Gong

[gong](gong): Integrates with Gong's conversation analytics platform to access call recordings, transcripts, and user data. Supports listing and searching calls, retrieving detailed call information and transcripts with speaker mapping, and managing user accounts. Includes comprehensive error handling and date filtering capabilities.

### Google Looker

[google-looker](google-looker): Business intelligence integration with Looker API for accessing dashboards, executing queries, and managing data models. Supports listing and retrieving dashboards with full metadata, executing LookML queries against explores with dimensions and measures, running raw SQL queries against database connections, and browsing available models and connections. Features custom authentication and comprehensive error handling for enterprise analytics workflows.

### Xero

[xero](xero): Integration for accessing Xero accounting reports and contact data through OAuth 2.0 authentication. Features retrieving available tenant connections, contact search by name within tenants, and retrieval of comprehensive accounting reports including aged payables, aged receivables, balance sheets, profit & loss statements, and trial balances. Supports optional date parameters and period comparisons for financial reporting.

### Reddit

[reddit](reddit): Connect workflows to Reddit with automated engagement capabilities. Search posts across subreddits with customizable filtering options and automatically post comments to join conversations. Includes authentication via Reddit OAuth with read and submit permissions, comprehensive post data extraction, and support for brand monitoring and community engagement workflows.

### Supadata

[supadata](supadata): Video transcription integration that extracts text transcripts from social media videos using the Supadata API. Supports YouTube, TikTok, Instagram, and X (Twitter) platforms with timestamped SRT-format output. Ideal for content analysis, accessibility features, and creating searchable text archives from video content.

### Heartbeat

[heartbeat](heartbeat): Connects to Heartbeat.chat community platform for comprehensive access to channels, threads, comments, users, and events. Supports retrieving channel information, managing thread discussions, creating and viewing comments, accessing user profiles, and viewing community events. Includes full CRUD operations for community engagement and content management.

### Google Calendar

[google-calendar](google-calendar): Integrates with Google Calendar API for comprehensive calendar and event management within Autohive workflows. Supports listing accessible calendars, creating and managing calendar events (both timed and all-day), attendee management, and event lifecycle operations. Features secure OAuth2 authentication and pagination support for large event datasets.

## Template

[template-structure](template-structure) contains a structural template for new integrations, including a sample template for an appropriate README file and a basic testbed.
