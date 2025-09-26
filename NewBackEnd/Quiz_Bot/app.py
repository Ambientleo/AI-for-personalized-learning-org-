from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
from werkzeug.utils import secure_filename
import logging
import random
from typing import List, Dict, Any
import ollama
import PyPDF2
from docx import Document
import re
import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urlparse, urljoin
import concurrent.futures
from datetime import datetime, timezone
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# History storage (in production, use a proper database)
USER_HISTORY_FILE = 'user_history.json'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class UserHistoryManager:
    """Manages user history including quizzes, chats, and topics"""
    
    def __init__(self):
        self.history_file = USER_HISTORY_FILE
        self.history = self.load_history()
    
    def load_history(self) -> Dict[str, Any]:
        """Load user history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            logger.error(f"Error loading history: {str(e)}")
            return {}
    
    def save_history(self):
        """Save user history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving history: {str(e)}")
    
    def get_user_history(self, user_id: str) -> Dict[str, Any]:
        """Get history for a specific user"""
        if user_id not in self.history:
            self.history[user_id] = {
                'quizzes': [],
                'chats': [],
                'topics': [],
                'created_at': datetime.now(timezone.utc).isoformat(),
                'last_activity': datetime.now(timezone.utc).isoformat()
            }
        return self.history[user_id]
    
    def add_quiz_history(self, user_id: str, quiz_data: Dict[str, Any]):
        """Add quiz to user history"""
        user_history = self.get_user_history(user_id)
        
        quiz_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'topic': quiz_data.get('topic', 'Unknown'),
            'source_type': quiz_data.get('source_type', 'topic'),
            'num_questions': quiz_data.get('num_questions', 0),
            'score': quiz_data.get('score', 0),
            'total_questions': quiz_data.get('total_questions', 0),
            'score_percentage': quiz_data.get('score_percentage', 0),
            'ollama_used': quiz_data.get('ollama_used', False),
            'questions': quiz_data.get('questions', []),
            'results': quiz_data.get('results', []),
            'input_content': quiz_data.get('input_content', ''),
            'filename': quiz_data.get('filename', ''),
            'url': quiz_data.get('url', '')
        }
        
        user_history['quizzes'].append(quiz_entry)
        user_history['last_activity'] = datetime.now(timezone.utc).isoformat()
        
        # Keep only last 50 quizzes
        if len(user_history['quizzes']) > 50:
            user_history['quizzes'] = user_history['quizzes'][-50:]
        
        self.save_history()
        logger.info(f"Added quiz history for user {user_id}")
    
    def add_chat_history(self, user_id: str, chat_data: Dict[str, Any]):
        """Add chat interaction to user history"""
        user_history = self.get_user_history(user_id)
        
        chat_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'message': chat_data.get('message', ''),
            'response': chat_data.get('response', ''),
            'topic': chat_data.get('topic', ''),
            'type': chat_data.get('type', 'general')
        }
        
        user_history['chats'].append(chat_entry)
        user_history['last_activity'] = datetime.now(timezone.utc).isoformat()
        
        # Keep only last 100 chats
        if len(user_history['chats']) > 100:
            user_history['chats'] = user_history['chats'][-100:]
        
        self.save_history()
        logger.info(f"Added chat history for user {user_id}")
    
    def add_topic_history(self, user_id: str, topic: str, source_type: str = 'topic'):
        """Add topic to user history"""
        user_history = self.get_user_history(user_id)
        
        # Check if topic already exists
        existing_topics = [t for t in user_history['topics'] if t['topic'].lower() == topic.lower()]
        
        if existing_topics:
            # Update existing topic
            existing_topics[0]['count'] += 1
            existing_topics[0]['last_used'] = datetime.now(timezone.utc).isoformat()
            existing_topics[0]['source_types'].add(source_type)
        else:
            # Add new topic
            topic_entry = {
                'id': str(uuid.uuid4()),
                'topic': topic,
                'count': 1,
                'first_used': datetime.now(timezone.utc).isoformat(),
                'last_used': datetime.now(timezone.utc).isoformat(),
                'source_types': {source_type}
            }
            user_history['topics'].append(topic_entry)
        
        user_history['last_activity'] = datetime.now(timezone.utc).isoformat()
        
        # Keep only last 100 topics
        if len(user_history['topics']) > 100:
            user_history['topics'] = sorted(
                user_history['topics'], 
                key=lambda x: x['last_used'], 
                reverse=True
            )[:100]
        
        self.save_history()
        logger.info(f"Added topic history for user {user_id}: {topic}")
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        user_history = self.get_user_history(user_id)
        
        total_quizzes = len(user_history['quizzes'])
        total_chats = len(user_history['chats'])
        total_topics = len(user_history['topics'])
        
        # Calculate average quiz score
        quiz_scores = [q['score_percentage'] for q in user_history['quizzes'] if q.get('score_percentage')]
        avg_score = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0
        
        # Get most used topics
        sorted_topics = sorted(user_history['topics'], key=lambda x: x['count'], reverse=True)
        top_topics = sorted_topics[:5] if sorted_topics else []
        
        # Get recent activity
        recent_quizzes = sorted(user_history['quizzes'], key=lambda x: x['timestamp'], reverse=True)[:5]
        recent_chats = sorted(user_history['chats'], key=lambda x: x['timestamp'], reverse=True)[:5]
        
        return {
            'total_quizzes': total_quizzes,
            'total_chats': total_chats,
            'total_topics': total_topics,
            'average_score': round(avg_score, 2),
            'top_topics': top_topics,
            'recent_quizzes': recent_quizzes,
            'recent_chats': recent_chats,
            'created_at': user_history.get('created_at'),
            'last_activity': user_history.get('last_activity')
        }
    
    def clear_user_history(self, user_id: str, history_type: str = 'all'):
        """Clear user history"""
        if user_id in self.history:
            if history_type == 'all':
                del self.history[user_id]
            elif history_type == 'quizzes':
                self.history[user_id]['quizzes'] = []
            elif history_type == 'chats':
                self.history[user_id]['chats'] = []
            elif history_type == 'topics':
                self.history[user_id]['topics'] = []
            
            self.save_history()
            logger.info(f"Cleared {history_type} history for user {user_id}")

# Initialize history manager
history_manager = UserHistoryManager()

