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

### Circle

[circle](circle): Comprehensive integration with Circle.so community platform for managing posts, members, spaces, and events. Features searching and creating posts with markdown-to-TipTap conversion, member management with email search and profile access, space discovery and filtering by type, event tracking for upcoming/past community events, and comment operations for engagement. Includes comprehensive error handling, pagination support, and access to community-wide information and statistics.

### Coda

[coda](coda): Comprehensive Coda integration for managing documents, pages, tables, and rows. Supports full CRUD operations for docs (list, get, create, update, delete) and pages (list, get, create with HTML/Markdown content, update metadata, delete). Includes table and column discovery (list tables/columns, get table/column details) and complete row management (list with filtering/sorting, get, upsert with keyColumns, update, delete single/multiple). Features Bearer token authentication, pagination support, async processing (HTTP 202 responses), multiple value formats (simple/rich), and comprehensive error handling. Ideal for document automation, content management, and data synchronization workflows.

### ElevenLabs

[elevenlabs](elevenlabs): AI-powered text-to-speech integration with ElevenLabs API for voice generation and audio management. Supports converting text to realistic speech with customizable voice settings, browsing and filtering available voices by category and use case, accessing voice metadata and settings, tracking generation history, downloading previously generated audio files, and monitoring subscription usage and credits. Features 7 actions (1 paid, 6 free), API key authentication, multiple output formats (MP3, PCM), voice customization controls (stability, similarity, style), and base64-encoded audio file outputs. Includes 20 premade professional voices with various accents. Ideal for content creation, audiobook narration, voiceovers, and automated audio generation workflows.

### Front

[front](front): Customer service integration for Front's communication platform. Supports comprehensive inbox and conversation management, including listing and accessing inboxes, managing conversations and messages, creating new messages and replies through channels, accessing message templates for consistent responses, and managing conversation assignments and tags. Features channel-based message creation, conversation filtering, teammate and tag management, and complete message lifecycle operations for customer support workflows.

### Gong

[gong](gong): Integrates with Gong's conversation analytics platform to access call recordings, transcripts, and user data. Supports listing and searching calls, retrieving detailed call information and transcripts with speaker mapping, and managing user accounts. Includes comprehensive error handling and date filtering capabilities.

### Google Looker

[google-looker](google-looker): Business intelligence integration with Looker API for accessing dashboards, executing queries, and managing data models. Supports listing and retrieving dashboards with full metadata, executing LookML queries against explores with dimensions and measures, running raw SQL queries against database connections, and browsing available models and connections. Features custom authentication and comprehensive error handling for enterprise analytics workflows.

### Xero

[xero](xero): Comprehensive Xero accounting integration with OAuth 2.0 authentication. Features retrieving available tenant connections, creating and updating sales invoices and purchase bills, attaching files to invoices/bills, contact search, and comprehensive financial reporting (aged payables/receivables, balance sheet, P&L, trial balance). Includes chart of accounts access, payment records, bank transactions, robust error handling, and rate limiting.

### Zoho CRM

[Zoho](Zoho): Comprehensive Zoho CRM integration providing full customer lifecycle management capabilities. Supports complete CRUD operations across all major CRM modules including contacts, accounts, deals, leads, tasks, events, and calls. Features lead-to-deal conversion workflows, advanced relationship queries, hierarchical account structures, activity tracking, and custom COQL query execution. Includes OAuth 2.0 authentication, robust error handling, pagination support, and 33 distinct actions covering sales pipeline management, customer onboarding, and CRM automation workflows.

### Reddit

[reddit](reddit): Connect workflows to Reddit with automated engagement capabilities. Search posts across subreddits with customizable filtering options and automatically post comments to join conversations. Includes authentication via Reddit OAuth with read and submit permissions, comprehensive post data extraction, and support for brand monitoring and community engagement workflows.

### App and Business Reviews

