# Luma Integration

Luma integration for Autohive - manage events, guests, invitations, and registrations on the Luma event platform.

## Overview

[Luma](https://lu.ma) is an event management platform for hosting virtual and in-person events. This integration allows Autohive users to:

- **Event Management**: Create, update, and list events
- **Guest Management**: View registrations, add guests, approve/decline RSVPs
- **Invitations**: Send email invitations to potential attendees
- **Tickets & Coupons**: Manage ticket types and discount codes for paid events
- **Calendar Operations**: List all events and people associated with your calendar

## Authentication

Luma uses API key authentication. Users need:

1. A **Luma Plus** subscription (required for API access)
2. An API key from their Luma Calendar settings

### Getting an API Key

1. Go to [Luma Calendars](https://luma.com/home/calendars)
2. Select your calendar
3. Navigate to **Settings → Developer**
4. Find the **API Keys** section and generate a key
5. Copy and securely store the key

⚠️ **Important**: The API key grants full access to your Luma account. Keep it secure and never share publicly.

## Available Actions

### Event Actions

| Action | Description |
|--------|-------------|
| `get_self` | Get authenticated user info (verify API key) |
| `get_events` | Get events - pass `event_api_id` for a single event, omit to list all |
| `create_event` | Create a new event with name, time, location, etc. |
| `update_event` | Update an existing event's details |

### Guest Actions

| Action | Description |
|--------|-------------|
| `get_guests` | Get guests - pass `guest_api_id` for a single guest, omit to list all |
| `add_guests` | Add guests to an event (auto-register) |
| `update_guest_status` | Approve, decline, or set guest to pending |
| `send_invites` | Send email invitations to a list of addresses |

### Ticket & Coupon Actions

| Action | Description |
|--------|-------------|
| `list_ticket_types` | Get all ticket types for an event |
| `create_ticket_type` | Create a new ticket type (for paid events) |
| `list_coupons` | Get all discount coupons for an event |
| `create_coupon` | Create a discount coupon |

### Calendar Actions

| Action | Description |
|--------|-------------|
| `list_people` | List all people/contacts in your calendar |

## Example Use Cases

### 1. Automated Event Creation
Create events programmatically when a new meeting is scheduled or campaign launches.

### 2. Guest List Sync
Keep external CRM or email lists synced with event registrations.

### 3. Bulk Invitations
Send personalized invitations to a list of contacts from your marketing database.

### 4. Registration Approval Workflow
Automatically approve guests who meet certain criteria (e.g., verified email domain).

### 5. Ticket Sales Tracking
Monitor ticket sales and automatically create discount codes based on sales milestones.

## API Rate Limits

Luma enforces a rate limit of **300 requests per minute** across all endpoints. If you exceed this limit, you'll be locked out for one minute.

Best practices:
- Batch operations when possible
- Use pagination cursors instead of re-fetching
- Implement exponential backoff for retries

## Development

### Running Tests

```bash
cd luma
pytest tests/
```

### Project Structure

```
luma/
├── actions/
│   ├── __init__.py
│   ├── events.py      # Event CRUD, tickets, coupons
│   ├── guests.py      # Guest management
│   └── calendar.py    # Calendar-level operations
├── tests/
│   ├── context.py
│   └── test_luma.py
├── config.json        # Integration configuration
├── helpers.py         # Shared utilities
├── luma.py           # Entry point
├── README.md
└── requirements.txt
```

## Resources

- [Luma API Documentation](https://docs.lu.ma)
- [Luma Help Center](https://help.luma.com/p/luma-api)
- [Luma Plus Pricing](https://luma.com/pricing)
