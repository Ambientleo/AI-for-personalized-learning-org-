import os
import re
import json
import logging
import requests
import time
import concurrent.futures
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from dotenv import load_dotenv
import ollama
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("chatbot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Model configuration with fallback chain
PRIMARY_MODEL = "llama3:latest"  # Best performance and quality
FALLBACK_MODELS = ["mistral:instruct", "mistral:latest"]
MODEL_NAME = PRIMARY_MODEL

# Performance optimizations
MAX_CONTENT_LENGTH = 6000  # Optimized for faster processing
TIMEOUT = 30  # 30 second timeout

# Constants
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY", "")
SEARCH_API_URL = os.getenv("SEARCH_API_URL", "https://serpapi.com/search")
MAX_SOURCES = 3
SCRAPE_TIMEOUT = 10  # seconds

# Cache for recent queries to reduce repeated scraping
query_cache = {}
CACHE_EXPIRY = 3600  # 1 hour in seconds


class TeacherChatbot:
    def __init__(self):
        self.logger = logger
        self.initialize_model()
        
    def initialize_model(self):
        """Initialize the LLaMA model through Ollama."""
        try:
            # Check if model exists in Ollama
            models = ollama.list()
            model_exists = any(model.get('name') == MODEL_NAME for model in models.get('models', []))
            
            if not model_exists:
                self.logger.info(f"Model {MODEL_NAME} not found. Make sure it's available in Ollama.")
            else:
                self.logger.info(f"Successfully connected to Ollama with model {MODEL_NAME}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Ollama model: {str(e)}")
            raise

    def search_web(self, query):
        """Search the web for educational content related to the query."""
        if not SEARCH_API_KEY:
            self.logger.warning("Search API key not available, using direct scraping")
            return self._get_default_educational_urls(query)
            
        try:
            params = {
                "q": query + " educational content",
                "api_key": SEARCH_API_KEY,
                "engine": "google",
                "num": 5
            }
            response = requests.get(SEARCH_API_URL, params=params)
            data = response.json()
            
            # Extract relevant URLs, prioritizing educational sites
            urls = []
            if "organic_results" in data:
                for result in data["organic_results"]:
                    url = result.get("link")
                    if url and self._is_educational_site(url):
                        urls.append(url)
                        if len(urls) >= MAX_SOURCES:
                            break
            
            return urls
        except Exception as e:
            self.logger.error(f"Error in web search: {str(e)}")
            return self._get_default_educational_urls(query)

    def _get_default_educational_urls(self, query):
        """Get default educational URLs when search API is not available."""
        query_formatted = query.replace(" ", "_")
        urls = [
            f"https://en.wikipedia.org/wiki/{query_formatted}",
            f"https://simple.wikipedia.org/wiki/{query_formatted}"
        ]
        return urls

    def _is_educational_site(self, url):
        """Check if the URL is from an educational website."""
        educational_domains = [
            'wikipedia.org', 'khanacademy.org', 'britannica.com', 
            'edu', 'coursera.org', 'edx.org', 'mit.edu', 
            'stanford.edu', 'harvard.edu', 'scholarpedia.org'
        ]
        
        try:
            domain = urlparse(url).netloc
            return any(edu_domain in domain for edu_domain in educational_domains)
        except:
            return False

    def scrape_content(self, url):
        """Scrape educational content from a URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=SCRAPE_TIMEOUT)
            
            # Check if the page exists and is accessible
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script, style, and navigation elements
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Extract title
            title = soup.title.string if soup.title else ""
            
            # Try to get content based on website-specific selectors
            domain = urlparse(url).netloc
            content = ""
            
            # Special handling for Wikipedia
            if 'wikipedia.org' in domain:
                main_content = soup.find('div', {'id': 'mw-content-text'})
                if main_content:
                    paragraphs = main_content.find_all('p')
                    content = ' '.join([p.get_text().strip() for p in paragraphs])
            else:
                # Get main content based on common article containers
                main_elements = soup.find_all(
                    ['article', 'main', 'div'], 
                    class_=re.compile(r'content|article|main|body')
                )
                
                if main_elements:
                    # Use the largest content block
                    main_element = max(main_elements, key=lambda x: len(x.get_text()))
                    paragraphs = main_element.find_all('p')
                    content = ' '.join([p.get_text().strip() for p in paragraphs])
                else:
                    # Fallback to all paragraphs
                    paragraphs = soup.find_all('p')
                    content = ' '.join([p.get_text().strip() for p in paragraphs])
            
            # Clean the content
            content = re.sub(r'\s+', ' ', content).strip()
            content = re.sub(r'\[\d+\]', '', content)  # Remove reference numbers like [1], [2], etc.
            
            # Trim to max length
            if len(content) > MAX_CONTENT_LENGTH:
                content = content[:MAX_CONTENT_LENGTH] + "..."
                
            return {
                "title": title,
                "content": content,
                "url": url
            }
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {str(e)}")
            return None

    def scrape_multiple_sources(self, urls):
        """Scrape content from multiple URLs in parallel."""
        sources = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_SOURCES) as executor:
            future_to_url = {executor.submit(self.scrape_content, url): url for url in urls}
            for future in concurrent.futures.as_completed(future_to_url):
                result = future.result()
                if result and result["content"]:
                    sources.append(result)
        
        return sources

    def generate_response(self, query, context=None):
        """Generate a response using the LLaMA model via Ollama."""
        try:
            if context:
                prompt = f"""You are an educational assistant helping with a student query.
                
Context information:
{context}

Based on the above context and your knowledge, please answer the following student question in a helpful, educational manner:
{query}

Explain the concepts clearly and in simple terms. If you're unsure, acknowledge this and provide your best educational guidance."""
            else:
                prompt = f"""You are an educational assistant helping with a student query.
                
Please answer the following student question in a helpful, educational manner:
{query}

Explain the concepts clearly and in simple terms. If you're unsure, acknowledge this and provide your best educational guidance."""

            # Generate response using Ollama
            response = ollama.chat(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful educational assistant that explains concepts clearly and accurately. Always provide accurate information and explain concepts in a way that's easy to understand."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 1024
                }
            )
            
            return response['message']['content']
        
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return "I'm having trouble generating a response right now. Please try again later."

    def answer_query(self, query):
        """Main method to answer educational queries."""
        # Check cache first
        cache_key = query.lower().strip()
        current_time = time.time()
        
        if cache_key in query_cache and current_time - query_cache[cache_key]["timestamp"] < CACHE_EXPIRY:
            self.logger.info(f"Returning cached response for: {query}")
            return query_cache[cache_key]["response"]
        
        try:
            # Log the query
            self.logger.info(f"Received query: {query}")
            
            # Try to get web content first
            urls = self.search_web(query)
            
            if urls:
                # Scrape content from the URLs
                sources = self.scrape_multiple_sources(urls)
                
                if sources:
                    # Prepare context from scraped content
                    context = "\n\n".join([
                        f"Source: {source['title']} ({source['url']})\n{source['content']}"
                        for source in sources
                    ])
                    
                    # Generate response with context
                    response = self.generate_response(query, context)
                    
                    # Add sources to the response
                    source_urls = [f"- {source['title']}: {source['url']}" for source in sources]
                    response += "\n\nSources:\n" + "\n".join(source_urls)
                else:
                    # No useful content scraped, fall back to model
                    response = self.generate_response(query)
            else:
                # No URLs found, fall back to model
                response = self.generate_response(query)
            
            # Cache the response
            query_cache[cache_key] = {
                "response": response,
                "timestamp": current_time
            }
            
            # If cache is too large, remove oldest entries
            if len(query_cache) > 100:
                oldest_key = min(query_cache.keys(), key=lambda k: query_cache[k]["timestamp"])
                del query_cache[oldest_key]
                
            return response
            
        except Exception as e:
            self.logger.error(f"Error answering query: {str(e)}")
            return "I apologize, but I'm experiencing technical difficulties right now. Please try again later."

    def print_response(self, response):
        """Print the response in a formatted way."""
        print("\n" + "="*80)
        print("AI Teacher Response:")
        print("-"*80)
        
        # Split response into answer and sources if present
        if "Sources:" in response:
            answer, sources = response.split("Sources:", 1)
            print(answer.strip())
            print("\nSources:")
            print(sources.strip())
        else:
            print(response.strip())
        print("="*80 + "\n")