[app-business-reviews](app-business-reviews): Unified review aggregation integration powered by SerpAPI. Access reviews from Apple App Store (iOS apps), Google Play Store (Android apps), and Google Maps (business locations) through a single integration. Supports searching for apps and places, fetching reviews with advanced sorting and filtering, pagination for large datasets, and automatic ID resolution from names. Features customizable sort orders (newest, most helpful, rating-based), platform filtering for Android apps, and flexible location-based searches. Includes comprehensive error handling with helpful Place ID guidance and single API key authentication for all three review sources.

### Supadata

[supadata](supadata): Video transcription integration that extracts text transcripts from social media videos using the Supadata API. Supports YouTube, TikTok, Instagram, and X (Twitter) platforms with timestamped SRT-format output. Ideal for content analysis, accessibility features, and creating searchable text archives from video content.

### Heartbeat

[heartbeat](heartbeat): Connects to Heartbeat.chat community platform for comprehensive access to channels, threads, comments, users, and events. Supports retrieving channel information, managing thread discussions, creating and viewing comments, accessing user profiles, and viewing community events. Includes full CRUD operations for community engagement and content management.

### Google Calendar

[google-calendar](google-calendar): Integrates with Google Calendar API for comprehensive calendar and event management within Autohive workflows. Supports listing accessible calendars, creating and managing calendar events (both timed and all-day), attendee management, and event lifecycle operations. Features secure OAuth2 authentication and pagination support for large event datasets.

### Harvest

[harvest](harvest): Time tracking and project management integration with Harvest API for logging work hours, managing projects, clients, and teams. Supports creating and managing time entries with running timers, listing and filtering time entries by project, client, user, and date range, managing projects and clients, tracking tasks and team members, and comprehensive resource management operations. Features OAuth2 authentication, flexible time logging (manual hours or running timers), pagination support for large datasets, and full CRUD operations for time entries. Includes 10 core actions covering time tracking workflows, project organization, and team collaboration.

### Google Sheets

[google-sheets](google-sheets): Connects to Google Sheets and Drive APIs to list accessible spreadsheets, read and write A1 ranges, append rows, apply formatting, freeze panes, run batch updates, and duplicate spreadsheets. Uses Google OAuth2 platform authentication with appropriate scopes for Sheets and Drive.

### Google Tasks

[google-tasks](google-tasks): Integrates with Google Tasks API for comprehensive task management within Autohive workflows. Supports listing and accessing task lists, and full CRUD operations for tasks including creating tasks with due dates and notes, managing subtasks with parent-child relationships, updating task status and properties, repositioning tasks, and filtering by completion status and date ranges. Features secure OAuth2 authentication, pagination support for large task collections (up to 2,000 lists and 20,000 tasks per list), and comprehensive error handling for productivity and workflow automation.

### Google Business Profile

[google-business-profile](google-business-profile): Connects to Google My Business API for comprehensive business profile and review management. Supports listing business accounts and locations, reading customer reviews with ratings and comments, replying to customer reviews professionally, and managing review interactions. Features secure OAuth2 authentication with Google Maps Reviews provider and comprehensive error handling for reputation management workflows.

### Microsoft 365

[microsoft365](microsoft365): Comprehensive integration with Microsoft 365 services including Outlook, OneDrive, Calendar, and SharePoint through Microsoft Graph API. Supports email management (send, draft, reply, forward, search with attachments), calendar operations (create, update, list events with date filtering), OneDrive file operations (search, read with PDF conversion), SharePoint site and document library access (search sites, list libraries, search documents across all drives, read files), and contact management. Features multi-drive SharePoint support, automatic PDF conversion for Office documents, timezone-aware calendar queries, null-safe field handling, and OAuth2 authentication with enterprise-grade permissions including Sites.Read.All for organizational knowledge base access.

### Microsoft Planner