class WebScraper:
    """Web scraping utility for gathering content from URLs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape content from a URL"""
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid URL format")
            
            # Fetch the page
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text content
            text_content = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text_content.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text_content = ' '.join(chunk for chunk in chunks if chunk)
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text() if title else "No title found"
            
            # Extract main content areas
            main_content = ""
            for tag in soup.find_all(['article', 'main', 'section', 'div']):
                if tag.get('class') and any('content' in cls.lower() for cls in tag.get('class')):
                    main_content += tag.get_text() + " "
            
            if not main_content.strip():
                # Fallback to paragraphs
                paragraphs = soup.find_all('p')
                main_content = ' '.join([p.get_text() for p in paragraphs])
            
            return {
                'url': url,
                'title': title_text,
                'content': text_content[:5000],  # Limit content length
                'main_content': main_content[:3000],
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            return {
                'url': url,
                'title': 'Error',
                'content': '',
                'main_content': '',
                'success': False,
                'error': str(e)
            }

class OllamaQuizGenerator:
    def __init__(self):
        # Use only llama3:latest for best performance
        self.model_name = "llama3:latest"  # Best model for quiz generation
        
        # Performance optimizations
        self.max_content_length = 6000  # Optimized for faster processing
        self.timeout = 30  # 30 second timeout
        self.batch_size = 3  # Process questions in smaller batches for better reliability
        
        self.web_scraper = WebScraper()
        
        # Fallback questions for when llama3:latest is not available
        self.fallback_questions = {
            'react': [
                {
                    'type': 'mcq',
                    'question': 'What is React primarily used for?',
                    'options': ['Backend development', 'Building user interfaces', 'Database management', 'Server configuration'],
                    'correct_answer': 'B',
                    'explanation': 'React is a JavaScript library for building user interfaces, particularly single-page applications.'
                },
                {
                    'type': 'mcq',
                    'question': 'Which hook is used to manage state in functional components?',
                    'options': ['useState', 'useEffect', 'useContext', 'useReducer'],
                    'correct_answer': 'A',
                    'explanation': 'useState is the primary hook for managing state in functional components.'
                },
                {
                    'type': 'fill_blank',
                    'question': 'React components must start with a _____ letter.',
                    'correct_answer': 'capital',
                    'explanation': 'React components must start with a capital letter to distinguish them from regular HTML elements.'
                },
                {
                    'type': 'true_false',
                    'question': 'React is a framework, not a library.',
                    'correct_answer': 'False',
                    'explanation': 'React is a library, not a framework. It focuses on the view layer and can be used with other libraries.'
                }
            ],
            'python': [
                {
                    'type': 'mcq',
                    'question': 'What is the correct way to create a function in Python?',
                    'options': ['function myFunc():', 'def myFunc():', 'create myFunc():', 'func myFunc():'],
                    'correct_answer': 'B',
                    'explanation': 'In Python, functions are defined using the def keyword.'
                },
                {
                    'type': 'mcq',
                    'question': 'Which data structure is mutable in Python?',
                    'options': ['tuple', 'list', 'string', 'frozenset'],
                    'correct_answer': 'B',
                    'explanation': 'Lists are mutable in Python, meaning they can be modified after creation.'
                },
                {
                    'type': 'fill_blank',
                    'question': 'Python uses _____ for indentation.',
                    'correct_answer': 'spaces',
                    'explanation': 'Python uses spaces (typically 4) for indentation to define code blocks.'
                },
                {
                    'type': 'true_false',
                    'question': 'Python is a compiled language.',
                    'correct_answer': 'False',
                    'explanation': 'Python is an interpreted language, not compiled.'
                }
            ],
            'javascript': [
                {
                    'type': 'mcq',
                    'question': 'What is the correct way to declare a variable in JavaScript?',
                    'options': ['var x = 5;', 'let x = 5;', 'const x = 5;', 'All of the above'],
                    'correct_answer': 'D',
                    'explanation': 'All three are valid ways to declare variables in JavaScript, each with different scoping rules.'
                },
                {
                    'type': 'mcq',
                    'question': 'Which method is used to add elements to the end of an array?',
                    'options': ['push()', 'pop()', 'shift()', 'unshift()'],
                    'correct_answer': 'A',
                    'explanation': 'push() adds elements to the end of an array.'
                },
                {
                    'type': 'fill_blank',
                    'question': 'JavaScript is a _____-typed language.',
                    'correct_answer': 'dynamically',
                    'explanation': 'JavaScript is dynamically typed, meaning variable types are determined at runtime.'
                },
                {
                    'type': 'true_false',
                    'question': 'JavaScript and Java are the same language.',
                    'correct_answer': 'False',
                    'explanation': 'JavaScript and Java are completely different languages with different syntax and use cases.'
                }
            ],
            'dbms': [
                {
                    'type': 'mcq',
                    'question': 'What does DBMS stand for?',
                    'options': ['Database Management System', 'Data Base Management System', 'Database Model System', 'Data Business Management System'],
                    'correct_answer': 'A',
                    'explanation': 'DBMS stands for Database Management System, which is software for managing databases.'
                },
                {
                    'type': 'mcq',
                    'question': 'Which SQL command is used to retrieve data from a database?',
                    'options': ['SELECT', 'GET', 'RETRIEVE', 'FETCH'],
                    'correct_answer': 'A',
                    'explanation': 'The SELECT command is used to retrieve data from database tables.'
                },
                {
                    'type': 'fill_blank',
                    'question': 'A _____ is a collection of related data organized in tables.',
                    'correct_answer': 'database',
                    'explanation': 'A database is a structured collection of data organized in tables with relationships.'
                },
                {
                    'type': 'true_false',
                    'question': 'SQL is a programming language.',
                    'correct_answer': 'False',
                    'explanation': 'SQL is a query language, not a programming language. It is used for managing and manipulating databases.'
                }
            ],
            'database': [
                {
                    'type': 'mcq',
                    'question': 'What is the primary purpose of a database?',
                    'options': ['To store and organize data', 'To create websites', 'To run applications', 'To connect to the internet'],
                    'correct_answer': 'A',
                    'explanation': 'The primary purpose of a database is to store, organize, and manage data efficiently.'
                },
                {
                    'type': 'mcq',
                    'question': 'Which database model organizes data in tables with relationships?',
                    'options': ['Relational', 'Hierarchical', 'Network', 'Object-oriented'],
                    'correct_answer': 'A',
                    'explanation': 'The relational database model organizes data in tables with relationships between them.'
                },
                {
                    'type': 'fill_blank',
                    'question': 'A _____ is a structured way to store and retrieve data.',
                    'correct_answer': 'database',
                    'explanation': 'A database provides a structured way to store, organize, and retrieve data efficiently.'
                },
                {
                    'type': 'true_false',
                    'question': 'All databases use SQL.',
                    'correct_answer': 'False',
                    'explanation': 'Not all databases use SQL. NoSQL databases like MongoDB use different query languages.'
                }
            ]
        }
        
        # Initialize Ollama connection - only use llama3:latest
        try:
            models = ollama.list()
            available_models = [model.get('name') for model in models.get('models', [])]
            
            if self.model_name in available_models:
                logger.info(f"✅ Using llama3:latest for quiz generation")
                self.ollama_available = True
            else:
                logger.warning(f"❌ llama3:latest not found. Available models: {available_models}")
                logger.warning("⚠️ Quiz generation will use fallback questions only")
                self.ollama_available = False
                
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {str(e)}")
            self.ollama_available = False

    def read_file_content(self, filepath: str) -> str:
        """Read content from different file types."""
        try:
            ext = os.path.splitext(filepath)[1].lower()
            
            if ext == '.txt':
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif ext == '.pdf':
                text = ""
                with open(filepath, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                content = text
            elif ext == '.docx':
                doc = Document(filepath)
                content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            else:
                raise ValueError(f"Unsupported file type: {ext}")
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error reading file {filepath}: {str(e)}")
            raise

    def generate_questions_with_ollama(self, content: str, topic: str, num_questions: int, question_types: List[str]) -> List[Dict[str, Any]]:
        """Generate questions using Ollama AI with optimized performance."""
        try:
            if not self.ollama_available:
                logger.warning(f"❌ llama3:latest not available, using fallback questions for topic: {topic}")
                return self.get_fallback_questions(topic, num_questions, question_types)
            
            logger.info(f"🚀 Generating {num_questions} questions for topic: {topic} using llama3:latest")
            logger.info(f"📝 Content preview: {content[:200]}...")
            
            # Optimize content length for faster processing
            optimized_content = content[:self.max_content_length]
            
            # Create enhanced prompt for question generation with stronger content focus
            prompt = f"""You are a quiz generator. Create exactly {num_questions} quiz questions based EXCLUSIVELY on the following content. 

CRITICAL: You MUST use ONLY the information provided in the content below. Do NOT use any external knowledge.

CONTENT:
{optimized_content}

REQUIREMENTS:
- Generate exactly {num_questions} questions
- Use these question types: {', '.join(question_types)}
- EVERY question MUST be based ONLY on the specific content above
- Questions should test understanding of facts, names, dates, and concepts mentioned in the content
- For MCQ: provide 4 options (A, B, C, D) with one correct answer
- For fill-in-the-blank: use _____ to indicate the blank
- For true/false: provide True or False as correct answer
- Include explanations that reference specific details from the content

Format as JSON array:
[
    {{
        "type": "mcq|fill_blank|true_false",
        "question": "Question text here",
        "options": ["option1", "option2", "option3", "option4"],  // only for MCQ
        "correct_answer": "A|B|C|D or text answer or True|False",
        "explanation": "Explanation referencing specific content"
    }}
]

Return ONLY the JSON array, no additional text."""

            logger.info(f"📤 Sending prompt to llama3:latest for topic: {topic}")
            logger.info(f"📊 Content length: {len(optimized_content)} characters")
            
            # Generate questions using Ollama with optimized timeout
            response = ollama.chat(
                model=self.model_name, 
                messages=[{'role': 'user', 'content': prompt}],
                options={'timeout': self.timeout}
            )
            
            # Parse the response
            response_text = response['message']['content']
            logger.info(f"📥 Received response from llama3:latest for topic: {topic}")
            
            # Try to extract JSON from the response
            try:
                # Find JSON array in the response
                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                
                if json_start != -1 and json_end != 0:
                    json_str = response_text[json_start:json_end]
                    logger.info(f"✅ Extracted JSON from llama3:latest response for topic: {topic}")
                    
                    questions = json.loads(json_str)  # Using json.loads for safety
                    
                    # Validate and clean questions - be more lenient with content relevance
                    validated_questions = []
                    for q in questions:
                        if self.validate_question(q):
                            # Check if question is content-relevant (be more lenient)
                            if self.is_question_content_relevant(q, content):
                                validated_questions.append(q)
                            else:
                                logger.warning(f"⚠️ Question not content-relevant, but keeping it: {q.get('question', '')[:100]}...")
                                validated_questions.append(q)  # Keep the question anyway
                        else:
                            logger.warning(f"❌ Question rejected - validation failed: {q.get('question', '')[:100]}...")
                    
                    logger.info(f"✅ Validated {len(validated_questions)} questions for topic: {topic}")
                    
                    if len(validated_questions) >= num_questions:
                        logger.info(f"🎉 Successfully generated {len(validated_questions)} questions for topic: {topic}")
                        return validated_questions[:num_questions]
                    else:
                        logger.warning(f"⚠️ Generated only {len(validated_questions)} questions for topic: {topic}, using fallback")
                        return self.get_fallback_questions(topic, num_questions, question_types)
                else:
                    logger.warning(f"❌ No valid JSON found in llama3:latest response for topic: {topic}, using fallback")
                    logger.debug(f"Response text: {response_text[:500]}...")
                    return self.get_fallback_questions(topic, num_questions, question_types)
                    
            except Exception as e:
                logger.error(f"❌ Error parsing llama3:latest response for topic {topic}: {str(e)}")
                logger.debug(f"Response text: {response_text[:500]}...")
                return self.get_fallback_questions(topic, num_questions, question_types)
                
        except Exception as e:
            logger.error(f"❌ Error generating questions with llama3:latest for topic {topic}: {str(e)}")
            return self.get_fallback_questions(topic, num_questions, question_types)

    def validate_question(self, question: Dict[str, Any]) -> bool:
        """Validate a generated question."""
        try:
            required_fields = ['type', 'question', 'correct_answer', 'explanation']
            
            # Check required fields
            for field in required_fields:
                if field not in question or not question[field]:
                    return False
            
            # Check question type
            if question['type'] not in ['mcq', 'fill_blank', 'true_false']:
                return False
            
            # Check MCQ specific requirements
            if question['type'] == 'mcq':
                if 'options' not in question or len(question['options']) != 4:
                    return False
                if question['correct_answer'] not in ['A', 'B', 'C', 'D']:
                    return False
            
            # Check fill_blank specific requirements
            elif question['type'] == 'fill_blank':
                if '_____' not in question['question']:
                    return False
            
            # Check true_false specific requirements
            elif question['type'] == 'true_false':
                if question['correct_answer'] not in ['True', 'False']:
                    return False
            
            return True
            
        except Exception:
            return False

    def is_question_content_relevant(self, question: Dict[str, Any], original_content: str) -> bool:
        """Check if a question is relevant to the provided content (more lenient version)."""
        try:
            if not question or not original_content:
                return True  # Be more lenient
            
            question_text = question.get('question', '').lower()
            explanation = question.get('explanation', '').lower()
            
            # Get key terms from the content (first 1000 characters for speed)
            content_sample = original_content[:1000].lower()
            
            # Extract key terms from content (simple approach)
            content_words = set(re.findall(r'\b\w{4,}\b', content_sample))  # Words with 4+ characters
            
            # Check if question contains any key terms from content
            question_words = set(re.findall(r'\b\w{4,}\b', question_text))
            explanation_words = set(re.findall(r'\b\w{4,}\b', explanation))
            
            # Check for overlap
            content_overlap = question_words.intersection(content_words)
            explanation_overlap = explanation_words.intersection(content_words)
            
            # Be more lenient - if there's any overlap or if it's a general question, accept it
            if content_overlap or explanation_overlap:
                return True
            
            # If no overlap but it's a reasonable question, still accept it
            if len(question_text) > 20:  # Reasonable question length
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking content relevance: {str(e)}")
            return True  # Be lenient on errors

    def get_fallback_questions(self, topic: str, num_questions: int, question_types: List[str]) -> List[Dict[str, Any]]:
        """Get fallback questions when Ollama is not available."""
        # Determine the best fallback topic based on the input topic
        topic_lower = topic.lower()
        
        # Check for exact matches first
        if topic_lower in self.fallback_questions:
            fallback_topic = topic_lower
        # Check for partial matches
        elif any(word in topic_lower for word in ['database', 'dbms', 'sql', 'mysql', 'oracle', 'postgres']):
            fallback_topic = 'dbms'
        elif any(word in topic_lower for word in ['programming', 'coding', 'development', 'software']):
            fallback_topic = 'general_programming'
        elif any(word in topic_lower for word in ['web', 'internet', 'browser']):
            fallback_topic = 'web_development'
        elif any(word in topic_lower for word in ['mobile', 'app', 'ios', 'android']):
            fallback_topic = 'mobile_development'
        elif any(word in topic_lower for word in ['game', 'gaming', 'unity', 'unreal']):
            fallback_topic = 'game_development'
        elif any(word in topic_lower for word in ['math', 'mathematics', 'algebra', 'calculus']):
            fallback_topic = 'mathematics'
        elif any(word in topic_lower for word in ['science', 'physics', 'chemistry', 'biology']):
            fallback_topic = 'science'
        elif any(word in topic_lower for word in ['history', 'historical', 'ancient']):
            fallback_topic = 'history'
        elif any(word in topic_lower for word in ['geography', 'country', 'world']):
            fallback_topic = 'geography'
        elif any(word in topic_lower for word in ['literature', 'book', 'novel', 'poetry']):
            fallback_topic = 'literature'
        else:
            fallback_topic = 'general_knowledge'
        
        # Get questions for the matched topic
        questions = self.fallback_questions.get(fallback_topic, [])
        
        # If no questions found for the specific topic, try to generate some based on the topic
        if not questions:
            questions = self.generate_topic_specific_questions(topic, fallback_topic)
        
        # Filter by question types
        filtered_questions = [q for q in questions if q['type'] in question_types]
        if not filtered_questions:
            filtered_questions = questions
        
        # Return random selection
        return random.sample(filtered_questions, min(num_questions, len(filtered_questions)))

    def generate_topic_specific_questions(self, topic: str, fallback_topic: str) -> List[Dict[str, Any]]:
        """Generate topic-specific questions when no fallback questions are available."""
        topic_lower = topic.lower()
        
        # Generate questions based on the topic category
        if fallback_topic == 'general_programming':
            return [
                {
                    'type': 'mcq',
                    'question': f'What is the primary purpose of {topic} in software development?',
                    'options': ['To make code more complex', 'To solve specific problems efficiently', 'To slow down development', 'To create bugs'],
                    'correct_answer': 'B',
                    'explanation': f'{topic} is designed to solve specific problems efficiently in software development.'
                },
                {
                    'type': 'fill_blank',
                    'question': f'{topic} is commonly used for _____ in modern development.',
                    'correct_answer': 'problem solving',
                    'explanation': f'{topic} is a tool or concept used for solving problems in modern software development.'
                },
                {
                    'type': 'true_false',
                    'question': f'{topic} is essential for building scalable applications.',
                    'correct_answer': 'True',
                    'explanation': f'{topic} provides important capabilities for building scalable and maintainable applications.'
                }
            ]
        elif fallback_topic == 'web_development':
            return [
                {
                    'type': 'mcq',
                    'question': f'How does {topic} contribute to web development?',
                    'options': ['By making websites slower', 'By improving user experience', 'By increasing server costs', 'By reducing functionality'],
                    'correct_answer': 'B',
                    'explanation': f'{topic} helps improve user experience and functionality in web development.'
                },
                {
                    'type': 'fill_blank',
                    'question': f'{topic} is important for creating _____ web applications.',
                    'correct_answer': 'responsive',
                    'explanation': f'{topic} helps create responsive and user-friendly web applications.'
                },
                {
                    'type': 'true_false',
                    'question': f'{topic} is only used for frontend development.',
                    'correct_answer': 'False',
                    'explanation': f'{topic} can be used in both frontend and backend development depending on the implementation.'
                }
            ]
        elif fallback_topic == 'general_knowledge':
            return [
                {
                    'type': 'mcq',
                    'question': f'What is {topic} primarily known for?',
                    'options': ['Being completely unknown', 'Having no practical applications', 'Being widely used and important', 'Being outdated'],
                    'correct_answer': 'C',
                    'explanation': f'{topic} is likely an important and widely used concept or technology.'
                },
                {
                    'type': 'fill_blank',
                    'question': f'{topic} is commonly used in _____ industries.',
                    'correct_answer': 'various',
                    'explanation': f'{topic} has applications across various industries and domains.'
                },
                {
                    'type': 'true_false',
                    'question': f'{topic} is a fundamental concept in its field.',
                    'correct_answer': 'True',
                    'explanation': f'{topic} represents a fundamental concept or technology in its respective field.'
                }
            ]
        else:
            # Default questions for any topic
            return [
                {
                    'type': 'mcq',
                    'question': f'Which of the following best describes {topic}?',
                    'options': ['A completely useless concept', 'An important technology or concept', 'Something that nobody uses', 'An outdated technology'],
                    'correct_answer': 'B',
                    'explanation': f'{topic} is an important technology or concept in its field.'
                },
                {
                    'type': 'fill_blank',
                    'question': f'{topic} is used for _____ purposes.',
                    'correct_answer': 'specific',
                    'explanation': f'{topic} serves specific purposes in its application domain.'
                },
                {
                    'type': 'true_false',
                    'question': f'{topic} has practical applications in modern technology.',
                    'correct_answer': 'True',
                    'explanation': f'{topic} has practical applications and is relevant in modern technology.'
                }
            ]

    def generate_quiz_from_topic(self, topic: str, num_questions: int = 5, question_types: List[str] = None) -> List[Dict[str, Any]]:
        """Generate quiz from a topic using Ollama with enhanced context."""
        if not question_types:
            question_types = ["mcq", "fill_blank", "true_false"]
        
        logger.info(f"🎯 Generating quiz for topic: {topic}")
        
        # Create a comprehensive prompt for topic-based generation
        topic_prompt = f"""You are a quiz generator. Create exactly {num_questions} quiz questions about the topic: {topic}

CRITICAL: Generate questions specifically about {topic}. Do NOT generate generic questions about other topics.

REQUIREMENTS:
- Generate exactly {num_questions} questions
- Use these question types: {', '.join(question_types)}
- EVERY question MUST be specifically about {topic}
- Questions should test understanding of {topic} concepts, facts, and applications
- For MCQ: provide 4 options (A, B, C, D) with one correct answer
- For fill-in-the-blank: use _____ to indicate the blank
- For true/false: provide True or False as correct answer
- Include detailed explanations that explain why the answer is correct

Format as JSON array:
[
    {{
        "type": "mcq|fill_blank|true_false",
        "question": "Question text here",
        "options": ["option1", "option2", "option3", "option4"],  // only for MCQ
        "correct_answer": "A|B|C|D or text answer or True|False",
        "explanation": "Detailed explanation about {topic}"
    }}
]

Return ONLY the JSON array, no additional text.

FOCUS: All questions must be about {topic} specifically."""

        try:
            # Generate questions using the topic-specific prompt
            response = ollama.chat(
                model=self.model_name, 
                messages=[{'role': 'user', 'content': topic_prompt}],
                options={'timeout': self.timeout}
            )
            
            response_text = response['message']['content']
            logger.info(f"📥 Received response from llama3:latest for topic: {topic}")
            
            # Try to extract JSON from the response
            try:
                # Find JSON array in the response
                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                
                if json_start != -1 and json_end != 0:
                    json_str = response_text[json_start:json_end]
                    logger.info(f"✅ Extracted JSON from llama3:latest response for topic: {topic}")
                    
                    questions = json.loads(json_str)
                    
                    # Validate questions
                    validated_questions = []
                    for q in questions:
                        if self.validate_question(q):
                            # Check if question is about the requested topic
                            if self.is_question_about_topic(q, topic):
                                validated_questions.append(q)
                            else:
                                logger.warning(f"⚠️ Question not about {topic}, but keeping it: {q.get('question', '')[:100]}...")
                                validated_questions.append(q)  # Keep the question anyway
                        else:
                            logger.warning(f"❌ Question rejected - validation failed: {q.get('question', '')[:100]}...")
                    
                    logger.info(f"✅ Validated {len(validated_questions)} questions for topic: {topic}")
                    
                    if len(validated_questions) >= num_questions:
                        logger.info(f"🎉 Successfully generated {len(validated_questions)} questions for topic: {topic}")
                        return validated_questions[:num_questions]
                    else:
                        logger.warning(f"⚠️ Generated only {len(validated_questions)} questions for topic: {topic}, using fallback")
                        return self.get_fallback_questions(topic, num_questions, question_types)
                else:
                    logger.warning(f"❌ No valid JSON found in llama3:latest response for topic: {topic}, using fallback")
                    return self.get_fallback_questions(topic, num_questions, question_types)
                    
            except Exception as e:
                logger.error(f"❌ Error parsing llama3:latest response for topic {topic}: {str(e)}")
                return self.get_fallback_questions(topic, num_questions, question_types)
                
        except Exception as e:
            logger.error(f"❌ Error generating questions with llama3:latest for topic {topic}: {str(e)}")
            return self.get_fallback_questions(topic, num_questions, question_types)

    def is_question_about_topic(self, question: Dict[str, Any], topic: str) -> bool:
        """Check if a question is about the specified topic."""
        try:
            if not question or not topic:
                return False
            
            question_text = question.get('question', '').lower()
            topic_lower = topic.lower()
            
            # Check if the question contains any keywords related to the topic
            keywords = re.findall(r'\b\w{4,}\b', question_text)
            for keyword in keywords:
                if keyword in topic_lower:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking question topic: {str(e)}")
            return False

    def generate_quiz_from_content(self, content: str, num_questions: int = 5, question_types: List[str] = None) -> List[Dict[str, Any]]:
        """Generate quiz from text content using Ollama."""
        if not question_types:
            question_types = ["mcq", "fill_blank", "true_false"]
        
        # Extract topic from content
        topic = self.extract_topic_from_content(content)
        
        return self.generate_questions_with_ollama(content, topic, num_questions, question_types)

    def generate_quiz_from_file(self, filepath: str, num_questions: int = 5, question_types: List[str] = None) -> List[Dict[str, Any]]:
        """Generate quiz from uploaded file using Ollama."""
        if not question_types:
            question_types = ["mcq", "fill_blank", "true_false"]
        
        try:
            # Read file content
            content = self.read_file_content(filepath)
            
            if not content:
                raise ValueError("No content could be extracted from the file")
            
            logger.info(f"📄 Extracted {len(content)} characters from file")
            logger.info(f"📝 Content preview: {content[:200]}...")
            
            # Extract topic from content
            topic = self.extract_topic_from_content(content)
            logger.info(f"🎯 Extracted topic: {topic}")
            
            # Use the improved question generation method
            return self.generate_questions_with_ollama(content, topic, num_questions, question_types)
            
        except Exception as e:
            logger.error(f"Error generating quiz from file: {str(e)}")
            return self.get_fallback_questions("general", num_questions, question_types)

    def generate_quiz_from_url(self, url: str, num_questions: int = 5, question_types: List[str] = None) -> List[Dict[str, Any]]:
        """Generate quiz from web URL using web scraping and Ollama."""
        if not question_types:
            question_types = ["mcq", "fill_blank", "true_false"]
        
        try:
            # Scrape content from URL
            scraped_data = self.web_scraper.scrape_url(url)
            
            if not scraped_data['success']:
                raise ValueError(f"Failed to scrape URL: {scraped_data.get('error', 'Unknown error')}")
            
            # Use main content if available, otherwise use full content
            content = scraped_data['main_content'] if scraped_data['main_content'] else scraped_data['content']
            
            if not content:
                raise ValueError("No content could be extracted from the URL")
            
            # Extract topic from content
            topic = self.extract_topic_from_content(content)
            
            return self.generate_questions_with_ollama(content, topic, num_questions, question_types)
            
        except Exception as e:
            logger.error(f"Error generating quiz from URL: {str(e)}")
            return self.get_fallback_questions("general", num_questions, question_types)

    def gather_topic_context(self, topic: str) -> str:
        """Gather additional context about a topic using web scraping."""
        try:
            # Search for relevant content about the topic
            search_urls = [
                f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
                f"https://www.w3schools.com/{topic.lower()}/",
                f"https://developer.mozilla.org/en-US/docs/Web/{topic.upper()}"
            ]
            
            context_parts = []
            
            # Try to get content from multiple sources
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                future_to_url = {executor.submit(self.web_scraper.scrape_url, url): url for url in search_urls}
                
                for future in concurrent.futures.as_completed(future_to_url, timeout=10):
                    try:
                        scraped_data = future.result()
                        if scraped_data['success'] and scraped_data['main_content']:
                            context_parts.append(scraped_data['main_content'][:1000])
                    except Exception as e:
                        logger.warning(f"Failed to gather context from URL: {str(e)}")
            
            if context_parts:
                return f"Additional context about {topic}: {' '.join(context_parts)}"
            else:
                return f"Generate questions about {topic}. This could be a programming language, technology, concept, or any educational topic."
                
        except Exception as e:
            logger.error(f"Error gathering topic context: {str(e)}")
            return f"Generate questions about {topic}. This could be a programming language, technology, concept, or any educational topic."

    def extract_topic_from_content(self, content: str) -> str:
        """Extract the main topic from content using keyword analysis and Ollama."""
        try:
            if not content:
                return 'General Knowledge'
            
            # First, try keyword-based extraction
            content_lower = content.lower()
            
            # Define topic keywords
            topic_keywords = {
                'geography': ['geography', 'geographic', 'earth', 'land', 'map', 'cartography', 'eratosthenes', 'ptolemy'],
                'python': ['python', 'programming', 'code', 'script', 'function', 'variable'],
                'javascript': ['javascript', 'js', 'web', 'browser', 'dom', 'react', 'node'],
                'react': ['react', 'jsx', 'component', 'hook', 'state', 'props'],
                'machine learning': ['machine learning', 'ml', 'ai', 'algorithm', 'model', 'training', 'neural'],
                'mathematics': ['math', 'mathematics', 'algebra', 'calculus', 'equation', 'formula'],
                'history': ['history', 'historical', 'ancient', 'civilization', 'war', 'empire'],
                'science': ['science', 'scientific', 'physics', 'chemistry', 'biology', 'experiment'],
                'literature': ['literature', 'book', 'novel', 'poetry', 'author', 'writing'],
                'technology': ['technology', 'tech', 'computer', 'software', 'hardware', 'digital'],
                'database': ['database', 'dbms', 'sql', 'mysql', 'postgresql', 'oracle', 'mongodb', 'table', 'query', 'schema', 'index', 'transaction', 'normalization', 'erd', 'entity', 'relationship'],
                'dbms': ['dbms', 'database management system', 'rdbms', 'relational database', 'sql server', 'mysql', 'postgresql', 'oracle', 'database design', 'data modeling'],
                'sql': ['sql', 'structured query language', 'select', 'insert', 'update', 'delete', 'join', 'where', 'group by', 'order by', 'database query'],
                'data structures': ['data structures', 'array', 'linked list', 'stack', 'queue', 'tree', 'graph', 'hash table', 'heap', 'binary tree'],
                'algorithms': ['algorithms', 'sorting', 'searching', 'recursion', 'dynamic programming', 'greedy', 'divide and conquer', 'complexity', 'big o'],
                'operating systems': ['operating system', 'os', 'linux', 'windows', 'unix', 'process', 'thread', 'memory management', 'file system', 'scheduling'],
                'networking': ['networking', 'network', 'tcp', 'ip', 'http', 'dns', 'router', 'switch', 'protocol', 'osi model', 'lan', 'wan'],
                'cybersecurity': ['cybersecurity', 'security', 'encryption', 'authentication', 'authorization', 'firewall', 'vulnerability', 'penetration testing', 'ethical hacking'],
                'web development': ['web development', 'html', 'css', 'javascript', 'php', 'asp.net', 'django', 'flask', 'frontend', 'backend', 'full stack'],
                'mobile development': ['mobile development', 'android', 'ios', 'react native', 'flutter', 'swift', 'kotlin', 'mobile app', 'smartphone'],
                'cloud computing': ['cloud computing', 'aws', 'azure', 'google cloud', 'saas', 'paas', 'iaas', 'virtualization', 'docker', 'kubernetes']
            }
            
            # Count keyword matches for each topic
            topic_scores = {}
            for topic, keywords in topic_keywords.items():
                score = sum(1 for keyword in keywords if keyword in content_lower)
                if score > 0:
                    topic_scores[topic] = score
            
            # If we found a clear topic, use it
            if topic_scores:
                best_topic = max(topic_scores, key=topic_scores.get)
                # Be more sensitive to database-related topics
                if best_topic in ['database', 'dbms', 'sql'] and topic_scores[best_topic] >= 1:
                    logger.info(f"📊 Extracted database topic '{best_topic}' from content using keyword analysis")
                    return best_topic.title()
                elif topic_scores[best_topic] >= 2:  # At least 2 keyword matches for other topics
                    logger.info(f"📊 Extracted topic '{best_topic}' from content using keyword analysis")
                    return best_topic.title()
            
            # If keyword analysis didn't work, use Ollama
            try:
                prompt = f"""Extract the main topic or subject from this content. Return only the topic name, nothing else.

Content: {content[:1000]}

Topic:"""
                
                response = ollama.chat(model=self.model_name, messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ])
                
                topic = response['message']['content'].strip()
                if topic and len(topic) < 50:  # Reasonable topic length
                    logger.info(f"🤖 Extracted topic '{topic}' from content using Ollama")
                    return topic
                else:
                    return 'General Knowledge'
                    
            except Exception as e:
                logger.error(f"Error extracting topic with llama3:latest: {str(e)}")
                return 'General Knowledge'
                
        except Exception as e:
            logger.error(f"Error in topic extraction: {str(e)}")
            return 'General Knowledge'

# Initialize quiz generator
quiz_generator = OllamaQuizGenerator()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "quiz-generator",
        "message": "Quiz Generator API is running",
        "model": "llama3:latest",
        "ollama_available": quiz_generator.ollama_available,
        "features": ["topic_generation", "text_generation", "file_generation", "url_generation", "web_scraping"],
        "optimizations": {
            "max_content_length": quiz_generator.max_content_length,
            "timeout": quiz_generator.timeout,
            "batch_size": quiz_generator.batch_size
        }
    })

