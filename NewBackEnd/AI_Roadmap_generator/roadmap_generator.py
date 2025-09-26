import requests
import json
import os
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_roadmap(topic):
    """
    Generate a learning roadmap for the given topic using Ollama.
    """
    logger.info(f"Generating roadmap for topic: {topic}")
    
    # Improved prompt for better roadmap generation
    prompt = f"""You are an expert learning path designer with deep knowledge of {topic}. Create a comprehensive, highly detailed learning roadmap specifically for {topic}.

IMPORTANT: Respond ONLY with valid JSON. Do not include any text before or after the JSON.

Create a detailed roadmap with this exact JSON structure:
{{
    "title": "Comprehensive Learning Roadmap for {topic}",
    "description": "A detailed, step-by-step guide to master {topic} from beginner to expert level",
    "steps": [
        {{
            "level": 1,
            "title": "Foundation and Basics of {topic}",
            "description": "Build a strong foundation with fundamental concepts, terminology, and basic principles specific to {topic}",
            "topics": [
                "Core concepts and definitions in {topic}",
                "Historical background and evolution of {topic}",
                "Basic terminology and vocabulary",
                "Fundamental principles and theories",
                "Essential tools and resources for {topic}"
            ],
            "resources": [
                "https://www.coursera.org/search?query={topic} - Coursera {topic} Courses",
                "https://www.udemy.com/topic/{topic}/ - Udemy {topic} Courses",
                "https://www.edx.org/search?q={topic} - edX {topic} Programs",
                "https://www.youtube.com/results?search_query={topic}+tutorial - YouTube {topic} Tutorials",
                "https://www.khanacademy.org/search?page_search_query={topic} - Khan Academy {topic} Content"
            ]
        }},
        {{
            "level": 2,
            "title": "Intermediate Concepts in {topic}",
            "description": "Dive deeper into advanced concepts, practical applications, and intermediate-level skills in {topic}",
            "topics": [
                "Advanced theories and methodologies in {topic}",
                "Practical applications and case studies",
                "Problem-solving techniques specific to {topic}",
                "Industry best practices and standards",
                "Integration with related fields and technologies"
            ],
            "resources": [
                "https://www.linkedin.com/learning/search?keywords={topic} - LinkedIn Learning {topic} Courses",
                "https://www.pluralsight.com/search?q={topic} - Pluralsight {topic} Paths",
                "https://www.skillshare.com/search?query={topic} - Skillshare {topic} Classes",
                "https://www.datacamp.com/search?q={topic} - DataCamp {topic} Tracks",
                "https://www.codecademy.com/search?query={topic} - Codecademy {topic} Courses"
            ]
        }},
        {{
            "level": 3,
            "title": "Advanced Applications of {topic}",
            "description": "Master advanced techniques, specialized applications, and expert-level skills in {topic}",
            "topics": [
                "Expert-level techniques and methodologies",
                "Specialized applications and use cases",
                "Research and innovation in {topic}",
                "Performance optimization and advanced strategies",
                "Emerging trends and future directions"
            ],
            "resources": [
                "https://www.oreilly.com/search/?query={topic} - O'Reilly {topic} Books and Courses",
                "https://www.packtpub.com/search?query={topic} - Packt {topic} Publications",
                "https://www.manning.com/search?q={topic} - Manning {topic} Books",
                "https://www.springer.com/search?query={topic} - Springer {topic} Publications",
                "https://scholar.google.com/scholar?q={topic} - Google Scholar {topic} Research"
            ]
        }},
        {{
            "level": 4,
            "title": "Specialization and Mastery in {topic}",
            "description": "Focus on specialized areas, industry applications, and achieving mastery in specific aspects of {topic}",
            "topics": [
                "Specialized sub-fields within {topic}",
                "Industry-specific applications and implementations",
                "Advanced research methodologies",
                "Leadership and expertise development",
                "Contributing to the {topic} community and field"
            ],
            "resources": [
                "https://www.researchgate.net/search/publication?q={topic} - ResearchGate {topic} Publications",
                "https://arxiv.org/search/?query={topic} - arXiv {topic} Papers",
                "https://www.academia.edu/search?q={topic} - Academia.edu {topic} Research",
                "https://www.semanticscholar.org/search?q={topic} - Semantic Scholar {topic} Papers",
                "https://www.jstor.org/action/doBasicSearch?Query={topic} - JSTOR {topic} Articles"
            ]
        }},
        {{
            "level": 5,
            "title": "Expert Level and Innovation in {topic}",
            "description": "Achieve expert status, contribute to the field, and drive innovation in {topic}",
            "topics": [
                "Cutting-edge research and developments",
                "Innovation and breakthrough applications",
                "Teaching and mentoring in {topic}",
                "Industry leadership and thought leadership",
                "Contributing to open source and community projects"
            ],
            "resources": [
                "https://github.com/topics/{topic} - GitHub {topic} Projects",
                "https://stackoverflow.com/questions/tagged/{topic} - Stack Overflow {topic} Community",
                "https://www.reddit.com/r/{topic}/ - Reddit {topic} Community",
                "https://www.meetup.com/find/?keywords={topic} - Meetup {topic} Groups",
                "https://www.conferenceindex.org/conferences/{topic} - {topic} Conferences and Events"
            ]
        }}
    ],
    "estimated_time": "12-24 months for complete mastery",
    "prerequisites": [
        "Basic computer literacy and internet skills",
        "Strong analytical and problem-solving abilities",
        "Commitment to continuous learning and practice",
        "Time management and self-discipline",
        "Curiosity and passion for programming"
    ],
    "learning_tips": [
        "Practice coding daily with real projects",
        "Join Python communities on Reddit, Discord, and Stack Overflow",
        "Follow Python experts like Guido van Rossum and Raymond Hettinger",
        "Attend PyCon conferences and local Python meetups",
        "Build a portfolio of Python projects on GitHub",
        "Stay updated with Python releases and new features",
        "Network with Python developers and contribute to open source",
        "Consider Python certifications and advanced courses"
    ]
}}

Make this roadmap highly specific to {topic}. Include:
- Actual concepts, theories, and methodologies specific to {topic}
- Real learning platforms, courses, and resources
- Industry-specific applications and use cases
- Current trends and developments in {topic}
- Practical projects and hands-on learning opportunities
- Professional development and career advancement paths

For each level, provide specific, actionable content that builds upon previous levels. Make sure each step is unique and progresses logically from basic to expert level.

Respond with ONLY the JSON, no other text."""
    
    try:
        # Try llama3:latest first (better model)
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3:latest",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 2000
                }
            },
            timeout=45
        )
        
        if response.status_code != 200:
            logger.warning(f"llama3:latest failed, trying mistral:latest")
            # Fallback to mistral:latest
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "mistral:latest",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
        
        if response.status_code != 200:
            logger.error(f"Ollama API error: {response.status_code}")
            return get_default_roadmap(topic)
        
        # Parse the response
        result = response.json()
        response_text = result.get("response", "").strip()
        
        logger.info(f"Raw response from Ollama: {response_text[:500]}...")
        
        # Clean the response text (remove markdown formatting if present)
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        # Try to extract JSON from the response
        try:
            # First, try to parse as JSON directly
            roadmap_data = json.loads(response_text)
        except json.JSONDecodeError:
            # If that fails, try to find JSON within the text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    roadmap_data = json.loads(json_match.group())
                except json.JSONDecodeError:
                    logger.warning("Could not extract valid JSON from response")
                    return get_default_roadmap(topic)
            else:
                logger.warning("No JSON found in response")
                return get_default_roadmap(topic)
        
        # Validate the roadmap structure
        if validate_roadmap_structure(roadmap_data):
            logger.info(f"Successfully generated roadmap for {topic}")
            return roadmap_data
        else:
            logger.warning("Generated roadmap has invalid structure, using default")
            logger.warning(f"Generated data: {json.dumps(roadmap_data, indent=2)[:500]}...")
            return get_default_roadmap(topic)
            
    except Exception as e:
        logger.error(f"Error generating roadmap: {str(e)}")
        return get_default_roadmap(topic)

