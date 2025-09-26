# AI Teacher Chatbot Service

An intelligent educational assistant powered by AI that provides personalized learning support, answers questions, and cites reliable sources.

## Features

- **AI-Powered Responses**: Uses Mistral AI model through Ollama for intelligent educational responses
- **Web Content Integration**: Searches and scrapes educational content from reliable sources
- **Source Citation**: Provides citations and links to educational resources
- **Multi-Topic Support**: Covers programming, mathematics, science, history, technology, and languages
- **Real-time Learning**: Instant responses to educational queries
- **RESTful API**: Easy integration with frontend applications

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running with Mistral model
- Internet connection for web content integration

## Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd NewBackEnd/teacher_chatbot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up Ollama (if not already installed)**
   ```bash
   # Install Ollama from https://ollama.ai/
   # Pull the Mistral model
   ollama pull mistral:instruct
   ```

## Quick Start

### Windows
```bash
# Using batch file
start.bat

# Or manually
venv\Scripts\activate
python app.py
```

### PowerShell
```powershell
# Using PowerShell script
.\start.ps1

# Or manually
venv\Scripts\Activate.ps1
python app.py
```

### macOS/Linux
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the service
python app.py
```

The service will start on `http://localhost:5003`

## API Endpoints

### Health Check
```
GET /health
```
Returns the health status of the service.

### Chat with AI Teacher
```
POST /api/chat
Content-Type: application/json

{
  "message": "What is machine learning?"
}
```

### Chat via GET (for simple queries)
```
GET /api/chat/{message}
```

### Get Suggested Questions
```
GET /api/suggestions
```
Returns categorized question suggestions for different subjects.

### Get Learning Topics
```
GET /api/topics
```
Returns available learning topics with icons and subtopics.

### Get Service Status
```
GET /api/status
```
Returns detailed service status and capabilities.

## API Response Format

### Chat Response
```json
{
  "success": true,
  "response": {
    "answer": "Detailed educational response...",
    "sources": [
      {
        "title": "Source Title",
        "url": "https://example.com"
      }
    ],
    "full_response": "Complete response with sources"
  },
  "query": "Original user question"
}
```

### Suggestions Response
```json
{
  "success": true,
  "suggestions": [
    {
      "category": "Programming",
      "questions": [
        "What is object-oriented programming?",
        "How do I learn Python?"
      ]
    }
  ]
}
```

## Configuration

### Environment Variables
Create a `.env` file in the project directory:

```env
# Optional: Search API configuration
SEARCH_API_KEY=your_search_api_key
SEARCH_API_URL=https://serpapi.com/search

# Model configuration
MODEL_NAME=mistral:instruct
```

### Model Configuration
The service uses the Mistral model by default. You can change this in `main.py`:

```python
MODEL_NAME = "mistral:instruct"  # Change to your preferred model
```

## Features in Detail

### 1. Intelligent Responses
- Uses advanced AI models for contextual understanding
- Provides detailed explanations with examples
- Adapts responses to different learning levels

### 2. Web Content Integration
- Searches educational websites for relevant content
- Scrapes and processes content from reliable sources
- Prioritizes educational domains (Wikipedia, Khan Academy, etc.)

### 3. Source Citation
- Automatically cites sources for responses
- Provides clickable links to educational resources
- Ensures information credibility and traceability

### 4. Multi-Topic Support
- **Programming**: Python, JavaScript, Java, Web Development
- **Mathematics**: Algebra, Calculus, Statistics, Geometry
- **Science**: Physics, Chemistry, Biology, Astronomy
- **History**: Ancient History, Modern History, World Wars
- **Technology**: AI, Machine Learning, Cybersecurity
- **Languages**: English, Spanish, French, German, etc.

## Error Handling

The service includes comprehensive error handling:

- **Connection Errors**: Graceful handling of network issues
- **Model Errors**: Fallback responses when AI model is unavailable
- **Scraping Errors**: Continues with AI-only responses when web scraping fails
- **API Errors**: Proper HTTP status codes and error messages

## Logging

The service logs all activities to `chatbot.log`:

- Query processing
- Web scraping results
- AI model responses
- Error conditions
- Performance metrics

## Performance Optimization

- **Caching**: Recent queries are cached to improve response times
- **Parallel Processing**: Multiple sources are scraped concurrently
- **Content Filtering**: Only relevant educational content is processed
- **Response Optimization**: Content is trimmed to optimal length

## Troubleshooting

### Common Issues

1. **Ollama not running**
   ```
   Error: Failed to initialize Ollama model
   ```
   Solution: Start Ollama service and ensure Mistral model is available

2. **Port already in use**
   ```
   Error: Address already in use
   ```
   Solution: Change port in `app.py` or stop conflicting service

3. **Missing dependencies**
   ```
   ModuleNotFoundError: No module named 'flask'
   ```
   Solution: Install dependencies with `pip install -r requirements.txt`

4. **Model not found**
   ```
   Error: Model mistral:instruct not found
   ```
   Solution: Pull the model with `ollama pull mistral:instruct`

### Debug Mode

Enable debug mode by setting `debug=True` in `app.py`:

```python
app.run(host='0.0.0.0', port=5003, debug=True)
```

## Integration with Frontend

The service is designed to work seamlessly with the React frontend:

1. **CORS Enabled**: Cross-origin requests are allowed
2. **JSON Responses**: All responses are in JSON format
3. **Error Handling**: Proper error responses for frontend handling
4. **Real-time Updates**: Supports real-time chat functionality

## Security Considerations

- Input validation and sanitization
- Rate limiting (can be implemented)
- CORS configuration for specific origins
- Error message sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the NF TRY learning platform.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in `chatbot.log`
3. Ensure all prerequisites are met
4. Test with the health check endpoint

---

**Note**: This service requires Ollama to be running with the Mistral model for full functionality. Without Ollama, the service will return error responses. 