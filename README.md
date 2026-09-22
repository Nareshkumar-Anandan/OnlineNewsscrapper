# Online News Scraper - Backend

Flask API backend for fetching and exporting news articles.

## Features
- NewsAPI integration for reliable news data
- Web scraping fallback for additional sources
- Excel export with comprehensive article details
- RESTful API endpoints
- CORS enabled for frontend access

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get NewsAPI Key:**
   - Sign up at: https://newsapi.org/register
   - Get your free API key (100 requests/day)

3. **Configure Environment:**
   ```bash
   # Copy the example file
   copy .env.example .env
   
   # Edit .env and add your API key
   NEWS_API_KEY=your_actual_api_key_here
   ```

## Usage

**Start the server:**
```bash
python app.py
```

Server will start on http://localhost:5000

## API Endpoints

### POST /api/search
Search for news articles.

**Request:**
```json
{
  "query": "technology",
  "max_results": 100
}
```

**Response:**
```json
{
  "search_id": "uuid",
  "query": "technology",
  "count": 100,
  "articles": [...]
}
```

### GET /api/export/<search_id>
Export search results to Excel file.

**Response:** Excel file download

### GET /api/health
Check API health and configuration status.

## Article Data Structure
Each article contains:
- `title` - Article headline
- `description` - Brief summary
- `url` - Link to full article
- `published_date` - Publication date
- `author` - Article author
- `source` - News source name
- `image_url` - Featured image URL
- `content` - Article preview

## Testing

Test the scraper module independently:
```bash
python scraper.py
```

This will fetch 10 test articles and create a test Excel file.

## Troubleshooting

**"NEWS_API_KEY not found" error:**
- Make sure you created the `.env` file (not `.env.example`)
- Verify the API key is correctly set in `.env`

**"No module named 'flask'" error:**
- Run: `pip install -r requirements.txt`

**Articles not fetching:**
- Check your internet connection
- Verify your NewsAPI key is valid
- Check NewsAPI quota (free tier: 100 requests/day)
