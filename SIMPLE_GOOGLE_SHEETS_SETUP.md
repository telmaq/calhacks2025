# Google Sheets Integration Setup (Standard API)

## Standard Google Sheets API Setup

This uses the official Google Sheets API with service account authentication - the most reliable and secure approach.

### Step 1: Create Google Cloud Project

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Create a new project** or select an existing one
3. **Note your project ID**

### Step 2: Enable Google Sheets API

1. **Go to "APIs & Services" > "Library"**
2. **Search for "Google Sheets API"**
3. **Click on it and press "Enable"**

### Step 3: Create Service Account

1. **Go to "APIs & Services" > "Credentials"**
2. **Click "Create Credentials" > "Service Account"**
3. **Fill in the details:**
   - Service account name: `farmfresh-sheets`
   - Service account ID: `farmfresh-sheets@your-project.iam.gserviceaccount.com`
   - Description: `Service account for FarmFresh Google Sheets integration`
4. **Click "Create and Continue"**
5. **Skip the optional steps and click "Done"**

### Step 4: Generate Service Account Key

1. **In the Credentials page, find your service account**
2. **Click on the service account email**
3. **Go to "Keys" tab**
4. **Click "Add Key" > "Create new key"**
5. **Choose "JSON" format**
6. **Click "Create"**
7. **Download the JSON file** (keep it secure!)

### Step 5: Share Google Sheet with Service Account

1. **Open your Google Sheet**
2. **Click "Share" button**
3. **Add the service account email** (from the JSON file, looks like `farmfresh-sheets@your-project.iam.gserviceaccount.com`)
4. **Give it "Editor" permissions**
5. **Click "Send"**

### Step 6: Get Google Sheet ID

1. **Open your Google Sheet**
2. **Copy the Sheet ID from the URL:**
   ```
   https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
   ```
3. **The Sheet ID is the long string between `/d/` and `/edit`**

### Step 7: Configure Environment Variables

Create a `.env` file in your project root:

```bash
# Claude API Configuration
CLAUDE_API_KEY=your_claude_api_key_here

# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_FILE=path/to/your/service-account-key.json
GOOGLE_SHEETS_ID=your_google_sheets_id_here

# API Security
API_KEY=your-secret-api-key-here

# Server Configuration
PORT=8000
```

### Step 8: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 9: Test the Integration

1. **Run the application:**

   ```bash
   python app.py
   ```

2. **Open the webcam client with a farmer ID:**

   ```
   http://localhost:8000/webcam_client.html?farmer_id=test_farmer_123
   ```

3. **Click "Start Camera" to begin detection**
4. **When produce is detected, click "Capture Produce"**
5. **Check your Google Sheet - data should appear automatically!**

## Data Format

The system writes data in exactly the format you specified:

- **ID**: Auto-generated UUID
- **Seller ID**: Farmer ID from URL parameter
- **Name**: Detected produce name
- **Description**: Auto-generated description
- **Category**: "vegetables" (default)
- **Price**: Weight value from scale
- **Unit**: Weight unit (g, kg, etc.)
- **Stock**: 1 (default)
- **Image URL**: null
- **Available**: TRUE
- **Creator**: Farmer ID
- **Updater**: Farmer ID
- **Created**: Current timestamp
- **Updated**: Current timestamp

## Troubleshooting

- **"Google Sheets service not initialized"**: Check your credentials file path and Sheet ID
- **"Permission denied"**: Make sure you shared the sheet with the service account email
- **"Sheet not found"**: Verify the Sheet ID is correct
- **"Invalid credentials"**: Check that the JSON key file is valid and not corrupted

This is the standard, reliable way to integrate with Google Sheets!