def validate_roadmap_structure(roadmap_data):
    """
    Validate that the roadmap has the correct structure.
    """
    try:
        required_fields = ['title', 'description', 'steps', 'estimated_time', 'prerequisites']
        for field in required_fields:
            if field not in roadmap_data:
                return False
        
        if not isinstance(roadmap_data['steps'], list) or len(roadmap_data['steps']) == 0:
            return False
        
        for step in roadmap_data['steps']:
            step_fields = ['level', 'title', 'description', 'topics', 'resources']
            for field in step_fields:
                if field not in step:
                    return False
        
        # Check for optional learning_tips field
        if 'learning_tips' not in roadmap_data:
            roadmap_data['learning_tips'] = [
                "Practice regularly with hands-on projects",
                "Join online communities and forums",
                "Follow industry experts and thought leaders",
                "Attend workshops, conferences, and meetups",
                "Build a portfolio of projects and contributions"
            ]
        
        return True
    except:
        return False

def get_default_roadmap(topic):
    """
    Return a topic-specific default roadmap structure with actual links.
    """
    # Create topic-specific default roadmap
    topic_lower = topic.lower()
    
    if 'ayurveda' in topic_lower or 'ayurvedic' in topic_lower:
        return {
            "title": f"Learning Roadmap for {topic}",
            "description": f"A comprehensive guide to learning {topic} - the ancient Indian system of medicine and wellness",
            "steps": [
                {
                    "level": 1,
                    "title": "Ayurveda Fundamentals",
                    "description": "Learn the basic principles and philosophy of Ayurveda",
                    "topics": ["Doshas (Vata, Pitta, Kapha)", "Panchamahabhutas (Five Elements)", "Ayurvedic Philosophy", "Basic Ayurvedic Terms"],
                    "resources": [
                        "https://www.ayurveda.com/resources/charaka-samhita - Charaka Samhita (Classical Text)",
                        "https://www.ayurveda.com/resources/sushruta-samhita - Sushruta Samhita (Classical Text)",
                        "https://www.coursera.org/specializations/ayurveda - Ayurveda Foundation Course (Coursera)",
                        "https://www.udemy.com/course/ayurveda-basics/ - Ayurveda Basics (Udemy)",
                        "https://www.youtube.com/c/AyurvedaInstitute - Ayurveda Institute YouTube Channel",
                        "The Complete Book of Ayurvedic Home Remedies by Vasant Lad - ISBN 9780609802861"
                    ]
                },
                {
                    "level": 2,
                    "title": "Ayurvedic Assessment & Diagnosis",
                    "description": "Learn how to assess body constitution and diagnose imbalances",
                    "topics": ["Prakriti Analysis", "Vikriti Assessment", "Pulse Diagnosis", "Tongue Analysis", "Ayurvedic Examination Methods"],
                    "resources": [
                        "https://www.ayurveda.com/online-programs/pulse-diagnosis - Pulse Reading Workshop",
                        "https://www.ayurveda.com/online-programs/ayurvedic-assessment - Ayurvedic Assessment Course",
                        "https://www.ayurveda.com/online-programs/clinical-training - Clinical Training Program",
                        "https://www.ayurveda.com/online-programs/diagnosis - Ayurvedic Diagnosis Course",
                        "Ayurveda: The Science of Self-Healing by Vasant Lad - ISBN 9780893890804"
                    ]
                },
                {
                    "level": 3,
                    "title": "Ayurvedic Treatment & Therapies",
                    "description": "Master Ayurvedic treatment methods and therapeutic approaches",
                    "topics": ["Herbal Medicine", "Panchakarma Therapies", "Ayurvedic Diet & Nutrition", "Lifestyle Recommendations", "Therapeutic Procedures"],
                    "resources": [
                        "https://www.ayurveda.com/online-programs/herbal-medicine - Ayurvedic Herbal Medicine Course",
                        "https://www.ayurveda.com/online-programs/panchakarma - Panchakarma Training",
                        "https://www.ayurveda.com/online-programs/nutrition - Ayurvedic Nutrition Program",
                        "https://www.ayurveda.com/online-programs/clinical-practice - Clinical Practice Training",
                        "Prakriti: Your Ayurvedic Constitution by Robert E. Svoboda - ISBN 9788120838166"
                    ]
                }
            ],
            "estimated_time": "2-4 years",
            "prerequisites": ["Interest in holistic health", "Basic understanding of biology", "Commitment to learning traditional medicine", "Patience for comprehensive study"]
        }
    elif 'yoga' in topic_lower:
        return {
            "title": f"Learning Roadmap for {topic}",
            "description": f"A comprehensive guide to learning {topic} - physical, mental, and spiritual practices",
            "steps": [
                {
                    "level": 1,
                    "title": "Yoga Foundations",
                    "description": "Learn basic yoga postures, breathing, and philosophy",
                    "topics": ["Asanas (Postures)", "Pranayama (Breathing)", "Yoga Philosophy", "Basic Meditation", "Yoga Ethics"],
                    "resources": [
                        "https://www.yogajournal.com/poses/ - Yoga Journal Pose Library",
                        "https://www.youtube.com/c/YogaWithAdriene - Yoga With Adriene (YouTube)",
                        "https://www.udemy.com/course/yoga-for-beginners/ - Yoga for Beginners (Udemy)",
                        "https://www.coursera.org/learn/yoga - Science of Yoga (Coursera)",
                        "https://www.yogabasics.com/ - Yoga Basics (Website)"
                    ]
                },
                {
                    "level": 2,
                    "title": "Intermediate Yoga Practice",
                    "description": "Deepen your practice with advanced techniques",
                    "topics": ["Advanced Asanas", "Bandhas (Energy Locks)", "Mudras (Gestures)", "Meditation Techniques", "Yoga Therapy"],
                    "resources": [
                        "https://www.yogajournal.com/advanced-poses/ - Advanced Yoga Poses",
                        "https://www.udemy.com/course/advanced-yoga/ - Advanced Yoga Course (Udemy)",
                        "https://www.yogatherapy.org/ - Yoga Therapy Certification",
                        "https://www.meditationretreats.com/ - Meditation Retreats Directory"
                    ]
                },
                {
                    "level": 3,
                    "title": "Advanced Yoga & Teaching",
                    "description": "Master advanced practices and learn to teach others",
                    "topics": ["Yoga Teaching Methodology", "Anatomy & Physiology", "Yoga Philosophy", "Advanced Meditation", "Yoga Research"],
                    "resources": [
                        "https://www.yogaalliance.org/ - Yoga Alliance Teacher Training",
                        "https://www.udemy.com/course/yoga-anatomy/ - Yoga Anatomy Course (Udemy)",
                        "https://www.coursera.org/learn/yoga-philosophy - Yoga Philosophy (Coursera)",
                        "https://www.yogaresearch.org/ - Yoga Research Foundation"
                    ]
                }
            ],
            "estimated_time": "1-3 years",
            "prerequisites": ["Basic fitness level", "Open mind", "Regular practice commitment", "Interest in mind-body connection"]
        }
    elif 'meditation' in topic_lower or 'mindfulness' in topic_lower:
        return {
            "title": f"Learning Roadmap for {topic}",
            "description": f"A comprehensive guide to learning {topic} - mental training and awareness practices",
            "steps": [
                {
                    "level": 1,
                    "title": "Meditation Basics",
                    "description": "Learn fundamental meditation techniques and mindfulness practices",
                    "topics": ["Breath Awareness", "Body Scan", "Mindfulness Basics", "Sitting Posture", "Meditation Environment"],
                    "resources": [
                        "https://www.headspace.com/ - Headspace Meditation App",
                        "https://www.calm.com/ - Calm Meditation App",
                        "https://www.insighttimer.com/ - Insight Timer (Free App)",
                        "https://www.mindful.org/ - Mindful.org (Website)",
                        "https://www.youtube.com/c/MeditationRelaxClub - Meditation Relax Club (YouTube)"
                    ]
                },
                {
                    "level": 2,
                    "title": "Intermediate Meditation",
                    "description": "Explore different meditation styles and deepen your practice",
                    "topics": ["Loving-Kindness Meditation", "Vipassana", "Zen Meditation", "Transcendental Meditation", "Walking Meditation"],
                    "resources": [
                        "https://www.dhamma.org/ - Vipassana Meditation Centers",
                        "https://www.tm.org/ - Transcendental Meditation",
                        "https://www.zen-azi.org/ - Zen Buddhism",
                        "https://www.meditationretreats.com/ - Meditation Retreats",
                        "https://www.udemy.com/course/meditation-course/ - Advanced Meditation Course (Udemy)"
                    ]
                },
                {
                    "level": 3,
                    "title": "Advanced Meditation & Integration",
                    "description": "Master advanced techniques and integrate meditation into daily life",
                    "topics": ["Advanced Techniques", "Meditation Research", "Teaching Meditation", "Integration Practices", "Spiritual Development"],
                    "resources": [
                        "https://www.meditation.org/ - Meditation Research",
                        "https://www.udemy.com/course/teach-meditation/ - Teaching Meditation Course (Udemy)",
                        "https://www.mindfulness.org/ - Mindfulness Research",
                        "https://www.spirituality.org/ - Spiritual Development Resources"
                    ]
                }
            ],
            "estimated_time": "1-2 years",
            "prerequisites": ["Regular practice commitment", "Open mind", "Patience", "Quiet space for practice"]
        }
    elif 'python' in topic_lower:
        return {
            "title": f"Comprehensive Learning Roadmap for {topic}",
            "description": f"A detailed, step-by-step guide to master {topic} programming from beginner to expert level",
            "steps": [
                {
                    "level": 1,
                    "title": "Foundation and Basics of Python",
                    "description": "Build a strong foundation with fundamental Python concepts, syntax, and basic programming principles",
                    "topics": [
                        "Python installation and environment setup",
                        "Variables, data types, and basic operations",
                        "Control flow: conditionals and loops",
                        "Functions and basic modularity",
                        "File I/O and basic data handling"
                    ],
                    "resources": [
                        "https://docs.python.org/3/tutorial/ - Official Python Tutorial",
                        "https://www.learnpython.org/ - Learn Python (Interactive)",
                        "https://www.codecademy.com/learn/learn-python-3 - Codecademy Python Course",
                        "https://www.udemy.com/course/complete-python-bootcamp/ - Complete Python Bootcamp (Udemy)",
                        "https://realpython.com/ - Real Python (Tutorials)",
                        "Automate the Boring Stuff with Python by Al Sweigart - ISBN 9781593275990"
                    ]
                },
                {
                    "level": 2,
                    "title": "Intermediate Python Programming",
                    "description": "Dive deeper into object-oriented programming, data structures, and intermediate-level Python skills",
                    "topics": [
                        "Object-oriented programming (OOP) concepts",
                        "Advanced data structures and algorithms",
                        "Error handling and debugging techniques",
                        "Testing and code quality practices",
                        "Working with external libraries and APIs"
                    ],
                    "resources": [
                        "https://realpython.com/python3-object-oriented-programming/ - OOP in Python",
                        "https://www.udemy.com/course/python-intermediate/ - Intermediate Python (Udemy)",
                        "https://docs.python.org/3/library/ - Python Standard Library",
                        "https://pytest.org/ - Pytest Testing Framework",
                        "https://www.coursera.org/learn/python-data - Python for Data Science (Coursera)",
                        "Fluent Python by Luciano Ramalho - ISBN 9781491946008"
                    ]
                },
                {
                    "level": 3,
                    "title": "Advanced Python Applications",
                    "description": "Master advanced techniques, specialized applications, and expert-level Python development",
                    "topics": [
                        "Web development with Django and Flask",
                        "Data science with pandas, numpy, and matplotlib",
                        "Machine learning with scikit-learn and TensorFlow",
                        "Automation and scripting for system administration",
                        "API development and microservices architecture"
                    ],
                    "resources": [
                        "https://www.djangoproject.com/ - Django Web Framework",
                        "https://flask.palletsprojects.com/ - Flask Web Framework",
                        "https://pandas.pydata.org/ - Pandas for Data Science",
                        "https://scikit-learn.org/ - Scikit-learn for Machine Learning",
                        "https://fastapi.tiangolo.com/ - FastAPI for APIs",
                        "Effective Python by Brett Slatkin - ISBN 9780134853987"
                    ]
                },
                {
                    "level": 4,
                    "title": "Specialization and Mastery in Python",
                    "description": "Focus on specialized areas, industry applications, and achieving mastery in specific Python domains",
                    "topics": [
                        "DevOps and infrastructure automation with Python",
                        "Cybersecurity and penetration testing tools",
                        "Game development with Pygame and Unity Python",
                        "Scientific computing and research applications",
                        "Contributing to open source Python projects"
                    ],
                    "resources": [
                        "https://www.ansible.com/ - Ansible Automation Platform",
                        "https://www.python.org/dev/ - Python Development Guide",
                        "https://github.com/topics/python - GitHub Python Projects",
                        "https://pypi.org/ - Python Package Index",
                        "https://www.python.org/community/ - Python Community",
                        "Python Cookbook by David Beazley & Brian K. Jones - ISBN 9781449340377"
                    ]
                },
                {
                    "level": 5,
                    "title": "Expert Level and Innovation in Python",
                    "description": "Achieve expert status, contribute to the Python ecosystem, and drive innovation in Python development",
                    "topics": [
                        "Python core development and language design",
                        "Performance optimization and C extensions",
                        "Advanced metaprogramming and decorators",
                        "Teaching and mentoring Python developers",
                        "Industry leadership and thought leadership in Python"
                    ],
                    "resources": [
                        "https://www.python.org/dev/core-mentorship/ - Python Core Mentorship",
                        "https://www.python.org/dev/peps/ - Python Enhancement Proposals",
                        "https://www.python.org/community/workshops/ - Python Workshops",
                        "https://www.python.org/community/awards/ - Python Community Awards",
                        "https://www.python.org/community/sigs/ - Python Special Interest Groups",
                        "Python in Practice by Mark Summerfield - ISBN 9780321905635"
                    ]
                }
            ],
            "estimated_time": "12-24 months for complete mastery",
            "prerequisites": [
                "Basic computer literacy and internet skills",
                "Strong analytical and problem-solving abilities",
                "Commitment to continuous learning and practice",
                "Time management and self-discipline",
                "Curiosity and passion for programming"
            ],
            "learning_tips": [
                "Practice coding daily with real projects",
                "Join Python communities on Reddit, Discord, and Stack Overflow",
                "Follow Python experts like Guido van Rossum and Raymond Hettinger",
                "Attend PyCon conferences and local Python meetups",
                "Build a portfolio of Python projects on GitHub",
                "Stay updated with Python releases and new features",
                "Network with Python developers and contribute to open source",
                "Consider Python certifications and advanced courses"
            ]
        }
    elif 'web development' in topic_lower or 'web dev' in topic_lower:
        return {
            "title": f"Comprehensive Learning Roadmap for {topic}",
            "description": f"A detailed, step-by-step guide to master {topic} from beginner to expert level",
            "steps": [
                {
                    "level": 1,
                    "title": "Foundation and Basics of Web Development",
                    "description": "Build a strong foundation with fundamental web technologies, HTML, CSS, and JavaScript basics",
                    "topics": [
                        "HTML5 semantic markup and document structure",
                        "CSS3 styling, layouts, and responsive design",
                        "JavaScript ES6+ fundamentals and DOM manipulation",
                        "Web accessibility standards and best practices",
                        "Basic web hosting and domain management"
                    ],
                    "resources": [
                        "https://developer.mozilla.org/en-US/docs/Web/HTML - MDN HTML Guide",
                        "https://developer.mozilla.org/en-US/docs/Web/CSS - MDN CSS Guide",
                        "https://developer.mozilla.org/en-US/docs/Web/JavaScript - MDN JavaScript Guide",
                        "https://www.freecodecamp.org/ - FreeCodeCamp (Free Courses)",
                        "https://www.udemy.com/course/the-complete-web-developer-bootcamp/ - Web Developer Bootcamp (Udemy)",
                        "HTML and CSS: Design and Build Websites by Jon Duckett - ISBN 9781118008188"
                    ]
                },
                {
                    "level": 2,
                    "title": "Intermediate Web Development",
                    "description": "Dive deeper into modern JavaScript frameworks, build tools, and intermediate-level web development skills",
                    "topics": [
                        "Modern JavaScript frameworks (React, Vue, Angular)",
                        "State management and component architecture",
                        "Build tools and bundlers (Webpack, Vite, Parcel)",
                        "CSS preprocessors and modern CSS frameworks",
                        "Version control with Git and collaborative development"
                    ],
                    "resources": [
                        "https://react.dev/ - React Official Documentation",
                        "https://vuejs.org/ - Vue.js Official Guide",
                        "https://angular.io/ - Angular Official Documentation",
                        "https://redux.js.org/ - Redux State Management",
                        "https://webpack.js.org/ - Webpack Build Tool",
                        "Learning React by Alex Banks & Eve Porcello - ISBN 9781491954614"
                    ]
                },
                {
                    "level": 3,
                    "title": "Advanced Web Development",
                    "description": "Master backend development, databases, APIs, and full-stack web applications",
                    "topics": [
                        "Server-side development with Node.js and Express",
                        "Database design and management (SQL and NoSQL)",
                        "RESTful API development and GraphQL",
                        "Authentication and authorization systems",
                        "Cloud deployment and DevOps practices"
                    ],
                    "resources": [
                        "https://nodejs.org/en/docs/ - Node.js Documentation",
                        "https://expressjs.com/ - Express.js Framework",
                        "https://www.mongodb.com/ - MongoDB Database",
                        "https://www.postgresql.org/ - PostgreSQL Database",
                        "https://vercel.com/ - Vercel Deployment Platform",
                        "Node.js Design Patterns by Mario Casciaro - ISBN 9781785885587"
                    ]
                },
                {
                    "level": 4,
                    "title": "Specialization and Mastery in Web Development",
                    "description": "Focus on specialized areas, performance optimization, and achieving mastery in specific web development domains",
                    "topics": [
                        "Performance optimization and Core Web Vitals",
                        "Progressive Web Apps (PWA) and mobile development",
                        "Security best practices and vulnerability prevention",
                        "Testing strategies and quality assurance",
                        "Contributing to open source web projects"
                    ],
                    "resources": [
                        "https://web.dev/performance/ - Web Performance Guide",
                        "https://developers.google.com/web/progressive-web-apps - PWA Documentation",
                        "https://owasp.org/www-project-top-ten/ - OWASP Security Guidelines",
                        "https://jestjs.io/ - Jest Testing Framework",
                        "https://github.com/topics/web-development - GitHub Web Development Projects",
                        "High Performance Web Sites by Steve Souders - ISBN 9780596529307"
                    ]
                },
                {
                    "level": 5,
                    "title": "Expert Level and Innovation in Web Development",
                    "description": "Achieve expert status, contribute to web standards, and drive innovation in web development",
                    "topics": [
                        "Web standards and browser development",
                        "Advanced architecture patterns and microservices",
                        "Machine learning integration in web applications",
                        "Teaching and mentoring web developers",
                        "Industry leadership and thought leadership in web development"
                    ],
                    "resources": [
                        "https://www.w3.org/ - World Wide Web Consortium",
                        "https://developer.mozilla.org/en-US/docs/Web/API - Web APIs Documentation",
                        "https://www.webassembly.org/ - WebAssembly",
                        "https://www.tensorflow.org/js - TensorFlow.js",
                        "https://www.webcomponents.org/ - Web Components",
                        "Web Development with Node and Express by Ethan Brown - ISBN 9781491949306"
                    ]
                }
            ],
            "estimated_time": "12-24 months for complete mastery",
            "prerequisites": [
                "Basic computer literacy and internet skills",
                "Strong analytical and problem-solving abilities",
                "Commitment to continuous learning and practice",
                "Time management and self-discipline",
                "Curiosity and passion for web technologies"
            ],
            "learning_tips": [
                "Build real projects and deploy them online",
                "Join web development communities on Reddit, Discord, and Stack Overflow",
                "Follow web development experts and stay updated with new technologies",
                "Attend web development conferences and local meetups",
                "Build a portfolio of web projects on GitHub",
                "Stay updated with browser updates and web standards",
                "Network with web developers and contribute to open source",
                "Consider web development certifications and advanced courses"
            ]
        }
    elif 'data science' in topic_lower:
        return {
            "title": f"Comprehensive Learning Roadmap for {topic}",
            "description": f"A detailed, step-by-step guide to master {topic} - extracting insights from data",
            "steps": [
                {
                    "level": 1,
                    "title": "Foundation and Basics of Data Science",
                    "description": "Build a strong foundation with fundamental data science concepts, tools, and basic analytical skills",
                    "topics": [
                        "Python programming for data science",
                        "Pandas and NumPy for data manipulation",
                        "Data visualization with matplotlib and seaborn",
                        "Basic statistics and probability concepts",
                        "Data cleaning and preprocessing techniques"
                    ],
                    "resources": [
                        "https://www.coursera.org/specializations/data-science-python - Applied Data Science with Python (Coursera)",
                        "https://www.udemy.com/course/python-for-data-science-and-machine-learning-bootcamp/ - Python for Data Science (Udemy)",
                        "https://pandas.pydata.org/ - Pandas Documentation",
                        "https://numpy.org/ - NumPy Documentation",
                        "https://seaborn.pydata.org/ - Seaborn Visualization Library",
                        "Python for Data Analysis by Wes McKinney - ISBN 9781491957660"
                    ]
                },
                {
                    "level": 2,
                    "title": "Intermediate Data Science",
                    "description": "Dive deeper into machine learning algorithms, data analysis, and intermediate-level data science skills",
                    "topics": [
                        "Supervised and unsupervised learning algorithms",
                        "Feature engineering and selection techniques",
                        "Model evaluation and validation methods",
                        "Advanced statistical analysis and hypothesis testing",
                        "SQL and database management for data science"
                    ],
                    "resources": [
                        "https://scikit-learn.org/ - Scikit-learn Machine Learning",
                        "https://www.coursera.org/learn/machine-learning - Machine Learning Course (Coursera)",
                        "https://www.kaggle.com/learn - Kaggle Learn (Free Courses)",
                        "https://www.fast.ai/ - Fast.ai Practical Deep Learning",
                        "https://www.datacamp.com/ - DataCamp Interactive Courses",
                        "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow by Aurélien Géron - ISBN 9781492032649"
                    ]
                },
                {
                    "level": 3,
                    "title": "Advanced Data Science Applications",
                    "description": "Master advanced techniques, specialized applications, and expert-level data science development",
                    "topics": [
                        "Deep learning with neural networks and TensorFlow/PyTorch",
                        "Big data processing with Spark and distributed computing",
                        "Natural language processing and text analytics",
                        "Computer vision and image processing",
                        "Time series analysis and forecasting"
                    ],
                    "resources": [
                        "https://pytorch.org/ - PyTorch Deep Learning",
                        "https://www.tensorflow.org/ - TensorFlow Deep Learning",
                        "https://spark.apache.org/mllib/ - Apache Spark MLlib",
                        "https://www.openai.com/research/ - OpenAI Research",
                        "https://deepmind.com/research - DeepMind Research",
                        "Reinforcement Learning: An Introduction by Richard S. Sutton - ISBN 9780262039246"
                    ]
                },
                {
                    "level": 4,
                    "title": "Specialization and Mastery in Data Science",
                    "description": "Focus on specialized areas, industry applications, and achieving mastery in specific data science domains",
                    "topics": [
                        "MLOps and model deployment in production",
                        "Business intelligence and data engineering",
                        "Advanced research methodologies and experimental design",
                        "Domain-specific applications (finance, healthcare, etc.)",
                        "Contributing to open source data science projects"
                    ],
                    "resources": [
                        "https://mlflow.org/ - MLflow Model Management",
                        "https://www.kubeflow.org/ - Kubeflow MLOps",
                        "https://www.tableau.com/ - Tableau Business Intelligence",
                        "https://airflow.apache.org/ - Apache Airflow",
                        "https://github.com/topics/data-science - GitHub Data Science Projects",
                        "Designing Data-Intensive Applications by Martin Kleppmann - ISBN 9781449373320"
                    ]
                },
                {
                    "level": 5,
                    "title": "Expert Level and Innovation in Data Science",
                    "description": "Achieve expert status, contribute to the data science field, and drive innovation in data science",
                    "topics": [
                        "Cutting-edge research in machine learning and AI",
                        "Innovation in data science methodologies and tools",
                        "Teaching and mentoring data scientists",
                        "Industry leadership and thought leadership",
                        "Contributing to data science research and publications"
                    ],
                    "resources": [
                        "https://arxiv.org/cs.AI - arXiv AI Research Papers",
                        "https://papers.nips.cc/ - NeurIPS Conference Papers",
                        "https://icml.cc/ - ICML Conference Papers",
                        "https://www.kdd.org/ - KDD Conference Papers",
                        "https://www.researchgate.net/topic/Data-Science - ResearchGate Data Science",
                        "The Elements of Statistical Learning by Trevor Hastie, Robert Tibshirani, and Jerome Friedman - ISBN 9780387848570"
                    ]
                }
            ],
            "estimated_time": "12-24 months for complete mastery",
            "prerequisites": [
                "Basic programming knowledge and mathematical fundamentals",
                "Strong analytical and problem-solving abilities",
                "Commitment to continuous learning and practice",
                "Time management and self-discipline",
                "Curiosity and passion for data and insights"
            ],
            "learning_tips": [
                "Work on real data science projects and competitions",
                "Join data science communities on Kaggle, Reddit, and Discord",
                "Follow data science experts and stay updated with new techniques",
                "Attend data science conferences and local meetups",
                "Build a portfolio of data science projects on GitHub",
                "Stay updated with latest research papers and methodologies",
                "Network with data scientists and contribute to open source",
                "Consider data science certifications and advanced degrees"
            ]
        }
    elif 'machine learning' in topic_lower or 'ml' in topic_lower:
        return {
            "title": f"Comprehensive Learning Roadmap for {topic}",
            "description": f"A detailed, step-by-step guide to master {topic} - building intelligent systems",
            "steps": [
                {
                    "level": 1,
                    "title": "Foundation and Basics of Machine Learning",
                    "description": "Build a strong foundation with fundamental machine learning concepts, algorithms, and mathematical principles",
                    "topics": [
                        "Supervised and unsupervised learning fundamentals",
                        "Linear regression and classification algorithms",
                        "Model evaluation and validation techniques",
                        "Basic statistics and probability for ML",
                        "Data preprocessing and feature engineering basics"
                    ],
                    "resources": [
                        "https://www.coursera.org/learn/machine-learning - Machine Learning Course (Coursera)",
                        "https://scikit-learn.org/stable/tutorial/ - Scikit-learn Tutorial",
                        "https://www.udemy.com/course/machinelearning/ - Machine Learning A-Z (Udemy)",
                        "https://www.kaggle.com/learn/intro-to-machine-learning - Kaggle ML Intro",
                        "https://developers.google.com/machine-learning/crash-course - Google ML Crash Course",
                        "Pattern Recognition and Machine Learning by Christopher Bishop - ISBN 9780387310732"
                    ]
                },
                {
                    "level": 2,
                    "title": "Intermediate Machine Learning",
                    "description": "Dive deeper into advanced algorithms, neural networks, and intermediate-level machine learning skills",
                    "topics": [
                        "Neural networks and deep learning fundamentals",
                        "Natural language processing basics",
                        "Computer vision and image processing",
                        "Ensemble methods and advanced algorithms",
                        "Hyperparameter tuning and model optimization"
                    ],
                    "resources": [
                        "https://www.deeplearning.ai/ - Deep Learning Specialization (Coursera)",
                        "https://pytorch.org/tutorials/ - PyTorch Tutorials",
                        "https://www.tensorflow.org/tutorials - TensorFlow Tutorials",
                        "https://huggingface.co/courses - Hugging Face NLP Course",
                        "https://www.fast.ai/ - Fast.ai Practical Deep Learning",
                        "Deep Learning with Python by François Chollet - ISBN 9781617294433"
                    ]
                },
                {
                    "level": 3,
                    "title": "Advanced Machine Learning Applications",
                    "description": "Master advanced techniques, specialized applications, and expert-level machine learning development",
                    "topics": [
                        "Advanced deep learning architectures (CNN, RNN, Transformer)",
                        "Reinforcement learning and AI agents",
                        "MLOps and model deployment in production",
                        "Big data processing and distributed ML",
                        "Research methodologies and experimental design"
                    ],
                    "resources": [
                        "https://mlflow.org/ - MLflow Model Management",
                        "https://www.kubeflow.org/ - Kubeflow MLOps",
                        "https://spark.apache.org/mllib/ - Apache Spark MLlib",
                        "https://www.openai.com/research/ - OpenAI Research",
                        "https://deepmind.com/research - DeepMind Research",
                        "Reinforcement Learning: An Introduction by Richard S. Sutton - ISBN 9780262039246"
                    ]
                },
                {
                    "level": 4,
                    "title": "Specialization and Mastery in Machine Learning",
                    "description": "Focus on specialized areas, industry applications, and achieving mastery in specific ML domains",
                    "topics": [
                        "Domain-specific ML applications (finance, healthcare, etc.)",
                        "Advanced research in ML and AI",
                        "ML ethics and responsible AI development",
                        "Teaching and mentoring ML practitioners",
                        "Contributing to open source ML projects"
                    ],
                    "resources": [
                        "https://arxiv.org/cs.AI - arXiv AI Research Papers",
                        "https://papers.nips.cc/ - NeurIPS Conference Papers",
                        "https://icml.cc/ - ICML Conference Papers",
                        "https://www.kdd.org/ - KDD Conference Papers",
                        "https://github.com/topics/machine-learning - GitHub ML Projects",
                        "The Hundred-Page Machine Learning Book by Andriy Burkov - ISBN 9781999579500"
                    ]
                },
                {
                    "level": 5,
                    "title": "Expert Level and Innovation in Machine Learning",
                    "description": "Achieve expert status, contribute to the ML field, and drive innovation in machine learning",
                    "topics": [
                        "Cutting-edge research and breakthrough applications",
                        "Innovation in ML algorithms and methodologies",
                        "Industry leadership and thought leadership",
                        "Contributing to ML research and publications",
                        "Advancing the field of artificial intelligence"
                    ],
                    "resources": [
                        "https://www.researchgate.net/topic/Machine-Learning - ResearchGate ML",
                        "https://www.academia.edu/search?q=machine+learning - Academia.edu ML Research",
                        "https://www.semanticscholar.org/search?q=machine+learning - Semantic Scholar ML Papers",
                        "https://www.jstor.org/action/doBasicSearch?Query=machine+learning - JSTOR ML Articles",
                        "https://www.meetup.com/find/?keywords=machine+learning - ML Meetup Groups",
                        "Machine Learning: A Probabilistic Perspective by Kevin P. Murphy - ISBN 9780262018029"
                    ]
                }
            ],
            "estimated_time": "12-24 months for complete mastery",
            "prerequisites": [
                "Strong mathematical foundation (linear algebra, calculus, statistics)",
                "Programming experience in Python or similar languages",
                "Strong analytical and problem-solving abilities",
                "Commitment to continuous learning and practice",
                "Curiosity and passion for artificial intelligence"
            ],
            "learning_tips": [
                "Work on real ML projects and participate in competitions",
                "Join ML communities on Kaggle, Reddit, and Discord",
                "Follow ML experts and stay updated with new research",
                "Attend ML conferences and local meetups",
                "Build a portfolio of ML projects on GitHub",
                "Stay updated with latest research papers and breakthroughs",
                "Network with ML practitioners and contribute to open source",
                "Consider ML certifications and advanced degrees"
            ]
        }
    elif 'javascript' in topic_lower or 'js' in topic_lower:
        return {
            "title": f"Comprehensive Learning Roadmap for {topic}",
            "description": f"A detailed, step-by-step guide to master {topic} programming from beginner to expert level",
            "steps": [
                {
                    "level": 1,
                    "title": "Foundation and Basics of JavaScript",
                    "description": "Build a strong foundation with fundamental JavaScript concepts, syntax, and basic programming principles",
                    "topics": [
                        "JavaScript variables, data types, and basic operations",
                        "Control flow: conditionals, loops, and functions",
                        "Arrays, objects, and basic data structures",
                        "DOM manipulation and event handling",
                        "Basic error handling and debugging"
                    ],
                    "resources": [
                        "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide - MDN JavaScript Guide",
                        "https://javascript.info/ - Modern JavaScript Tutorial",
                        "https://www.udemy.com/course/the-complete-javascript-course/ - Complete JavaScript Course (Udemy)",
                        "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/ - FreeCodeCamp JavaScript",
                        "https://eloquentjavascript.net/ - Eloquent JavaScript by Marijn Haverbeke - ISBN 9781593279509"
                    ]
                },
                {
                    "level": 2,
                    "title": "Intermediate JavaScript Programming",
                    "description": "Dive deeper into modern JavaScript features, asynchronous programming, and intermediate-level skills",
                    "topics": [
                        "ES6+ features and modern JavaScript syntax",
                        "Asynchronous programming with Promises and async/await",
                        "Modules and module systems (ES6 modules, CommonJS)",
                        "Advanced error handling and debugging techniques",
                        "Testing with Jest and other testing frameworks"
                    ],
                    "resources": [
                        "https://es6-features.org/ - ES6 Features Guide",
                        "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise - Promises Guide",
                        "https://jestjs.io/ - Jest Testing Framework",
                        "https://www.udemy.com/course/advanced-javascript-concepts/ - Advanced JavaScript (Udemy)",
                        "https://github.com/getify/You-Dont-Know-JS - You Don't Know JS by Kyle Simpson - ISBN 9781491904244"
                    ]
                },
                {
                    "level": 3,
                    "title": "Advanced JavaScript Applications",
                    "description": "Master JavaScript frameworks, build tools, and advanced web development applications",
                    "topics": [
                        "Modern JavaScript frameworks (React, Vue, Angular)",
                        "Node.js and server-side JavaScript development",
                        "Build tools and bundlers (Webpack, Vite, Parcel)",
                        "Package management and dependency handling",
                        "Performance optimization and best practices"
                    ],
                    "resources": [
                        "https://react.dev/ - React Official Documentation",
                        "https://nodejs.org/en/docs/ - Node.js Documentation",
                        "https://expressjs.com/ - Express.js Framework",
                        "https://webpack.js.org/ - Webpack Build Tool",
                        "https://www.npmjs.com/ - npm Package Manager",
                        "JavaScript: The Good Parts by Douglas Crockford - ISBN 9780596517748"
                    ]
                },
                {
                    "level": 4,
                    "title": "Specialization and Mastery in JavaScript",
                    "description": "Focus on specialized areas, advanced frameworks, and achieving mastery in specific JavaScript domains",
                    "topics": [
                        "Advanced React patterns and state management",
                        "Full-stack JavaScript development",
                        "JavaScript security and vulnerability prevention",
                        "Testing strategies and quality assurance",
                        "Contributing to open source JavaScript projects"
                    ],
                    "resources": [
                        "https://redux.js.org/ - Redux State Management",
                        "https://nextjs.org/ - Next.js Full-Stack Framework",
                        "https://owasp.org/www-project-top-ten/ - OWASP Security Guidelines",
                        "https://testing-library.com/ - Testing Library",
                        "https://github.com/topics/javascript - GitHub JavaScript Projects",
                        "Learning React by Alex Banks & Eve Porcello - ISBN 9781491954614"
                    ]
                },
                {
                    "level": 5,
                    "title": "Expert Level and Innovation in JavaScript",
                    "description": "Achieve expert status, contribute to JavaScript standards, and drive innovation in JavaScript development",
                    "topics": [
                        "JavaScript engine internals and performance optimization",
                        "Advanced architecture patterns and design principles",
                        "JavaScript standards and TC39 proposals",
                        "Teaching and mentoring JavaScript developers",
                        "Industry leadership and thought leadership in JavaScript"
                    ],
                    "resources": [
                        "https://tc39.es/ - TC39 JavaScript Standards",
                        "https://v8.dev/ - V8 JavaScript Engine",
                        "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference - JavaScript Reference",
                        "https://www.ecma-international.org/ - ECMA International",
                        "https://www.javascript.com/ - JavaScript.com Resources",
                        "You Don't Know JS: Up & Going by Kyle Simpson - ISBN 9781491924464"
                    ]
                }
            ],
            "estimated_time": "12-24 months for complete mastery",
            "prerequisites": [
                "Basic HTML and CSS knowledge",
                "Programming fundamentals and logical thinking",
                "Understanding of web browsers and web technologies",
                "Commitment to continuous learning and practice",
                "Curiosity and passion for web development"
            ],
            "learning_tips": [
                "Build real JavaScript projects and deploy them online",
                "Join JavaScript communities on Reddit, Discord, and Stack Overflow",
                "Follow JavaScript experts and stay updated with new features",
                "Attend JavaScript conferences and local meetups",
                "Build a portfolio of JavaScript projects on GitHub",
                "Stay updated with JavaScript releases and new proposals",
                "Network with JavaScript developers and contribute to open source",
                "Consider JavaScript certifications and advanced courses"
            ]
        }
    else:
        # Generic but more specific default roadmap with 5 levels
        return {
            "title": f"Comprehensive Learning Roadmap for {topic}",
            "description": f"A detailed, step-by-step guide to master {topic} from beginner to expert level",
            "steps": [
                {
                    "level": 1,
                    "title": f"Foundation and Basics of {topic}",
                    "description": f"Build a strong foundation with fundamental {topic} concepts, terminology, and basic principles",
                    "topics": [
                        f"Core concepts and definitions in {topic}",
                        f"Historical background and evolution of {topic}",
                        f"Basic terminology and vocabulary",
                        f"Fundamental principles and theories",
                        f"Essential tools and resources for {topic}"
                    ],
                    "resources": [
                        f"https://www.coursera.org/search?query={topic} - Coursera {topic} Courses",
                        f"https://www.udemy.com/topic/{topic.lower().replace(' ', '-')}/ - Udemy {topic} Courses",
                        f"https://www.edx.org/search?q={topic} - edX {topic} Programs",
                        f"https://www.youtube.com/results?search_query={topic}+tutorial - YouTube {topic} Tutorials",
                        f"https://www.khanacademy.org/search?page_search_query={topic} - Khan Academy {topic} Content"
                    ]
                },
                {
                    "level": 2,
                    "title": f"Intermediate Concepts in {topic}",
                    "description": f"Dive deeper into advanced concepts, practical applications, and intermediate-level skills in {topic}",
                    "topics": [
                        f"Advanced theories and methodologies in {topic}",
                        f"Practical applications and case studies",
                        f"Problem-solving techniques specific to {topic}",
                        f"Industry best practices and standards",
                        f"Integration with related fields and technologies"
                    ],
                    "resources": [
                        f"https://www.linkedin.com/learning/search?keywords={topic} - LinkedIn Learning {topic} Courses",
                        f"https://www.pluralsight.com/search?q={topic} - Pluralsight {topic} Paths",
                        f"https://www.skillshare.com/search?query={topic} - Skillshare {topic} Classes",
                        f"https://www.datacamp.com/search?q={topic} - DataCamp {topic} Tracks",
                        f"https://www.codecademy.com/search?query={topic} - Codecademy {topic} Courses"
                    ]
                },
                {
                    "level": 3,
                    "title": f"Advanced Applications of {topic}",
                    "description": f"Master advanced techniques, specialized applications, and expert-level skills in {topic}",
                    "topics": [
                        f"Expert-level techniques and methodologies",
                        f"Specialized applications and use cases",
                        f"Research and innovation in {topic}",
                        f"Performance optimization and advanced strategies",
                        f"Emerging trends and future directions"
                    ],
                    "resources": [
                        f"https://www.oreilly.com/search/?query={topic} - O'Reilly {topic} Books and Courses",
                        f"https://www.packtpub.com/search?query={topic} - Packt {topic} Publications",
                        f"https://www.manning.com/search?q={topic} - Manning {topic} Books",
                        f"https://www.springer.com/search?query={topic} - Springer {topic} Publications",
                        f"https://scholar.google.com/scholar?q={topic} - Google Scholar {topic} Research"
                    ]
                },
                {
                    "level": 4,
                    "title": f"Specialization and Mastery in {topic}",
                    "description": f"Focus on specialized areas, industry applications, and achieving mastery in specific aspects of {topic}",
                    "topics": [
                        f"Specialized sub-fields within {topic}",
                        f"Industry-specific applications and implementations",
                        f"Advanced research methodologies",
                        f"Leadership and expertise development",
                        f"Contributing to the {topic} community and field"
                    ],
                    "resources": [
                        f"https://www.researchgate.net/search/publication?q={topic} - ResearchGate {topic} Publications",
                        f"https://arxiv.org/search/?query={topic} - arXiv {topic} Papers",
                        f"https://www.academia.edu/search?q={topic} - Academia.edu {topic} Research",
                        f"https://www.semanticscholar.org/search?q={topic} - Semantic Scholar {topic} Papers",
                        f"https://www.jstor.org/action/doBasicSearch?Query={topic} - JSTOR {topic} Articles"
                    ]
                },
                {
                    "level": 5,
                    "title": f"Expert Level and Innovation in {topic}",
                    "description": f"Achieve expert status, contribute to the field, and drive innovation in {topic}",
                    "topics": [
                        f"Cutting-edge research and developments",
                        f"Innovation and breakthrough applications",
                        f"Teaching and mentoring in {topic}",
                        f"Industry leadership and thought leadership",
                        f"Contributing to open source and community projects"
                    ],
                    "resources": [
                        f"https://github.com/topics/{topic.lower().replace(' ', '-')} - GitHub {topic} Projects",
                        f"https://stackoverflow.com/questions/tagged/{topic.lower().replace(' ', '-')} - Stack Overflow {topic} Community",
                        f"https://www.reddit.com/r/{topic.lower().replace(' ', '')}/ - Reddit {topic} Community",
                        f"https://www.meetup.com/find/?keywords={topic} - Meetup {topic} Groups",
                        f"https://www.conferenceindex.org/conferences/{topic.lower().replace(' ', '-')} - {topic} Conferences and Events"
                    ]
                }
            ],
            "estimated_time": "12-24 months for complete mastery",
            "prerequisites": [
                "Basic computer literacy and internet skills",
                "Strong analytical and problem-solving abilities",
                "Commitment to continuous learning and practice",
                "Time management and self-discipline",
                f"Curiosity and passion for {topic}"
            ],
            "learning_tips": [
                "Practice regularly with hands-on projects",
                "Join online communities and forums",
                "Follow industry experts and thought leaders",
                "Attend workshops, conferences, and meetups",
                "Build a portfolio of projects and contributions",
                "Stay updated with latest trends and developments",
                "Network with professionals in the field",
                "Consider certifications and advanced degrees"
            ]
        }