[microsoft-planner](microsoft-planner): Comprehensive task and project management integration with Microsoft Planner via Microsoft Graph API v1.0 for organizing team work within Microsoft 365 groups. Supports complete plan lifecycle management (create, update, delete, list plans within groups), bucket organization for task categorization, full CRUD operations for tasks with assignments, due dates, priorities, categories, and progress tracking, and checklist operations within tasks. Features user lookup and search by email, group membership listing, task filtering by plan/bucket/user, task details management including descriptions and references, and board format customization for different views (assigned-to, bucket, progress). Includes automatic ETag management for optimistic concurrency control, proper assignment formatting with user GUIDs, data cleaning for read-only fields, and OAuth2 authentication with Tasks.ReadWrite and Group.ReadWrite.All scopes. Comprises 36 actions covering groups, users, plans, buckets, tasks, checklists, and board formatting. Ideal for team collaboration, project planning, task tracking, and workflow automation across Microsoft 365 workspaces.

### Spreadsheet Tools

[spreadsheet-tools](spreadsheet-tools): Tools for working with spreadsheet files including conversion to JSON format with automatic header sanitization and type inference. Supports Excel (.xlsx/.xls) and CSV file formats. Features automatic data type detection, header sanitization for valid JSON property names, duplicate header handling, and UTF-8/BOM encoding support. Ideal for data transformation, spreadsheet parsing, and converting tabular data into structured JSON for workflow automation.

### Asana

[asana](asana): Comprehensive project management integration with Asana API v1.0 for task and team collaboration automation. Supports complete task lifecycle management (create, get, update, list, delete tasks with assignees, due dates, and completion tracking), full project CRUD operations (list, get, create, update, delete projects with team associations and archiving), section organization (list, create, update sections, move tasks between sections for board/column workflows), team communication (create and list comments/stories on tasks), and subtask creation for breaking down complex work. Features Personal Access Token authentication with Bearer token headers, Asana data object wrapper handling, GID-based resource identification, and flexible task filtering. Includes 17 comprehensive actions covering tasks, projects, sections, comments, and subtasks. Ideal for workflow automation, task capture from external sources, project template creation, team collaboration, and productivity tracking across workspaces.

### Google Chat

[google-chat](google-chat): User-authenticated Google Chat integration for messaging and space management. Supports sending and managing messages with threading and @mentions, creating and managing Chat spaces, listing and reacting to messages with emojis, managing space memberships, and finding direct message conversations. Features 13 actions including full CRUD operations for messages, space management, reaction support, and OAuth2 authentication with user context. Ideal for team communication automation, notification workflows, and Chat bot alternatives using user credentials.

### Freshdesk

[freshdesk](freshdesk): Comprehensive help desk integration with Freshdesk API v2 for complete customer support operations. Supports ticket management (create, list, get, update, delete tickets with priority and status control), contact management (full CRUD operations for customer contacts with company associations), company management (create and manage organizations with domain associations), and conversation tracking (list ticket conversations, add private notes for agents, create public replies to customers). Features custom API key authentication with automatic Basic Auth encoding, pagination support for all list operations, and robust error handling. Ideal for automating support workflows, ticket routing, customer communication, and help desk operations.

### Doc Maker

[doc-maker](doc-maker): Word document automation integration with markdown-first content creation and intelligent template filling. Supports creating professional documents from markdown syntax, safely filling templates with context-aware placeholder detection, find-and-replace operations with safety checks, and adding images, tables, and formatted content. Features LLM-optimized responses, stateless file streaming for AWS Lambda deployment, and comprehensive safety mechanisms to prevent unintended content corruption. No authentication required.

### Slide Maker

[slider](slider): PowerPoint automation integration with markdown-first content creation and intelligent template filling. Supports creating professional presentations from markdown syntax with two powerful modes: auto-layout for automatic vertical content flow and granular mode for precise positioning control. Features safe template filling with placeholder metadata support (font size, color, formatting), find-and-replace with automatic font sizing and safety checks, chart creation (column, line, pie, bar, area, scatter), image insertion, and intelligent overlap detection. Includes markdown support for headings (H1-H6), bullets, tables, blockquotes, and code blocks. Features stateless file streaming for AWS Lambda deployment, comprehensive positioning validation, and graceful error handling. No authentication required.

## Template

[template-structure](template-structure) contains a structural template for new integrations, including a sample template for an appropriate README file and a basic testbed.