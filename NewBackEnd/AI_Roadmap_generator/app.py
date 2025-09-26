from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the current directory to the path so we can import roadmap_generator
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from roadmap_generator import generate_roadmap, get_default_roadmap

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "roadmap_generator"})

@app.route('/api/generate', methods=['POST'])
def generate_learning_roadmap():
    """Generate a learning roadmap for the given topic"""
    try:
        data = request.get_json()
        
        if not data or 'topic' not in data:
            return jsonify({
                "error": "Missing 'topic' field in request body"
            }), 400
        
        topic = data['topic'].strip()
        
        if not topic:
            return jsonify({
                "error": "Topic cannot be empty"
            }), 400
        
        # Generate the roadmap
        roadmap = generate_roadmap(topic)
        
        if not roadmap:
            return jsonify({
                "error": "Failed to generate roadmap"
            }), 500
        
        return jsonify({
            "success": True,
            "roadmap": roadmap,
            "topic": topic
        })
        
    except Exception as e:
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/generate/<topic>', methods=['GET'])
def generate_roadmap_by_topic(topic):
    """Generate a learning roadmap for the given topic via GET request"""
    try:
        if not topic or not topic.strip():
            return jsonify({
                "error": "Topic cannot be empty"
            }), 400
        
        # Generate the roadmap
        roadmap = generate_roadmap(topic.strip())
        
        if not roadmap:
            return jsonify({
                "error": "Failed to generate roadmap"
            }), 500
        
        return jsonify({
            "success": True,
            "roadmap": roadmap,
            "topic": topic.strip()
        })
        
    except Exception as e:
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/templates', methods=['GET'])
def get_roadmap_templates():
    """Get available roadmap templates"""
    try:
        templates = [
            {
                "id": "web-development",
                "title": "Web Development",
                "description": "Full-stack web development roadmap",
                "topics": ["HTML", "CSS", "JavaScript", "React", "Node.js", "Database"],
                "estimated_time": "6-12 months"
            },
            {
                "id": "python",
                "title": "Python Programming",
                "description": "Complete Python learning path",
                "topics": ["Python Basics", "OOP", "Data Structures", "Web Development", "Data Science"],
                "estimated_time": "4-8 months"
            },
            {
                "id": "machine-learning",
                "title": "Machine Learning",
                "description": "AI and machine learning journey",
                "topics": ["Python", "Mathematics", "Statistics", "ML Algorithms", "Deep Learning"],
                "estimated_time": "8-12 months"
            },
            {
                "id": "mobile-development",
                "title": "Mobile Development",
                "description": "Mobile app development roadmap",
                "topics": ["React Native", "Flutter", "iOS", "Android", "App Store"],
                "estimated_time": "6-10 months"
            },
            {
                "id": "cybersecurity",
                "title": "Cybersecurity",
                "description": "Information security and ethical hacking",
                "topics": ["Networking", "Linux", "Cryptography", "Penetration Testing", "Security Tools"],
                "estimated_time": "8-12 months"
            },
            {
                "id": "data-science",
                "title": "Data Science",
                "description": "Data analysis and visualization",
                "topics": ["Python", "Statistics", "SQL", "Data Visualization", "Machine Learning"],
                "estimated_time": "6-10 months"
            }
        ]
        
        return jsonify({
            "success": True,
            "templates": templates,
            "count": len(templates)
        })
        
    except Exception as e:
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/template/<template_id>', methods=['GET'])
def get_roadmap_template(template_id):
    """Get a specific roadmap template"""
    try:
        templates = {
            "web-development": {
                "title": "Web Development Roadmap",
                "description": "A comprehensive guide to becoming a full-stack web developer",
                "steps": [
                    {
                        "level": 1,
                        "title": "Frontend Fundamentals",
                        "description": "Learn the basics of web development",
                        "topics": ["HTML5", "CSS3", "JavaScript ES6+", "Responsive Design"],
                        "resources": ["MDN Web Docs", "freeCodeCamp", "W3Schools", "CSS-Tricks"]
                    },
                    {
                        "level": 2,
                        "title": "Frontend Framework",
                        "description": "Master a modern JavaScript framework",
                        "topics": ["React.js", "State Management", "Component Architecture", "Hooks"],
                        "resources": ["React Documentation", "React Tutorial", "Redux Toolkit", "React Router"]
                    },
                    {
                        "level": 3,
                        "title": "Backend Development",
                        "description": "Learn server-side development",
                        "topics": ["Node.js", "Express.js", "REST APIs", "Database Design"],
                        "resources": ["Node.js Documentation", "Express.js Guide", "MongoDB Tutorial", "PostgreSQL"]
                    },
                    {
                        "level": 4,
                        "title": "Full-Stack Integration",
                        "description": "Connect frontend and backend",
                        "topics": ["API Integration", "Authentication", "Deployment", "DevOps Basics"],
                        "resources": ["Heroku", "Vercel", "Netlify", "Docker Basics"]
                    }
                ],
                "estimated_time": "6-12 months",
                "prerequisites": ["Basic computer skills", "Logical thinking", "Patience to learn"]
            },
            "python": {
                "title": "Python Programming Roadmap",
                "description": "Master Python programming from basics to advanced concepts",
                "steps": [
                    {
                        "level": 1,
                        "title": "Python Basics",
                        "description": "Learn fundamental Python concepts",
                        "topics": ["Variables", "Data Types", "Control Flow", "Functions", "Modules"],
                        "resources": ["Python Official Docs", "Real Python", "W3Schools Python", "Codecademy"]
                    },
                    {
                        "level": 2,
                        "title": "Object-Oriented Programming",
                        "description": "Master OOP concepts in Python",
                        "topics": ["Classes", "Objects", "Inheritance", "Polymorphism", "Encapsulation"],
                        "resources": ["Python OOP Tutorial", "Real Python OOP", "GeeksforGeeks"]
                    },
                    {
                        "level": 3,
                        "title": "Advanced Python",
                        "description": "Explore advanced Python features",
                        "topics": ["Decorators", "Generators", "Context Managers", "Async/Await"],
                        "resources": ["Python Advanced Tutorial", "Real Python Advanced", "Python Cookbook"]
                    },
                    {
                        "level": 4,
                        "title": "Specializations",
                        "description": "Choose your Python path",
                        "topics": ["Web Development (Django/Flask)", "Data Science", "Automation", "API Development"],
                        "resources": ["Django Documentation", "Flask Tutorial", "Pandas", "FastAPI"]
                    }
                ],
                "estimated_time": "4-8 months",
                "prerequisites": ["Basic computer literacy", "Logical thinking", "Mathematics fundamentals"]
            }
        }
        
        if template_id not in templates:
            return jsonify({
                "error": f"Template '{template_id}' not found"
            }), 404
        
        return jsonify({
            "success": True,
            "template": templates[template_id],
            "template_id": template_id
        })
        
    except Exception as e:
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("Starting Roadmap Generator API...")
    print("Available endpoints:")
    print("- GET  /health - Health check")
    print("- POST /api/generate - Generate custom roadmap")
    print("- GET  /api/generate/<topic> - Generate roadmap by topic")
    print("- GET  /api/templates - Get available templates")
    print("- GET  /api/template/<id> - Get specific template")
    print("\nServer running on http://localhost:5002")
    
    app.run(host='0.0.0.0', port=5002, debug=True) 