@app.route('/api/generate', methods=['POST'])
def generate_quiz():
    """Generate quiz from topic or text content"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        source_type = data.get('type', 'topic')  # 'topic', 'text', or 'url'
        content = data.get('content', '')
        num_questions = data.get('num_questions', 5)
        question_types = data.get('question_types', ['mcq', 'fill_blank', 'true_false'])
        user_id = data.get('user_id', 'anonymous')  # Get user ID from request
        
        # Handle content validation properly
        if isinstance(content, dict):
            content = str(content)
        elif not isinstance(content, str):
            content = str(content)
        
        if not content.strip():
            return jsonify({"error": "Content is required"}), 400
        
        if source_type == 'topic':
            questions = quiz_generator.generate_quiz_from_topic(
                content, 
                num_questions, 
                question_types
            )
            # Add topic to history
            history_manager.add_topic_history(user_id, content, source_type)
        elif source_type == 'text':
            questions = quiz_generator.generate_quiz_from_content(
                content, 
                num_questions, 
                question_types
            )
            # Extract topic from content for history
            topic = quiz_generator.extract_topic_from_content(content)
            history_manager.add_topic_history(user_id, topic, source_type)
        elif source_type == 'url':
            questions = quiz_generator.generate_quiz_from_url(
                content, 
                num_questions, 
                question_types
            )
            # Add URL topic to history
            history_manager.add_topic_history(user_id, f"URL: {content}", source_type)
        else:
            return jsonify({"error": "Invalid source type. Use 'topic', 'text', or 'url'"}), 400
        
        response_data = {
            "success": True,
            "questions": questions,
            "total_questions": len(questions),
            "source_type": source_type,
            "ollama_used": quiz_generator.ollama_available,
            "topic": content if source_type == 'topic' else quiz_generator.extract_topic_from_content(content)
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        return jsonify({"error": f"Failed to generate quiz: {str(e)}"}), 500

@app.route('/api/generate/file', methods=['POST'])
def generate_quiz_from_file():
    """Generate quiz from uploaded file"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed. Supported types: txt, pdf, docx"}), 400
        
        # Get additional parameters
        num_questions = int(request.form.get('num_questions', 5))
        question_types = request.form.get('question_types', 'mcq,fill_blank,true_false').split(',')
        user_id = request.form.get('user_id', 'anonymous')  # Get user ID from form
        
        logger.info(f"📁 Processing file: {file.filename}")
        logger.info(f"📊 Parameters: {num_questions} questions, types: {question_types}")
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Generate quiz from file content using Ollama
            questions = quiz_generator.generate_quiz_from_file(
                filepath, 
                num_questions, 
                question_types
            )
            
            # Extract topic from file content for history
            content = quiz_generator.read_file_content(filepath)
            topic = quiz_generator.extract_topic_from_content(content)
            history_manager.add_topic_history(user_id, topic, 'file')
            
            logger.info(f"✅ Successfully generated {len(questions)} questions from file")
            
            response_data = {
                "success": True,
                "questions": questions,
                "total_questions": len(questions),
                "source_type": "file",
                "filename": filename,
                "ollama_used": quiz_generator.ollama_available,
                "topic": topic
            }
            
            return jsonify(response_data)
            
        finally:
            # Clean up temporary file
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"🗑️ Cleaned up temporary file: {filepath}")
        
    except Exception as e:
        logger.error(f"Error generating quiz from file: {str(e)}")
        return jsonify({"error": f"Failed to generate quiz from file: {str(e)}"}), 500

