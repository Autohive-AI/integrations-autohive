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

### Supadata

[supadata](supadata): Video transcription integration that extracts text transcripts from social media videos using the Supadata API. Supports YouTube, TikTok, Instagram, and X (Twitter) platforms with timestamped SRT-format output. Ideal for content analysis, accessibility features, and creating searchable text archives from video content.

### Heartbeat

[heartbeat](heartbeat): Connects to Heartbeat.chat community platform for comprehensive access to channels, threads, comments, users, and events. Supports retrieving channel information, managing thread discussions, creating and viewing comments, accessing user profiles, and viewing community events. Includes full CRUD operations for community engagement and content management.

### Google Calendar

[google-calendar](google-calendar): Integrates with Google Calendar API for comprehensive calendar and event management within Autohive workflows. Supports listing accessible calendars, creating and managing calendar events (both timed and all-day), attendee management, and event lifecycle operations. Features secure OAuth2 authentication and pagination support for large event datasets.

### Google Sheets

[google-sheets](google-sheets): Connects to Google Sheets and Drive APIs to list accessible spreadsheets, read and write A1 ranges, append rows, apply formatting, freeze panes, run batch updates, and duplicate spreadsheets. Uses Google OAuth2 platform authentication with appropriate scopes for Sheets and Drive.

### Google Business Profile

[google-business-profile](google-business-profile): Connects to Google My Business API for comprehensive business profile and review management. Supports listing business accounts and locations, reading customer reviews with ratings and comments, replying to customer reviews professionally, and managing review interactions. Features secure OAuth2 authentication with Google Maps Reviews provider and comprehensive error handling for reputation management workflows.

### Microsoft 365

[microsoft365](microsoft365): Comprehensive integration with Microsoft 365 services including Outlook, OneDrive, Calendar, and SharePoint through Microsoft Graph API. Supports email management (send, draft, reply, forward, search with attachments), calendar operations (create, update, list events with date filtering), OneDrive file operations (search, read with PDF conversion), SharePoint site and document library access (search sites, list libraries, search documents across all drives, read files), and contact management. Features multi-drive SharePoint support, automatic PDF conversion for Office documents, timezone-aware calendar queries, null-safe field handling, and OAuth2 authentication with enterprise-grade permissions including Sites.Read.All for organizational knowledge base access.

### Spreadsheet Tools

[spreadsheet-tools](spreadsheet-tools): Tools for working with spreadsheet files including conversion to JSON format with automatic header sanitization and type inference. Supports Excel (.xlsx/.xls) and CSV file formats. Features automatic data type detection, header sanitization for valid JSON property names, duplicate header handling, and UTF-8/BOM encoding support. Ideal for data transformation, spreadsheet parsing, and converting tabular data into structured JSON for workflow automation.

### Doc Maker

[doc-maker](doc-maker): Word document automation integration with markdown-first content creation and intelligent template filling. Supports creating professional documents from markdown syntax, safely filling templates with context-aware placeholder detection, find-and-replace operations with safety checks, and adding images, tables, and formatted content. Features LLM-optimized responses, stateless file streaming for AWS Lambda deployment, and comprehensive safety mechanisms to prevent unintended content corruption. No authentication required.

## Template

[template-structure](template-structure) contains a structural template for new integrations, including a sample template for an appropriate README file and a basic testbed.