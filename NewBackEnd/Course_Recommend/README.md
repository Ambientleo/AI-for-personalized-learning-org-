# Course Recommender Backend

A Flask-based API service that provides intelligent course recommendations based on user interests and searches for courses from external sources.

## Features

- **Interest-based Recommendations**: Get personalized course recommendations based on user interests
- **Course Search**: Search for courses by topic or skill
- **External Course Integration**: Fetches courses from Coursera and other educational platforms
- **Internal Course Database**: Maintains a curated list of high-quality courses
- **RESTful API**: Clean and easy-to-use API endpoints

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Server**:
   ```bash
   python app.py
   ```

   The server will start on `http://localhost:5001`

## API Endpoints

### Health Check
- **GET** `/health`
- Returns server status

### Get Course Recommendations
- **POST** `/api/recommend`
- **Body**: `{"interests": ["Python", "React", "Machine Learning"]}`
- Returns personalized course recommendations

### Search Courses
- **GET** `/api/search?q=<query>`
- Returns courses matching the search query

### Get All Courses
- **GET** `/api/courses`
- Returns all available internal courses

### Get Available Topics
- **GET** `/api/topics`
- Returns all available topics for recommendations

## Example Usage

### Get Recommendations
```bash
curl -X POST http://localhost:5001/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"interests": ["Python", "React"]}'
```

### Search Courses
```bash
curl "http://localhost:5001/api/search?q=Python"
```

## Response Format

### Recommendations Response
```json
{
  "success": true,
  "recommendations": [
    {
      "title": "Introduction to Python Programming",
      "description": "Learn the basics of Python programming language",
      "level": "Beginner",
      "topics": ["programming", "python", "coding"],
      "source": "internal",
      "url": null
    },
    {
      "title": "Python Official Docs",
      "url": "https://docs.python.org/3/tutorial/",
      "source": "external",
      "level": "Not specified"
    }
  ],
  "count": 7,
  "interests": ["Python", "React"]
}
```

## Integration with Frontend

The frontend Course Recommender component integrates with this API to provide:

1. **Interest-based Recommendations**: Users can enter their learning interests and get personalized course suggestions
2. **Course Search**: Search functionality to find specific courses
3. **Real-time Results**: Live course data from both internal and external sources
4. **User-friendly Interface**: Clean UI with loading states and error handling

## Technologies Used

- **Flask**: Web framework for the API
- **Flask-CORS**: Cross-origin resource sharing
- **BeautifulSoup**: Web scraping for external courses
- **Requests**: HTTP library for API calls

## Notes

- The service scrapes Coursera for external course recommendations
- Internal courses are curated and maintained in the codebase
- CORS is enabled for frontend integration
- Error handling and validation are implemented for all endpoints 