@app.route('/api/generate/<topic>', methods=['GET'])
def generate_quiz_from_topic_get(topic):
    """Generate quiz from topic via GET request"""
    try:
        num_questions = int(request.args.get('num_questions', 5))
        question_types = request.args.get('question_types', 'mcq,fill_blank,true_false').split(',')
        user_id = request.args.get('user_id', 'anonymous')  # Get user ID from query params
        
        questions = quiz_generator.generate_quiz_from_topic(
            topic, 
            num_questions, 
            question_types
        )
        
        # Add topic to history
        history_manager.add_topic_history(user_id, topic, 'topic')
        
        response_data = {
            "success": True,
            "questions": questions,
            "total_questions": len(questions),
            "source_type": "topic",
            "topic": topic,
            "ollama_used": quiz_generator.ollama_available
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error generating quiz from topic: {str(e)}")
        return jsonify({"error": f"Failed to generate quiz: {str(e)}"}), 500

@app.route('/api/scrape-url', methods=['POST'])
def scrape_url():
    """Scrape content from a URL"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({"error": "URL is required"}), 400
        
        url = data['url']
        scraped_data = quiz_generator.web_scraper.scrape_url(url)
        
        return jsonify(scraped_data)
        
    except Exception as e:
        logger.error(f"Error scraping URL: {str(e)}")
        return jsonify({"error": f"Failed to scrape URL: {str(e)}"}), 500

@app.route('/api/validate', methods=['POST'])
def validate_quiz():
    """Validate quiz answers and return results"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        questions = data.get('questions', [])
        answers = data.get('answers', [])
        user_id = data.get('user_id', 'anonymous')  # Get user ID from request
        topic = data.get('topic', 'Unknown')
        source_type = data.get('source_type', 'topic')
        
        if len(questions) != len(answers):
            return jsonify({"error": "Number of questions and answers don't match"}), 400
        
        results = []
        correct_count = 0
        
        for i, (question, answer) in enumerate(zip(questions, answers)):
            is_correct = False
            
            if question['type'] == 'mcq':
                correct_answer = question['correct_answer']
                is_correct = answer == correct_answer
            elif question['type'] == 'fill_blank':
                correct_answer = question['correct_answer'].lower().strip()
                user_answer = answer.lower().strip()
                is_correct = user_answer == correct_answer
            elif question['type'] == 'true_false':
                correct_answer = question['correct_answer']
                is_correct = answer == correct_answer
            
            if is_correct:
                correct_count += 1
            
            results.append({
                "question_index": i,
                "is_correct": is_correct,
                "user_answer": answer,
                "correct_answer": question['correct_answer'],
                "explanation": question.get('explanation', '')
            })
        
        score_percentage = (correct_count / len(questions)) * 100 if questions else 0
        
        response_data = {
            "success": True,
            "results": results,
            "score": correct_count,
            "total_questions": len(questions),
            "score_percentage": round(score_percentage, 2)
        }
        
        # Save quiz to history
        quiz_data = {
            'topic': topic,
            'source_type': source_type,
            'num_questions': len(questions),
            'score': correct_count,
            'total_questions': len(questions),
            'score_percentage': round(score_percentage, 2),
            'ollama_used': data.get('ollama_used', False),
            'questions': questions,
            'results': results,
            'input_content': data.get('input_content', ''),
            'filename': data.get('filename', ''),
            'url': data.get('url', '')
        }
        history_manager.add_quiz_history(user_id, quiz_data)
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error validating quiz: {str(e)}")
        return jsonify({"error": f"Failed to validate quiz: {str(e)}"}), 500

@app.route('/api/supported-types', methods=['GET'])
def get_supported_types():
    """Get supported file types and question types"""
    return jsonify({
        "supported_file_types": list(ALLOWED_EXTENSIONS),
        "supported_question_types": ["mcq", "fill_blank", "true_false"],
        "supported_source_types": ["topic", "text", "file", "url"],
        "max_file_size_mb": app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024),
        "ollama_available": quiz_generator.ollama_available
    })

