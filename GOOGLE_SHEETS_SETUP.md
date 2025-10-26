# Google Sheets Integration Setup Guide

## Environment Variables Required

Create a `.env` file in the project root with the following variables:

```bash
# Claude API Configuration
CLAUDE_API_KEY=your_claude_api_key_here

# Supabase Configuration (optional)
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_FILE=path/to/your/service-account-key.json
GOOGLE_SHEETS_ID=your_google_sheets_id_here

# API Security
API_KEY=your-secret-api-key-here

# Server Configuration
PORT=8000
```

## Google Sheets Setup

1. **Create a Google Cloud Project**:

   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Google Sheets API**:

   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API" and enable it

3. **Create Service Account**:

   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Give it a name (e.g., "farmfresh-sheets")
   - Create and download the JSON key file

4. **Share Google Sheet**:

   - Open your Google Sheet
   - Click "Share" button
   - Add the service account email (found in the JSON key file)
   - Give it "Editor" permissions

5. **Get Sheet ID**:
   - The Sheet ID is in the URL: `https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit`

## Usage

### URL Parameters

The webcam client now accepts farmer ID from URL parameters:

- `?farmer_id=12345` or `?farmerid=12345`

### Example URLs

```
http://localhost:8000/webcam_client.html?farmer_id=100019a1edcbeed766ea9c19842fdcfa5f1
```

### Features

- **Live Camera Feed**: Real-time produce detection using YOLOv8
- **Automatic Produce Detection**: AI identifies produce types
- **Weight Capture**: Uses Claude AI to read weight from digital scales
- **Google Sheets Integration**: Automatically writes captured data to your sheet
- **Farmer ID Pre-population**: Gets farmer ID from URL parameters

### Data Format Written to Google Sheets

The system writes data in this format:

- ID: Auto-generated UUID
- Seller ID: Farmer ID from URL parameter
- Name: Detected produce name
- Description: Auto-generated description
- Category: "vegetables" (default)
- Price: Weight value from scale
- Unit: Weight unit (g, kg, etc.)
- Stock: 1 (default)
- Image URL: null
- Available: TRUE
- Creator: Farmer ID
- Updater: Farmer ID
- Created: Current timestamp
- Updated: Current timestamp

## Testing

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set up your `.env` file with the required credentials

3. Run the application:

   ```bash
   python app.py
   ```

4. Open the webcam client with a farmer ID:

   ```
   http://localhost:8000/webcam_client.html?farmer_id=test_farmer_123
   ```

5. Click "Start Camera" to begin detection
6. When produce is detected, click "Capture Produce" to save to Google Sheets
