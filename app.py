"""
Flask API for Online News Scraper
Provides endpoints for searching news and exporting to Excel
"""

import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from scraper import NewsScraper

# Load environment variables
load_dotenv()

# Frontend directory path
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Frontend'))

# Initialize Flask app (serving Frontend static files when hosted together)
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)  # Enable CORS for frontend access

# Initialize news scraper
API_KEY = os.getenv('NEWS_API_KEY')
IS_PLACEHOLDER = API_KEY == "your_newsapi_key_here"

if not API_KEY or IS_PLACEHOLDER:
    print(f"\n{'!'*50}")
    if IS_PLACEHOLDER:
        print("WARNING: NEWS_API_KEY is still the placeholder value!")
        print("Please update NEWS_API_KEY in .env with a real key from newsapi.org")
    else:
        print("WARNING: NEWS_API_KEY not found in .env file!")
    print(f"{'!'*50}\n")
    # Reset API_KEY to None if it's the placeholder so the scraper knows to use fallback
    if IS_PLACEHOLDER:
        API_KEY = None

scraper = NewsScraper(API_KEY)

# Store search results temporarily (in production, use Redis or database)
search_cache = {}


@app.route('/')
def home():
    """API home endpoint / Serves Frontend web application if available"""
    index_file = os.path.join(FRONTEND_DIR, 'index.html')
    if os.path.exists(index_file):
        return send_file(index_file)
    return jsonify({
        'message': 'Online News Scraper API',
        'version': '1.0',
        'endpoints': {
            'search': '/api/search (POST)',
            'export': '/api/export/<search_id> (GET)',
            'details': '/api/details (POST)',
            'health': '/api/health (GET)'
        }
    })


@app.route('/api/search', methods=['POST'])
def search_news():
    """
    Search for news articles
    
    Request body:
    {
        "query": "search term",
        "max_results": 100  (optional, default: 100)
    }
    
    Returns:
    {
        "search_id": "unique_id",
        "query": "search term",
        "count": 100,
        "articles": [...]
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Missing required field: query'
            }), 400
        
        query = data['query'].strip()
        max_results = data.get('max_results', 100)
        page = data.get('page', 1)
        
        if not query:
            return jsonify({
                'error': 'Query cannot be empty'
            }), 400
        
        # Validate max_results and page
        if not isinstance(max_results, int) or max_results < 1 or max_results > 500:
            return jsonify({
                'error': 'max_results must be between 1 and 500'
            }), 400
        
        if not isinstance(page, int) or page < 1:
            page = 1
        
        # Perform search
        print(f"Searching for: {query} (max: {max_results}, page: {page})")
        articles = scraper.search_news(query, max_results, page)
        
        # Check if we got results and from where
        api_key_status = "Configured" if API_KEY else "Not Configured"
        print(f"Search completed. Found {len(articles)} articles. API Key: {api_key_status}")
        
        # Generate unique search ID
        search_id = str(uuid.uuid4())
        
        # Cache results
        search_cache[search_id] = {
            'query': query,
            'page': page,
            'articles': articles,
            'timestamp': datetime.now().isoformat()
        }
        
        # Return results
        return jsonify({
            'search_id': search_id,
            'query': query,
            'page': page,
            'count': len(articles),
            'articles': articles
        })
    
    except Exception as e:
        print(f"Error in search_news: {str(e)}")
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500


@app.route('/api/export', methods=['POST'])
def export_excel_direct():
    """
    Export articles provided in request body to Excel directly
    
    Request body:
    {
        "query": "search term",
        "articles": [...]
    }
    """
    try:
        data = request.get_json()
        if not data or 'articles' not in data:
            return jsonify({'error': 'Missing articles in request'}), 400
            
        articles = data.get('articles', [])
        query = data.get('query', 'news')
        
        if not articles:
            return jsonify({'error': 'No articles to export'}), 400
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        clean_query = "".join(c for c in query if c.isalnum() or c in (' ', '_', '-')).strip() or 'news'
        filename = f"news_{clean_query.replace(' ', '_')}_{timestamp}.xlsx"
        
        filepath = scraper.export_to_excel(articles, filename)
        
        return send_file(
            filepath,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"Error in export_excel_direct: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@app.route('/api/export/<search_id>', methods=['GET'])
def export_excel(search_id):
    """
    Export search results to Excel
    
    URL parameter:
        search_id: The unique search ID from a previous search
    
    Returns:
        Excel file download
    """
    try:
        # Check if search_id exists
        if search_id not in search_cache:
            return jsonify({
                'error': 'Search ID not found or expired'
            }), 404
        
        # Get cached results
        search_data = search_cache[search_id]
        articles = search_data['articles']
        query = search_data['query']
        
        if not articles:
            return jsonify({
                'error': 'No articles to export'
            }), 400
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        clean_query = "".join(c for c in query if c.isalnum() or c in (' ', '_', '-')).strip() or 'news'
        filename = f"news_{clean_query.replace(' ', '_')}_{timestamp}.xlsx"
        
        # Export to Excel
        filepath = scraper.export_to_excel(articles, filename)
        
        # Send file
        return send_file(
            filepath,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        print(f"Error in export_excel: {str(e)}")
        return jsonify({
            'error': f'An error occurred: {str(e)}'
        }), 500


@app.route('/api/details', methods=['POST'])
def get_article_details():
    """
    Extract detailed article text and metadata from URL
    """
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'Missing required field: url'}), 400
        
        url = data['url'].strip()
        if not url:
            return jsonify({'error': 'URL cannot be empty'}), 400
            
        print(f"Extracting details for: {url}")
        details = scraper.extract_article_details(url)
        
        if not details:
            return jsonify({'error': 'Could not extract details from URL'}), 404
            
        return jsonify(details)
    except Exception as e:
        print(f"Error in get_article_details: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'api_key_configured': bool(API_KEY),
        'timestamp': datetime.now().isoformat()
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({
            'error': 'API endpoint not found'
        }), 404
    # If a static file or frontend route is requested
    index_file = os.path.join(FRONTEND_DIR, 'index.html')
    if os.path.exists(index_file):
        return send_file(index_file)
    return jsonify({
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"\n{'='*50}")
    print("[Server] Online News Scraper Full-Stack App")
    print(f"{'='*50}")
    print(f"Listening on: http://{host}:{port}")
    print(f"API Key: {'[OK] Configured' if API_KEY else '[!] Not configured (using fallback)'}")
    print(f"Debug Mode: {debug}")
    print(f"{'='*50}\n")
    
    app.run(
        host=host,
        port=port,
        debug=debug
    )
