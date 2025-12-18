# Gemini Deep Research Integration

Autonomous AI research agent powered by Google Gemini 2.0 Pro. This integration enables multi-step research tasks with web search, content synthesis, and comprehensive report generation.

## Overview

The Gemini Deep Research agent autonomously:
- Plans research strategy based on your query
- Searches the web using Google Search
- Reads and analyzes multiple sources
- Synthesizes findings into comprehensive reports
- Supports follow-up questions for deeper exploration

## Authentication

This integration requires a **Google AI Studio API key**.

### Getting Your API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

### Configuration

Add your API key in Autohive when connecting the integration:

| Field | Description |
|-------|-------------|
| Gemini API Key | Your Google AI Studio API key |

## Actions

### 1. Start Deep Research

Initiates an autonomous research task. Returns an interaction ID for polling results.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | string | Yes | The research question or topic (max 10,000 chars) |
| output_format | string | No | Formatting instructions (e.g., "bullet points", "academic style") |
| enable_file_search | boolean | No | Enable searching uploaded files (default: false) |

**Outputs:**
| Field | Type | Description |
|-------|------|-------------|
| interaction_id | string | ID to poll for results |
| status | string | Current status (in_progress, completed, failed) |
| result | boolean | Whether the action succeeded |

**Example:**
```json
{
  "query": "What are the latest developments in quantum computing?",
  "output_format": "structured with sections, bullet points, and citations"
}
```

### 2. Get Research Status

Polls for research completion and retrieves results.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| interaction_id | string | Yes | The interaction ID from Start Deep Research |

**Outputs:**
| Field | Type | Description |
|-------|------|-------------|
| status | string | Current status (in_progress, completed, failed) |
| research_output | string | The full research report (when completed) |
| result | boolean | Whether the action succeeded |

### 3. Continue Research

Ask follow-up questions on a completed research task.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| previous_interaction_id | string | Yes | The completed research interaction ID |
| follow_up_query | string | Yes | Your follow-up question |
| output_format | string | No | Formatting instructions for the response |

**Outputs:**
| Field | Type | Description |
|-------|------|-------------|
| interaction_id | string | New interaction ID for the follow-up |
| status | string | Current status |
| result | boolean | Whether the action succeeded |

### 4. Get Research with Thought Updates

Get research status with intermediate thinking summaries for progress tracking.

**Inputs:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| interaction_id | string | Yes | The interaction ID from Start Deep Research |
| include_thoughts | boolean | No | Include thinking summaries (default: true) |

**Outputs:**
| Field | Type | Description |
|-------|------|-------------|
| status | string | Current status |
| research_output | string | The full research report (when completed) |
| thought_summaries | array | List of intermediate progress updates |
| result | boolean | Whether the action succeeded |

## Usage Pattern

Since deep research is asynchronous and can take up to 60 minutes, use this polling pattern:

```
1. Call "Start Deep Research" with your query
2. Save the returned interaction_id
3. Poll "Get Research Status" every 10-30 seconds
4. When status is "completed", retrieve the research_output
5. Optionally use "Continue Research" for follow-up questions
```

## Limitations

- **Maximum research time**: 60 minutes per task
- **Async only**: Results must be polled (no synchronous mode)
- **Beta API**: Schema may change in future versions
- **No custom tools**: Cannot use custom function calling tools
- **Web search only**: Google Search for web research (free until Jan 5, 2026)

## Example Workflow

### Basic Research
```
Step 1: Start Research
  Input: "What are the environmental impacts of electric vehicles vs gasoline cars?"
  Output: { interaction_id: "abc123", status: "in_progress" }

Step 2: Poll Status (repeat until completed)
  Input: { interaction_id: "abc123" }
  Output: { status: "in_progress" } ... { status: "completed", research_output: "..." }

Step 3: Follow-up (optional)
  Input: { previous_interaction_id: "abc123", follow_up_query: "Focus on battery recycling" }
  Output: { interaction_id: "def456", status: "in_progress" }
```

## Error Handling

All actions return a `result` boolean and optional `error` string:

```json
{
  "result": false,
  "error": "Invalid API key",
  "status": "failed"
}
```

Common errors:
- **Invalid API key**: Check your API key is correct
- **Rate limited**: Wait and retry
- **Research timeout**: Research exceeded 60 minutes
- **Invalid interaction ID**: The ID doesn't exist or has expired

## Pricing

- **Google Search**: Free until January 5, 2026
- **Gemini API**: See [Google AI pricing](https://ai.google.dev/pricing) for current rates

## Development

### Running Tests

```bash
# Set your API key
export GEMINI_API_KEY="your-api-key"

# Run tests
cd gemini-deep-research
pytest tests/ -v
```

### Manual Testing

```bash
# Run a full research test with polling
python tests/test_gemini_deep_research.py
```

## Support

For issues with this integration, please check:
1. Your API key is valid and has sufficient quota
2. The query is within character limits
3. You're polling with appropriate intervals (10-30 seconds)

For Gemini API issues, see [Google AI documentation](https://ai.google.dev/gemini-api/docs/deep-research).