def display_roadmap(roadmap):
    """
    Display the roadmap in a readable format.
    """
    if not roadmap:
        print("Failed to generate roadmap.")
        return
    
    print(f"\n{roadmap['title']}")
    print("=" * 50)
    print(f"{roadmap['description']}\n")
    
    if 'prerequisites' in roadmap:
        print("Prerequisites:")
        for prereq in roadmap['prerequisites']:
            print(f"  • {prereq}")
        print()
    
    if 'estimated_time' in roadmap:
        print(f"Estimated Time: {roadmap['estimated_time']}\n")
    
    print("Learning Path:")
    for i, step in enumerate(roadmap['steps'], 1):
        print(f"\nStep {i}: {step['title']}")
        print(f"Level: {step['level']}")
        print(f"Description: {step['description']}")
        
        if 'topics' in step:
            print("Topics:")
            for topic in step['topics']:
                print(f"  • {topic}")
        
        if 'resources' in step:
            print("Resources:")
            for resource in step['resources']:
                print(f"  • {resource}")
        print("-" * 30)

def main():
    """
    Main function to run the roadmap generator.
    """
    print("AI Learning Roadmap Generator")
    print("=" * 30)
    
    while True:
        topic = input("\nEnter a topic (or 'quit' to exit): ")
        
        if topic.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not topic.strip():
            print("Please enter a valid topic.")
            continue
        
        roadmap = generate_roadmap(topic)
        display_roadmap(roadmap)
        
        again = input("\nGenerate another roadmap? (y/n): ")
        if again.lower() not in ['y', 'yes']:
            print("Goodbye!")
            break

if __name__ == "__main__":
    main() 