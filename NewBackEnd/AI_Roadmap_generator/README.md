# AI Roadmap Generator Backend

A Flask-based API service that generates personalized learning roadmaps using AI and provides curated template roadmaps for various skills and technologies.

## Features

- **AI-Powered Roadmap Generation**: Generate custom learning roadmaps using Ollama AI
- **Template Library**: Pre-built roadmaps for popular skills and technologies
- **Interactive Learning Paths**: Step-by-step learning guides with resources
- **Progress Tracking**: Track completion of roadmap steps
- **RESTful API**: Clean and easy-to-use API endpoints

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Ollama** (for AI-powered generation):
   - Download from: https://ollama.ai/
   - Install and start Ollama service
   - Pull the Mistral model: `ollama pull mistral:latest`

3. **Run the Server**:
   ```bash
   python app.py
   ```

   The server will start on `http://localhost:5002`

## API Endpoints

### Health Check
- **GET** `/health`
- Returns server status

### Generate Custom Roadmap
- **POST** `/api/generate`
- **Body**: `{"topic": "Python Programming"}`
- Returns AI-generated learning roadmap

### Generate Roadmap by Topic (GET)
- **GET** `/api/generate/<topic>`
- Returns roadmap for the specified topic

### Get Available Templates
- **GET** `/api/templates`
- Returns list of available roadmap templates

### Get Specific Template
- **GET** `/api/template/<template_id>`
- Returns detailed roadmap template

## Example Usage

### Generate Custom Roadmap
```bash
curl -X POST http://localhost:5002/api/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Machine Learning"}'
```

### Get Roadmap by Topic
```bash
curl "http://localhost:5002/api/generate/Python"
```

### Get Templates
```bash
curl "http://localhost:5002/api/templates"
```

## Response Format

### Roadmap Response
```json
{
  "success": true,
  "roadmap": {
    "title": "Learning Roadmap for Python",
    "description": "A comprehensive guide to learning Python",
    "steps": [
      {
        "level": 1,
        "title": "Getting Started",
        "description": "Learn the basics and fundamentals",
        "topics": ["Introduction", "Basic concepts", "Setup"],
        "resources": ["Documentation", "Tutorial videos", "Online courses"]
      }
    ],
    "estimated_time": "3-6 months",
    "prerequisites": ["Basic computer skills", "Motivation to learn"]
  },
  "topic": "Python"
}
```

## Available Templates

- **Web Development**: Full-stack web development roadmap
- **Python Programming**: Complete Python learning path
- **Machine Learning**: AI and machine learning journey
- **Mobile Development**: Mobile app development roadmap
- **Cybersecurity**: Information security and ethical hacking
- **Data Science**: Data analysis and visualization

## Integration with Frontend

The frontend Roadmap Generator component integrates with this API to provide:

1. **Custom Roadmap Generation**: Users can enter any topic and get AI-generated roadmaps
2. **Template Selection**: Choose from pre-built roadmap templates
3. **Interactive Progress Tracking**: Mark steps as complete and track progress
4. **Download & Share**: Export roadmaps as text files or share them
5. **Real-time Generation**: Live roadmap generation with loading states

## Technologies Used

- **Flask**: Web framework for the API
- **Flask-CORS**: Cross-origin resource sharing
- **Ollama**: Local AI model for roadmap generation
- **Requests**: HTTP library for API calls

## AI Model

The service uses Ollama with the Mistral model for generating custom roadmaps. The AI:
- Analyzes the requested topic
- Creates structured learning steps
- Suggests relevant resources
- Estimates learning time
- Identifies prerequisites

## Notes

- Requires Ollama to be running for AI-powered generation
- Falls back to default roadmaps if AI generation fails
- Templates are curated and maintained in the codebase
- CORS is enabled for frontend integration
- Error handling and validation are implemented for all endpoints 