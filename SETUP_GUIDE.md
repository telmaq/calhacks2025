# FarmFresh Weight Capture Service - Setup Guide

## Overview

This service captures weight readings from digital scale images using Claude AI and stores the data in Google Sheets.

## Required Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Claude API Configuration
CLAUDE_API_KEY=your_claude_api_key_here

# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS_FILE=path/to/your/service-account-key.json
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit

# Server Configuration
PORT=8000
```

## Setup Instructions

### 1. Claude API Setup

1. Go to https://console.anthropic.com/
2. Create an account and get your API key
3. Add the key to your `.env` file

### 2. Google Sheets Setup

1. Create a Google Cloud project at https://console.cloud.google.com/
2. Enable the Google Sheets API
3. Create a service account:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Download the JSON credentials file
4. Share your Google Sheet with the service account email (found in the JSON file)
5. Update `GOOGLE_SHEETS_URL` with your actual spreadsheet URL

### 3. Google Sheets Format

Your Google Sheet should have these columns in the first row:

- ID
- Seller ID
- Name
- Description
- Category
- Price
- Unit
- Stock
- Image URL
- Available
- Creator
- Updater
- Created
- Updated

### 4. Installation

```bash
pip install -r requirements.txt
```

### 5. Running the Service

```bash
python app.py
```

The service will be available at:

- API: http://localhost:8000/api/v1/capture/weight
- Test Interface: http://localhost:8000/test_weight_capture.html
- Documentation: http://localhost:8000/docs

## API Usage

Send a POST request to `/api/v1/capture/weight` with:

```json
{
  "farmer_id": "your_farmer_id",
  "produce_name": "Organic Tomatoes",
  "image_base64": "base64_encoded_image_data"
}
```

The service will return the captured weight data and automatically save it to your Google Sheet.