def initialize_ollama():
    """Initialize Ollama with the best available model."""
    global MODEL_NAME
    
    try:
        models = ollama.list()
        available_models = [model.get('name') for model in models.get('models', [])]
        
        # Try to use the best available model
        if PRIMARY_MODEL in available_models:
            MODEL_NAME = PRIMARY_MODEL
            logger.info(f"Using primary model: {MODEL_NAME}")
            return True
        elif any(fallback in available_models for fallback in FALLBACK_MODELS):
            # Use the first available fallback model
            for fallback in FALLBACK_MODELS:
                if fallback in available_models:
                    MODEL_NAME = fallback
                    logger.info(f"Using fallback model: {MODEL_NAME}")
                    return True
        else:
            logger.warning(f"No preferred models available. Available models: {available_models}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to initialize Ollama: {str(e)}")
        return False

def print_welcome_message():
    """Print welcome message for the chatbot."""
    print("🎓 Welcome to AI Teacher Chatbot!")
    print("📚 Your intelligent learning assistant")
    print("="*80)
    print("💡 Features:")
    print("   • Answer questions with detailed explanations")
    print("   • Provide step-by-step solutions")
    print("   • Search for current information")
    print("   • Generate educational content")
    print("="*80 + "\n")

def get_chatbot_response(user_input: str, conversation_history: List[Dict[str, str]]) -> str:
    """Get response from the chatbot using the best available model."""
    try:
        # Create the conversation context
        messages = [
            {
                "role": "system",
                "content": """You are an intelligent and helpful teacher assistant. Your role is to:
1. Provide clear, accurate, and educational responses
2. Break down complex concepts into understandable parts
3. Give step-by-step explanations when appropriate
4. Use examples to illustrate points
5. Be encouraging and supportive
6. Ask clarifying questions when needed
7. Provide additional resources or suggestions when helpful

Always maintain a professional yet friendly tone."""
            }
        ]
        
        # Add conversation history (last 5 exchanges to keep context manageable)
        recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
        messages.extend(recent_history)
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        # Get response from Ollama with optimized settings
        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            options={'timeout': TIMEOUT}
        )
        
        return response['message']['content']
        
    except Exception as e:
        logger.error(f"Error getting chatbot response: {str(e)}")
        return f"I apologize, but I encountered an error while processing your request: {str(e)}. Please try again."

def main():
    """Main function to run the chatbot in terminal."""
    print_welcome_message()
    
    # Initialize Ollama with best available model
    if not initialize_ollama():
        print("❌ Failed to initialize Ollama. Please make sure Ollama is running and models are available.")
        return
    
    print(f"🤖 Using model: {MODEL_NAME}")
    print("💡 Type 'quit' or 'exit' to stop the chatbot\n")
    
    # Initialize conversation history
    conversation_history = []
    
    while True:
        try:
            # Get user input
            user_input = input("👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye! Thanks for using the Teacher Chatbot!")
                break
            
            if not user_input:
                continue
            
            # Get response from chatbot
            response = get_chatbot_response(user_input, conversation_history)
            
            # Add to conversation history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})
            
            # Keep only last 10 exchanges to manage memory
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]
            
            print(f"🤖 Assistant: {response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye! Thanks for using the Teacher Chatbot!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            continue

if __name__ == '__main__':
    main()