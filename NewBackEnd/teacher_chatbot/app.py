from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import logging

# Add the current directory to the path so we can import main
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import TeacherChatbot

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the teacher chatbot
try:
    chatbot = TeacherChatbot()
    logger.info("Teacher chatbot initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize teacher chatbot: {str(e)}")
    chatbot = None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy" if chatbot else "unhealthy",
        "service": "teacher_chatbot",
        "model_available": chatbot is not None
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with the AI teacher"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "error": "Missing 'message' field in request body"
            }), 400
        
        message = data['message'].strip()
        
        if not message:
            return jsonify({
                "error": "Message cannot be empty"
            }), 400
        
        if not chatbot:
            return jsonify({
                "error": "Teacher chatbot is not available. Please check the service."
            }), 503
        
        # Get response from the chatbot
        response = chatbot.answer_query(message)
        
        # Parse response to separate answer and sources
        sources = []
        answer = response
        
        if "Sources:" in response:
            parts = response.split("Sources:", 1)
            answer = parts[0].strip()
            if len(parts) > 1:
                sources_text = parts[1].strip()
                # Parse sources (format: "- Title: URL")
                for line in sources_text.split('\n'):
                    line = line.strip()
                    if line.startswith('- ') and ':' in line:
                        title_url = line[2:]  # Remove "- "
                        if ':' in title_url:
                            title, url = title_url.split(':', 1)
                            sources.append({
                                "title": title.strip(),
                                "url": url.strip()
                            })
        
        return jsonify({
            "success": True,
            "response": {
                "answer": answer,
                "sources": sources,
                "full_response": response
            },
            "query": message
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/chat/<message>', methods=['GET'])
def chat_get(message):
    """Chat with the AI teacher via GET request"""
    try:
        if not message or not message.strip():
            return jsonify({
                "error": "Message cannot be empty"
            }), 400
        
        if not chatbot:
            return jsonify({
                "error": "Teacher chatbot is not available. Please check the service."
            }), 503
        
        # Get response from the chatbot
        response = chatbot.answer_query(message.strip())
        
        # Parse response to separate answer and sources
        sources = []
        answer = response
        
        if "Sources:" in response:
            parts = response.split("Sources:", 1)
            answer = parts[0].strip()
            if len(parts) > 1:
                sources_text = parts[1].strip()
                # Parse sources (format: "- Title: URL")
                for line in sources_text.split('\n'):
                    line = line.strip()
                    if line.startswith('- ') and ':' in line:
                        title_url = line[2:]  # Remove "- "
                        if ':' in title_url:
                            title, url = title_url.split(':', 1)
                            sources.append({
                                "title": title.strip(),
                                "url": url.strip()
                            })
        
        return jsonify({
            "success": True,
            "response": {
                "answer": answer,
                "sources": sources,
                "full_response": response
            },
            "query": message.strip()
        })
        
    except Exception as e:
        logger.error(f"Error in chat GET endpoint: {str(e)}")
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """Get suggested questions for the AI teacher"""
    try:
        suggestions = [
            {
                "category": "Programming",
                "questions": [
                    "What is object-oriented programming?",
                    "How do I learn Python?",
                    "What are the differences between Python and JavaScript?",
                    "How do I create a REST API?",
                    "What is machine learning?"
                ]
            },
            {
                "category": "Mathematics",
                "questions": [
                    "What is calculus?",
                    "How do I solve quadratic equations?",
                    "What are matrices used for?",
                    "How do I understand probability?",
                    "What is linear algebra?"
                ]
            },
            {
                "category": "Science",
                "questions": [
                    "How does photosynthesis work?",
                    "What is the theory of relativity?",
                    "How do atoms work?",
                    "What is DNA?",
                    "How do ecosystems function?"
                ]
            },
            {
                "category": "History",
                "questions": [
                    "What caused World War II?",
                    "How did the Industrial Revolution change society?",
                    "What was the Cold War?",
                    "How did ancient civilizations develop?",
                    "What led to the fall of the Roman Empire?"
                ]
            },
            {
                "category": "Technology",
                "questions": [
                    "How do computers work?",
                    "What is artificial intelligence?",
                    "How does the internet work?",
                    "What is blockchain technology?",
                    "How do smartphones function?"
                ]
            }
        ]
        
        return jsonify({
            "success": True,
            "suggestions": suggestions
        })
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/topics', methods=['GET'])
def get_topics():
    """Get available learning topics"""
    try:
        topics = [
            {
                "name": "Programming",
                "subtopics": ["Python", "JavaScript", "Java", "C++", "Web Development", "Mobile Development"],
                "icon": "💻"
            },
            {
                "name": "Mathematics",
                "subtopics": ["Algebra", "Calculus", "Statistics", "Geometry", "Linear Algebra"],
                "icon": "📐"
            },
            {
                "name": "Science",
                "subtopics": ["Physics", "Chemistry", "Biology", "Astronomy", "Earth Science"],
                "icon": "🔬"
            },
            {
                "name": "History",
                "subtopics": ["Ancient History", "Modern History", "World Wars", "Civilizations", "Political History"],
                "icon": "📚"
            },
            {
                "name": "Technology",
                "subtopics": ["AI", "Machine Learning", "Cybersecurity", "Cloud Computing", "IoT"],
                "icon": "🚀"
            },
            {
                "name": "Languages",
                "subtopics": ["English", "Spanish", "French", "German", "Chinese", "Japanese"],
                "icon": "🗣️"
            }
        ]
        
        return jsonify({
            "success": True,
            "topics": topics
        })
        
    except Exception as e:
        logger.error(f"Error getting topics: {str(e)}")
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get detailed status of the teacher chatbot"""
    try:
        status = {
            "service": "teacher_chatbot",
            "status": "running" if chatbot else "error",
            "model_available": chatbot is not None,
            "model_name": "mistral:instruct" if chatbot else None,
            "features": [
                "AI-powered educational responses",
                "Web content integration",
                "Source citation",
                "Multi-topic support",
                "Real-time learning assistance"
            ],
            "capabilities": [
                "Answer educational questions",
                "Provide detailed explanations",
                "Cite reliable sources",
                "Support multiple subjects",
                "Adapt to different learning levels"
            ]
        }
        
        return jsonify({
            "success": True,
            "status": status
        })
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("Starting AI Teacher Chatbot API...")
    print("Available endpoints:")
    print("- GET  /health - Health check")
    print("- POST /api/chat - Chat with AI teacher")
    print("- GET  /api/chat/<message> - Chat via GET")
    print("- GET  /api/suggestions - Get question suggestions")
    print("- GET  /api/topics - Get available topics")
    print("- GET  /api/status - Get detailed status")
    print("\nServer running on http://localhost:5003")
    
    app.run(host='0.0.0.0', port=5003, debug=True) 