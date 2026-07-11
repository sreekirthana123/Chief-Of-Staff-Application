# Deployment Guide

## Setting up Streamlit Cloud

### 1. Environment Variables
In your Streamlit Cloud app settings, add these secrets:

```toml
# .streamlit/secrets.toml format (for reference - actual setup is in the web interface)

# Gemini AI API Key
GEMINI_API_KEY = "your_gemini_api_key_here"

# Google OAuth Credentials (from your Google Cloud Console credentials.json file)
[google_credentials]
client_id = "your_client_id.apps.googleusercontent.com"
project_id = "your_project_id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_secret = "your_client_secret"
redirect_uris = ["http://localhost"]

# Google OAuth Token (REQUIRED for Gmail features in cloud)
[google_token]
token = "your_access_token"
refresh_token = "your_refresh_token"
token_uri = "https://oauth2.googleapis.com/token"
client_id = "your_client_id.apps.googleusercontent.com"
client_secret = "your_client_secret"
scopes = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/calendar"]
```

### 2. How to Get Google Token (CRITICAL for Cloud Deployment)

**Step 1: Get OAuth Credentials**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable these APIs:
   - Gmail API
   - Google Calendar API
4. Go to "Credentials" → "Create Credentials" → "OAuth client ID"
5. Choose "Desktop application"
6. Download the JSON file - this contains the values for `[google_credentials]`

**Step 2: Generate Token Locally**
1. Run the app locally with your `credentials.json` file
2. Complete the Google OAuth login when prompted
3. This creates a `token.json` file in your project directory
4. Open `token.json` - it contains the values you need for `[google_token]`

**Step 3: Add Token to Streamlit Secrets**
Copy the values from your `token.json` file to the `[google_token]` section in Streamlit Cloud secrets.

Example `token.json` content:
```json
{
  "token": "ya29.a0AfH6SMBr...",
  "refresh_token": "1//04xxx...",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "123456789.apps.googleusercontent.com",
  "client_secret": "GOCSPX-abc123...",
  "scopes": ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/calendar"]
}
```

### 3. Setting Secrets in Streamlit Cloud

1. Deploy your app to Streamlit Cloud
2. Go to your app dashboard
3. Click "Settings" → "Secrets"
4. Add the secrets in TOML format as shown above
5. Replace the placeholder values with your actual credentials

### 4. Local Development

For local development, you can still use:
- `.env` file for environment variables
- `credentials.json` file for Google OAuth (place in project root)

The code will automatically fall back to file-based credentials when Streamlit secrets are not available.

## File Structure for Deployment

Make sure these files are in your repository root:
- `app.py` (main Streamlit app)
- `requirements.txt` (dependencies)
- `triage.py` (AI triage functions)
- `engine.py` (Gmail API functions)
- `calendar_engine.py` (Calendar API functions)
- `task_logger.py` (logging functions)
- `draft_machine.py` (draft generation)
- `.streamlit/config.toml` (Streamlit configuration)

## Testing the Deployment

1. Check that all dependencies install correctly
2. Verify environment variables are set
3. Test the Google OAuth flow works in the cloud environment
4. Ensure all features work as expected

The app will handle both development (file-based) and production (secrets-based) credential loading automatically.