@app.route('/api/history/<user_id>', methods=['GET'])
def get_user_history(user_id):
    """Get user history including quizzes, chats, and topics"""
    try:
        user_history = history_manager.get_user_history(user_id)
        
        # Convert sets to lists for JSON serialization
        for topic in user_history.get('topics', []):
            if 'source_types' in topic:
                topic['source_types'] = list(topic['source_types'])
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "history": user_history
        })
        
    except Exception as e:
        logger.error(f"Error getting user history: {str(e)}")
        return jsonify({"error": f"Failed to get user history: {str(e)}"}), 500

@app.route('/api/history/<user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    """Get user statistics and summary"""
    try:
        stats = history_manager.get_user_stats(user_id)
        
        # Convert sets to lists for JSON serialization
        for topic in stats.get('top_topics', []):
            if 'source_types' in topic:
                topic['source_types'] = list(topic['source_types'])
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "stats": stats
        })
        
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        return jsonify({"error": f"Failed to get user stats: {str(e)}"}), 500

@app.route('/api/history/<user_id>/quizzes', methods=['GET'])
def get_user_quiz_history(user_id):
    """Get user quiz history"""
    try:
        user_history = history_manager.get_user_history(user_id)
        quizzes = user_history.get('quizzes', [])
        
        # Sort by timestamp (most recent first)
        quizzes = sorted(quizzes, key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "quizzes": quizzes,
            "total_quizzes": len(quizzes)
        })
        
    except Exception as e:
        logger.error(f"Error getting user quiz history: {str(e)}")
        return jsonify({"error": f"Failed to get user quiz history: {str(e)}"}), 500

