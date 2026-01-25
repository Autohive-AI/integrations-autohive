# Ahrefs Integration for Autohive

SEO analytics integration with Ahrefs API v3 for backlink analysis, domain ratings, keyword research, and organic traffic insights.

## Description

This integration provides access to Ahrefs' comprehensive SEO data platform for analyzing websites, backlinks, keywords, and organic search performance. It allows you to automate SEO research, competitor analysis, and link building workflows.

The integration uses Ahrefs API v3 with Bearer token authentication and implements 8 actions covering domain analysis, backlink data, organic keywords, and keyword research.

## Setup & Authentication

This integration uses **Custom Authentication** with an API key.

### Requirements

- **Ahrefs Enterprise Plan** - API access is only available on the Enterprise plan
- API requests consume API units (minimum 50 units per request)

### Setup Steps

1. Log into your Ahrefs account at ahrefs.com
2. Navigate to **Settings > API Access**
3. Click **Generate New Token**
4. Copy the token immediately (it displays only once)
5. Enter the API key when connecting the integration

### Testing Without Enterprise

Free users can test the API using only `ahrefs.com` or `wordcount.com` as targets.

## Action Results

All actions return a standardized response structure:
- `result` (boolean): Indicates whether the action succeeded (true) or failed (false)
- `error` (string, optional): Contains error message if the action failed
- Additional action-specific data fields

## Actions (8 Total)

### Domain Analysis (1 action)

#### `get_domain_rating`
Get the Domain Rating (DR) and Ahrefs Rank for a target domain.

**Inputs:**
- `target` (required): Target domain to analyze (e.g., 'example.com')

**Outputs:**
- `domain_rating`: Domain Rating score (0-100)
- `ahrefs_rank`: Ahrefs Rank position
- `result`: Success status

---

### Backlinks Analysis (3 actions)

#### `get_backlinks_stats`
Get backlink statistics for a target domain including total backlinks, referring domains, and dofollow/nofollow counts.

**Inputs:**
- `target` (required): Target domain or URL to analyze
- `mode` (optional): Analysis mode - 'exact', 'domain', 'subdomains', or 'prefix' (default: 'domain')

**Outputs:**
- `stats`: Backlink statistics object
- `result`: Success status

---

#### `get_backlinks`
Get a list of backlinks pointing to a target domain or URL.

**Inputs:**
- `target` (required): Target domain or URL to analyze
- `mode` (optional): Analysis mode - 'exact', 'domain', 'subdomains', or 'prefix'
- `limit` (optional): Maximum results (default: 100, max: 1000)
- `order_by` (optional): Sort by 'ahrefs_rank', 'domain_rating', 'url_rating', 'first_seen', or 'last_seen'

**Outputs:**
- `backlinks`: Array of backlink objects
- `result`: Success status

---

#### `get_referring_domains`
Get a list of domains that link to the target.

**Inputs:**
- `target` (required): Target domain or URL to analyze
- `mode` (optional): Analysis mode - 'exact', 'domain', 'subdomains', or 'prefix'
- `limit` (optional): Maximum results (default: 100, max: 1000)

**Outputs:**
- `referring_domains`: Array of referring domain objects
- `result`: Success status

---

### Organic Search (2 actions)

#### `get_organic_keywords`
Get organic keywords that a domain ranks for in search results.

**Inputs:**
- `target` (required): Target domain to analyze
- `country` (optional): Two-letter country code (default: 'us')
- `limit` (optional): Maximum results (default: 100, max: 1000)

**Outputs:**
- `keywords`: Array of keyword objects with rankings
- `result`: Success status

---

#### `get_top_pages`
Get the top pages of a domain by organic traffic.

**Inputs:**
- `target` (required): Target domain to analyze
- `country` (optional): Two-letter country code (default: 'us')
- `limit` (optional): Maximum results (default: 100, max: 1000)

**Outputs:**
- `pages`: Array of page objects with traffic data
- `result`: Success status

---

### Keywords Explorer (1 action)

#### `get_keyword_metrics`
Get search metrics for specific keywords including volume, difficulty, and CPC.

**Inputs:**
- `keywords` (required): Array of keywords to analyze (max 10)
- `country` (optional): Two-letter country code (default: 'us')

**Outputs:**
- `metrics`: Array of keyword metrics objects
- `result`: Success status

---

### Link Analysis (1 action)

#### `get_outgoing_links`
Get external links from a target domain or page.

**Inputs:**
- `target` (required): Target domain or URL to analyze
- `mode` (optional): Analysis mode - 'exact', 'domain', 'subdomains', or 'prefix'
- `limit` (optional): Maximum results (default: 100)

**Outputs:**
- `outgoing_links`: Array of outgoing link objects
- `result`: Success status

---

## Requirements

- `autohive-integrations-sdk` - The Autohive integrations SDK

## API Information

- **API Version**: v3
- **Base URL**: `https://api.ahrefs.com/v3`
- **Authentication**: Bearer token (API key)
- **Documentation**: https://docs.ahrefs.com/docs/api/reference/introduction

## Important Notes

- **Enterprise Only**: Ahrefs API v3 is only available to Enterprise plan subscribers
- **API Units**: All requests consume API units (minimum 50 units per request)
- **Rate Limits**: Subject to Ahrefs rate limiting policies
- **Mode Options**:
  - `exact`: Analyze only the exact URL
  - `domain`: Analyze the entire domain (excluding subdomains)
  - `subdomains`: Analyze domain including all subdomains
  - `prefix`: Analyze all URLs with the target as a prefix

## Common Use Cases

**Competitor Analysis:**
- Get domain ratings to compare authority
- Analyze competitor backlink profiles
- Find competitor's top-performing pages

**Link Building:**
- Identify referring domains
- Find backlink opportunities
- Monitor new and lost backlinks

**Keyword Research:**
- Get keyword metrics (volume, difficulty)
- Find organic keywords competitors rank for
- Discover content gaps

**SEO Auditing:**
- Analyze outgoing links
- Review backlink quality
- Track domain authority over time

## Version History

- **1.0.0** - Initial release with 8 actions
  - Domain Analysis: get_domain_rating (1 action)
  - Backlinks: get_backlinks_stats, get_backlinks, get_referring_domains (3 actions)
  - Organic Search: get_organic_keywords, get_top_pages (2 actions)
  - Keywords: get_keyword_metrics (1 action)
  - Links: get_outgoing_links (1 action)

## Sources

- [Ahrefs API Documentation](https://docs.ahrefs.com/docs/api/reference/introduction)
- [About API v3 for Enterprise Plan](https://help.ahrefs.com/en/articles/6559232-about-api-v3-for-enterprise-plan)
- [Ahrefs API Backlinks](https://docs.ahrefs.com/docs/api/site-explorer/operations/list-all-backlinks)
