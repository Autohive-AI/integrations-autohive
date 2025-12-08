# Grammarly Integration

Grammarly integration for writing quality assessment, AI detection, plagiarism checking, and analytics.

## Features

### Writing Score API
- Create writing score requests
- Upload documents for analysis
- Retrieve detailed writing quality metrics (engagement, correctness, delivery, clarity)

### Analytics API
- Retrieve user analytics and usage statistics
- Track active days, sessions, and improvements
- Monitor AI prompt usage

### AI Detection API (Beta)
- Detect AI-generated content
- Get confidence scores and AI-generated percentage
- Support for multiple file formats

### Plagiarism Detection API (Beta)
- Check for plagiarism against billions of sources
- Get originality scores
- Identify matching content

## Authentication

This integration uses OAuth2 client credentials flow. You'll need:

- **Client ID**: Your Grammarly API Client ID
- **Client Secret**: Your Grammarly API Client Secret

The integration automatically requests all necessary scopes for full API access:
- `scores-api:read` and `scores-api:write` - Writing Score API
- `analytics-api:read` - Analytics API
- `ai-detection-api:read` and `ai-detection-api:write` - AI Detection API
- `plagiarism-api:read` and `plagiarism-api:write` - Plagiarism Detection API

## Actions

### Writing Score Actions

#### create_writing_score_request
Create a new writing score request.
- **Input**: `filename` (string)
- **Output**: `score_request_id`, `file_upload_url`

#### upload_document_for_writing_score
Upload a document to the pre-signed URL.
- **Input**: `upload_url` (string), `file_content` (string)
- **Output**: Success confirmation

#### get_writing_score_results
Get the results of a writing score request.
- **Input**: `score_request_id` (string)
- **Output**: Status and scores (when completed)

### Analytics Actions

#### get_user_analytics
Retrieve user analytics for a date range.
- **Input**: `date_from` (YYYY-MM-DD), `date_to` (YYYY-MM-DD), optional `cursor` and `limit`
- **Output**: List of users with analytics data and pagination info

### AI Detection Actions

#### create_ai_detection_request
Create a new AI detection request.
- **Input**: `filename` (string)
- **Output**: `score_request_id`, `file_upload_url`

#### upload_document_for_ai_detection
Upload a document for AI detection.
- **Input**: `upload_url` (string), `file_content` (string)
- **Output**: Success confirmation

#### get_ai_detection_results
Get AI detection results.
- **Input**: `score_request_id` (string)
- **Output**: Status, confidence score, and AI-generated percentage

### Plagiarism Detection Actions

#### create_plagiarism_detection_request
Create a new plagiarism detection request.
- **Input**: `filename` (string)
- **Output**: `score_request_id`, `file_upload_url`

#### upload_document_for_plagiarism_detection
Upload a document for plagiarism detection.
- **Input**: `upload_url` (string), `file_content` (string)
- **Output**: Success confirmation

#### get_plagiarism_detection_results
Get plagiarism detection results.
- **Input**: `score_request_id` (string)
- **Output**: Status, originality score, and plagiarism percentage

## Technical Details

### API Endpoints

- Token URL: `https://auth.grammarly.com/v4/api/oauth2/token`
- Writing Score API: `https://api.grammarly.com/ecosystem/api/v2/scores`
- Analytics API: `https://api.grammarly.com/ecosystem/api/v2/analytics/users`
- AI Detection API: `https://api.grammarly.com/ecosystem/api/v1/ai-detection`
- Plagiarism API: `https://api.grammarly.com/ecosystem/api/v1/plagiarism`

### Rate Limits

- POST requests: 10 requests per second
- GET requests: 50 requests per second

### File Constraints

- Maximum file size: 4MB
- Maximum text length: 100,000 characters
- Minimum text length: 30 words (for scoring)
- Supported formats: .doc, .docx, .odt, .txt, .rtf

### Data Retention

- Score results: Available for 30 days
- Uploaded documents: Retained for maximum 24 hours

## Testing

To test the integration:

1. Update the credentials in `tests/test_grammarly.py`
2. Replace placeholder values for `CLIENT_ID` and `CLIENT_SECRET`
3. Run the tests: `python tests/test_grammarly.py`

## Resources

- [Grammarly Developer Documentation](https://developer.grammarly.com/)
- [OAuth 2.0 Credentials Guide](https://developer.grammarly.com/oauth-credentials.html)
- [API Documentation](https://developer.grammarly.com/)

## Version

1.0.0