@app.route('/api/history/<user_id>/topics', methods=['GET'])
def get_user_topic_history(user_id):
    """Get user topic history"""
    try:
        user_history = history_manager.get_user_history(user_id)
        topics = user_history.get('topics', [])
        
        # Convert sets to lists for JSON serialization
        for topic in topics:
            if 'source_types' in topic:
                topic['source_types'] = list(topic['source_types'])
        
        # Sort by count (most used first)
        topics = sorted(topics, key=lambda x: x['count'], reverse=True)
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "topics": topics,
            "total_topics": len(topics)
        })
        
    except Exception as e:
        logger.error(f"Error getting user topic history: {str(e)}")
        return jsonify({"error": f"Failed to get user topic history: {str(e)}"}), 500

@app.route('/api/history/<user_id>/clear', methods=['DELETE'])
def clear_user_history(user_id):
    """Clear user history"""
    try:
        history_type = request.args.get('type', 'all')  # all, quizzes, chats, topics
        
        if history_type not in ['all', 'quizzes', 'chats', 'topics']:
            return jsonify({"error": "Invalid history type. Use 'all', 'quizzes', 'chats', or 'topics'"}), 400
        
        history_manager.clear_user_history(user_id, history_type)
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "message": f"Cleared {history_type} history successfully"
        })
        
    except Exception as e:
        logger.error(f"Error clearing user history: {str(e)}")
        return jsonify({"error": f"Failed to clear user history: {str(e)}"}), 500

