from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add the current directory to the path so we can import course_recommender
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from course_recommender import CourseRecommender, get_course_recommendations

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the course recommender
course_recommender = CourseRecommender()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "course_recommender"})

@app.route('/api/recommend', methods=['POST'])
def recommend_courses():
    """Get course recommendations based on user interests"""
    try:
        data = request.get_json()
        
        if not data or 'interests' not in data:
            return jsonify({
                "error": "Missing 'interests' field in request body"
            }), 400
        
        interests = data['interests']
        
        # Handle both string and list inputs
        if isinstance(interests, str):
            interests = [interests]
        elif not isinstance(interests, list):
            return jsonify({
                "error": "Interests must be a string or list of strings"
            }), 400
        
        # Get recommendations using the course recommender
        recommendations = course_recommender.get_recommendations(interests)
        
        # Also get external course recommendations
        external_recommendations = []
        for interest in interests:
            external_courses = get_course_recommendations(interest)
            for title, url in external_courses:
                external_recommendations.append({
                    "title": title,
                    "url": url,
                    "source": "external",
                    "level": "Not specified"
                })
        
        # Combine and format recommendations
        formatted_recommendations = []
        
        # Add internal recommendations
        for course in recommendations:
            formatted_recommendations.append({
                "title": course['title'],
                "description": course['description'],
                "level": course['level'],
                "topics": course['topics'],
                "source": "internal",
                "url": None
            })
        
        # Add external recommendations (limit to avoid duplicates)
        seen_titles = set()
        for course in recommendations:
            seen_titles.add(course['title'].lower())
        
        for ext_course in external_recommendations[:5]:  # Limit external courses
            if ext_course['title'].lower() not in seen_titles:
                formatted_recommendations.append(ext_course)
                seen_titles.add(ext_course['title'].lower())
        
        return jsonify({
            "success": True,
            "recommendations": formatted_recommendations,
            "count": len(formatted_recommendations),
            "interests": interests
        })
        
    except Exception as e:
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/search', methods=['GET'])
def search_courses():
    """Search for courses by topic"""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({
                "error": "Missing 'q' query parameter"
            }), 400
        
        # Get course recommendations for the search query
        recommendations = get_course_recommendations(query)
        
        formatted_recommendations = []
        for title, url in recommendations:
            formatted_recommendations.append({
                "title": title,
                "url": url,
                "source": "external",
                "level": "Not specified"
            })
        
        return jsonify({
            "success": True,
            "results": formatted_recommendations,
            "count": len(formatted_recommendations),
            "query": query
        })
        
    except Exception as e:
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/courses', methods=['GET'])
def get_all_courses():
    """Get all available courses from the internal database"""
    try:
        return jsonify({
            "success": True,
            "courses": course_recommender.courses,
            "count": len(course_recommender.courses)
        })
        
    except Exception as e:
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/topics', methods=['GET'])
def get_available_topics():
    """Get all available topics for recommendations"""
    try:
        all_topics = set()
        for course in course_recommender.courses:
            all_topics.update(course['topics'])
        
        return jsonify({
            "success": True,
            "topics": sorted(list(all_topics)),
            "count": len(all_topics)
        })
        
    except Exception as e:
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("Starting Course Recommender API...")
    print("Available endpoints:")
    print("- GET  /health - Health check")
    print("- POST /api/recommend - Get course recommendations")
    print("- GET  /api/search?q=<query> - Search courses")
    print("- GET  /api/courses - Get all courses")
    print("- GET  /api/topics - Get available topics")
    print("\nServer running on http://localhost:5001")
    
    app.run(host='0.0.0.0', port=5001, debug=True) 