@app.route('/api/history/<user_id>/quiz/<quiz_id>', methods=['GET'])
def get_quiz_details(user_id, quiz_id):
    """Get detailed information about a specific quiz"""
    try:
        user_history = history_manager.get_user_history(user_id)
        quizzes = user_history.get('quizzes', [])
        
        # Find the specific quiz
        quiz = next((q for q in quizzes if q['id'] == quiz_id), None)
        
        if not quiz:
            return jsonify({"error": "Quiz not found"}), 404
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "quiz": quiz
        })
        
    except Exception as e:
        logger.error(f"Error getting quiz details: {str(e)}")
        return jsonify({"error": f"Failed to get quiz details: {str(e)}"}), 500

@app.route('/api/chat', methods=['POST'])
def add_chat_history():
    """Add chat interaction to user history"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        user_id = data.get('user_id', 'anonymous')
        message = data.get('message', '')
        response = data.get('response', '')
        topic = data.get('topic', '')
        chat_type = data.get('type', 'general')
        
        if not message or not response:
            return jsonify({"error": "Message and response are required"}), 400
        
        chat_data = {
            'message': message,
            'response': response,
            'topic': topic,
            'type': chat_type
        }
        
        history_manager.add_chat_history(user_id, chat_data)
        
        return jsonify({
            "success": True,
            "message": "Chat history added successfully"
        })
        
    except Exception as e:
        logger.error(f"Error adding chat history: {str(e)}")
        return jsonify({"error": f"Failed to add chat history: {str(e)}"}), 500

@app.route('/api/history/<user_id>/chats', methods=['GET'])
def get_user_chat_history(user_id):
    """Get user chat history"""
    try:
        user_history = history_manager.get_user_history(user_id)
        chats = user_history.get('chats', [])
        
        # Sort by timestamp (most recent first)
        chats = sorted(chats, key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "chats": chats,
            "total_chats": len(chats)
        })
        
    except Exception as e:
        logger.error(f"Error getting user chat history: {str(e)}")
        return jsonify({"error": f"Failed to get user chat history: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004) 