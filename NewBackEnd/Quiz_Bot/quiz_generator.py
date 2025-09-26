import requests
import json
import re
import os
import time
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
import PyPDF2
import docx
import textwrap
import tkinter as tk
from tkinter import filedialog
import random
from typing import List, Dict, Any
from docx import Document
import logging
import ollama

console = Console()
logger = logging.getLogger(__name__)

class QuizGenerator:
    def __init__(self):
        self.console = Console()
        self.supported_extensions = {'.txt', '.pdf', '.docx'}
        self.question_templates = {
            'mcq': [
                "What is the main concept of {topic}?",
                "Which of the following best describes {topic}?",
                "What is the primary purpose of {topic}?",
                "Which statement about {topic} is correct?",
                "What is the key characteristic of {topic}?"
            ],
            'fill_blank': [
                "The main idea of {topic} is _____.",
                "{topic} is primarily used for _____.",
                "The key concept in {topic} is _____.",
                "_____ is an important aspect of {topic}.",
                "The primary function of {topic} is _____."
            ],
            'true_false': [
                "{topic} is always true.",
                "{topic} can be applied in all situations.",
                "{topic} is a fundamental concept.",
                "{topic} requires special conditions.",
                "{topic} is universally accepted."
            ]
        }
        self.num_questions = 5

    def read_file_content(self, filepath: str) -> str:
        """Read content from different file types with improved error handling."""
        try:
            ext = os.path.splitext(filepath)[1].lower()
            
            if ext not in self.supported_extensions:
                raise ValueError(f"Unsupported file type: {ext}. Supported types are: {', '.join(self.supported_extensions)}")
            
            if ext == '.txt':
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    # Try with a different encoding if UTF-8 fails
                    with open(filepath, 'r', encoding='latin-1') as f:
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
            
            if not content.strip():
                raise ValueError("File is empty or contains no readable text")
                
            return content
            
        except Exception as e:
            logger.error(f"Error reading file {filepath}: {str(e)}")
            raise

    def validate_question(self, q, i):
        """Validate a single question based on its type."""
        if 'type' not in q:
            raise ValueError(f"Question {i} is missing type field")
        
        if not isinstance(q['question'], str) or not q['question'].strip():
            raise ValueError(f"Question {i} has invalid question text")
        
        if 'explanation' not in q or not isinstance(q['explanation'], str) or not q['explanation'].strip():
            raise ValueError(f"Question {i} is missing or has invalid explanation")
        
        if q['type'] == 'mcq':
            if not all(k in q for k in ['options', 'correct_answer']):
                raise ValueError(f"MCQ {i} is missing required fields")
            if not isinstance(q['options'], list) or len(q['options']) != 4:
                raise ValueError(f"MCQ {i} must have exactly 4 options")
            if q['correct_answer'] not in ['A', 'B', 'C', 'D']:
                raise ValueError(f"MCQ {i} has invalid correct_answer: {q['correct_answer']}")
        
        elif q['type'] == 'fill_blank':
            if 'correct_answer' not in q:
                raise ValueError(f"Fill in the blank {i} is missing correct_answer")
            if '_____' not in q['question']:
                raise ValueError(f"Fill in the blank {i} must contain _____ to indicate the blank")
        
        elif q['type'] == 'true_false':
            if 'correct_answer' not in q:
                raise ValueError(f"True/False {i} is missing correct_answer")
            if q['correct_answer'] not in ['True', 'False']:
                raise ValueError(f"True/False {i} has invalid correct_answer: {q['correct_answer']}")
        
        else:
            raise ValueError(f"Question {i} has invalid type: {q['type']}")

    def generate_quiz(self, source: str, num_questions: int = 5, question_types: List[str] = None) -> List[Dict[str, Any]]:
        """Generate quiz from a file path or content with improved error handling and validation."""
        try:
            if not question_types:
                question_types = ["mcq", "fill_blank", "true_false"]
            
            # Validate question types
            valid_types = {"mcq", "fill_blank", "true_false"}
            invalid_types = set(question_types) - valid_types
            if invalid_types:
                raise ValueError(f"Invalid question types: {invalid_types}. Valid types are: {valid_types}")
            
            # Determine if source is a file path or content
            if os.path.exists(source):
                # It's a file path
                content = self.read_file_content(source)
            else:
                # It's content
                content = source
            
            if not content:
                raise ValueError("No content could be extracted from the source")
            
            # Extract topics and generate questions
            topics = self.extract_topics(content)
            if not topics:
                raise ValueError("Could not extract meaningful topics from the content")
            
            questions = []
            attempts = 0
            max_attempts = num_questions * 2
            
            while len(questions) < num_questions and attempts < max_attempts:
                topic = topics[attempts % len(topics)]  # Cycle through topics
                question_type = question_types[attempts % len(question_types)]  # Cycle through types
                
                question = self.generate_question(topic, question_type)
                if question:
                    try:
                        self.validate_question(question, len(questions) + 1)
                        questions.append(question)
                    except ValueError as e:
                        logger.warning(f"Question validation failed: {str(e)}")
                attempts += 1
            
            if len(questions) < num_questions:
                logger.warning(f"Could only generate {len(questions)} questions out of {num_questions} requested")
            
            return questions
            
        except Exception as e:
            logger.error(f"Error generating quiz: {str(e)}")
            raise

    def generate_quiz_from_content(self, content: str, num_questions: int = 5, question_types: List[str] = None) -> List[Dict[str, Any]]:
        """Generate quiz from text content."""
        return self.generate_quiz(content, num_questions, question_types)

    def generate_quiz_from_topic(self, topic: str, num_questions: int = 5, question_types: List[str] = None) -> List[Dict[str, Any]]:
        """Generate quiz from a topic using AI."""
        try:
            if not question_types:
                question_types = ["mcq", "fill_blank", "true_false"]
            
            # Validate question types
            valid_types = {"mcq", "fill_blank", "true_false"}
            invalid_types = set(question_types) - valid_types
            if invalid_types:
                raise ValueError(f"Invalid question types: {invalid_types}. Valid types are: {valid_types}")
            
            questions = []
            attempts = 0
            max_attempts = num_questions * 2
            
            while len(questions) < num_questions and attempts < max_attempts:
                question_type = question_types[attempts % len(question_types)]  # Cycle through types
                
                question = self.generate_question(topic, question_type)
                if question:
                    try:
                        self.validate_question(question, len(questions) + 1)
                        questions.append(question)
                    except ValueError as e:
                        logger.warning(f"Question validation failed: {str(e)}")
                attempts += 1
            
            if len(questions) < num_questions:
                logger.warning(f"Could only generate {len(questions)} questions out of {num_questions} requested")
            
            return questions
            
        except Exception as e:
            logger.error(f"Error generating quiz from topic: {str(e)}")
            raise

    def select_file(self) -> str:
        """Open file dialog to select a file."""
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        file_path = filedialog.askopenfilename(
            title="Select a file for quiz generation",
            filetypes=[
                ("Text files", "*.txt"),
                ("PDF files", "*.pdf"),
                ("Word documents", "*.docx"),
                ("All files", "*.*")
            ]
        )
        
        root.destroy()
        return file_path

    def display_quiz(self, questions: List[Dict[str, Any]]) -> None:
        """Display quiz questions in a formatted way."""
        console.print(f"\n[bold green]Generated {len(questions)} questions:[/bold green]\n")
        
        for i, question in enumerate(questions, 1):
            console.print(f"[bold blue]Question {i}:[/bold blue]")
            console.print(f"Type: {question['type'].upper()}")
            console.print(f"Question: {question['question']}")
            
            if question['type'] == 'mcq':
                for j, option in enumerate(question['options']):
                    letter = chr(65 + j)
                    console.print(f"  {letter}. {option}")
                console.print(f"Correct Answer: {question['correct_answer']}")
            
            elif question['type'] == 'fill_blank':
                console.print(f"Correct Answer: {question['correct_answer']}")
            
            elif question['type'] == 'true_false':
                console.print(f"Correct Answer: {question['correct_answer']}")
            
            console.print(f"Explanation: {question['explanation']}")
            console.print("-" * 50)

    def extract_topics(self, content: str) -> List[str]:
        """Extract meaningful topics from content with improved filtering."""
        # Split content into sentences
        sentences = re.split(r'[.!?]+', content)
        
        # Filter and clean sentences
        topics = []
        for sentence in sentences:
            sentence = sentence.strip()
            # Filter out very short or very long sentences
            words = sentence.split()
            if 3 <= len(words) <= 15:
                # Remove common stop words and clean the sentence
                cleaned = re.sub(r'\b(the|a|an|and|or|but|in|on|at|to|for|of|with|by)\b', '', sentence, flags=re.IGNORECASE)
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                if cleaned:
                    topics.append(cleaned)
        
        # If no good sentences found, try paragraphs
        if not topics:
            paragraphs = content.split('\n\n')
            topics = [p.strip() for p in paragraphs if len(p.strip().split()) >= 3]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_topics = []
        for topic in topics:
            if topic.lower() not in seen:
                seen.add(topic.lower())
                unique_topics.append(topic)
        
        return unique_topics or ["general knowledge"]

    def generate_question(self, topic: str, question_type: str) -> Dict[str, Any]:
        """Generate a single question using Ollama AI."""
        try:
            if not topic or not question_type:
                return None
            
            # Create a prompt for Ollama based on question type
            if question_type == 'mcq':
                prompt = f"""Generate a multiple choice question about: {topic}

Requirements:
- Create a clear, educational question
- Provide exactly 4 options (A, B, C, D)
- Make sure only one answer is correct
- Include a brief explanation

Format your response as JSON:
{{
    "type": "mcq",
    "question": "Your question here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "A",
    "explanation": "Brief explanation of why this is correct"
}}"""

            elif question_type == 'fill_blank':
                prompt = f"""Generate a fill-in-the-blank question about: {topic}

Requirements:
- Create a sentence with a blank (use _____ to indicate the blank)
- Provide the correct answer
- Include a brief explanation

Format your response as JSON:
{{
    "type": "fill_blank",
    "question": "The main concept of {topic} is _____.",
    "correct_answer": "Your answer here",
    "explanation": "Brief explanation of the answer"
}}"""

            elif question_type == 'true_false':
                prompt = f"""Generate a true/false question about: {topic}

Requirements:
- Create a clear statement that can be true or false
- Determine if it's true or false
- Include a brief explanation

Format your response as JSON:
{{
    "type": "true_false",
    "question": "Your statement here.",
    "correct_answer": "True",
    "explanation": "Brief explanation of why this is true or false"
}}"""

            else:
                logger.warning(f"Unknown question type: {question_type}")
                return None

            try:
                # Use Ollama to generate the question
                response = ollama.chat(model='mistral:latest', messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ])
                
                # Extract the response content
                content = response['message']['content']
                
                # Try to parse JSON from the response
                try:
                    # Look for JSON in the response
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        question_data = json.loads(json_match.group())
                        
                        # Validate the generated question
                        if self.validate_generated_question(question_data, question_type):
                            return question_data
                        else:
                            logger.warning("Generated question failed validation, using fallback")
                    else:
                        logger.warning("No JSON found in Ollama response, using fallback")
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON from Ollama response: {e}, using fallback")
                    
            except Exception as e:
                logger.warning(f"Ollama request failed: {e}, using fallback")
            
            # Fallback to template-based generation if Ollama fails
            return self.generate_fallback_question(topic, question_type)
                
        except Exception as e:
            logger.error(f"Error generating question: {str(e)}")
            return None

    def validate_generated_question(self, question_data: Dict[str, Any], expected_type: str) -> bool:
        """Validate a question generated by Ollama."""
        try:
            if not isinstance(question_data, dict):
                return False
            
            if question_data.get('type') != expected_type:
                return False
            
            if not question_data.get('question') or not isinstance(question_data['question'], str):
                return False
            
            if not question_data.get('explanation') or not isinstance(question_data['explanation'], str):
                return False
            
            if expected_type == 'mcq':
                if not question_data.get('options') or not isinstance(question_data['options'], list) or len(question_data['options']) != 4:
                    return False
                if question_data.get('correct_answer') not in ['A', 'B', 'C', 'D']:
                    return False
            
            elif expected_type == 'fill_blank':
                if not question_data.get('correct_answer') or not isinstance(question_data['correct_answer'], str):
                    return False
                if '_____' not in question_data['question']:
                    return False
            
            elif expected_type == 'true_false':
                if question_data.get('correct_answer') not in ['True', 'False']:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating generated question: {e}")
            return False

    def generate_fallback_question(self, topic: str, question_type: str) -> Dict[str, Any]:
        """Generate a fallback question using templates when Ollama fails."""
        try:
            if question_type == 'mcq':
                template = random.choice(self.question_templates['mcq'])
                question = template.format(topic=topic)
                
                # Generate more meaningful options based on the topic
                options = [
                    f"The primary concept of {topic}",
                    f"A common misconception about {topic}",
                    f"An advanced aspect of {topic}",
                    f"A practical application of {topic}"
                ]
                
                # Shuffle options and set correct answer
                random.shuffle(options)
                correct_index = options.index(f"The primary concept of {topic}")
                correct_answer = chr(65 + correct_index)  # Convert 0-3 to A-D
                
                return {
                    'type': 'mcq',
                    'question': question,
                    'options': options,
                    'correct_answer': correct_answer,
                    'explanation': f"This question tests understanding of {topic} and its core concepts. The correct answer is {correct_answer} because it represents the primary concept."
                }
                
            elif question_type == 'fill_blank':
                template = random.choice(self.question_templates['fill_blank'])
                question = template.format(topic=topic)
                
                # Generate a more specific answer
                answer = f"The key concept of {topic}"
                if "main idea" in question.lower():
                    answer = f"The main idea of {topic}"
                elif "used for" in question.lower():
                    answer = f"The primary purpose of {topic}"
                elif "key concept" in question.lower():
                    answer = f"The fundamental principle of {topic}"
                
                return {
                    'type': 'fill_blank',
                    'question': question,
                    'correct_answer': answer,
                    'explanation': f"This question tests knowledge of {topic} and its fundamental principles. The blank should be filled with the key concept or main idea."
                }
                
            elif question_type == 'true_false':
                template = random.choice(self.question_templates['true_false'])
                question = template.format(topic=topic)
                
                # Make the answer more meaningful
                correct_answer = 'True' if random.random() > 0.5 else 'False'
                explanation = f"This question tests understanding of {topic} and its general principles. The statement is {correct_answer.lower()} because "
                if correct_answer == 'True':
                    explanation += f"{topic} is a fundamental concept that applies in most cases."
                else:
                    explanation += f"{topic} may not always be true in all situations."
                
                return {
                    'type': 'true_false',
                    'question': question,
                    'correct_answer': correct_answer,
                    'explanation': explanation
                }
                
            else:
                logger.warning(f"Unknown question type: {question_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating fallback question: {str(e)}")
            return None

def main():
    console.print(Panel("[bold blue]Welcome to the AI Quiz Generator![/bold blue]"))
    
    generator = QuizGenerator()
    
    while True:
        console.print("\n[bold]Choose quiz generation method:[/bold]")
        console.print("1. Generate from topic")
        console.print("2. Generate from file")
        console.print("3. Generate from text input")
        console.print("4. Quit")
        
        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4"])
        
        if choice == "4":
            break
            
        num_questions = int(Prompt.ask("How many questions would you like?", default="5"))
        
        # Ask for question types
        console.print("\n[bold]Select question types:[/bold]")
        console.print("1. Multiple Choice (mcq)")
        console.print("2. Fill in the Blanks (fill_blank)")
        console.print("3. True/False (true_false)")
        console.print("4. Random (any type)")
        console.print("5. All types (mixed)")
        
        type_choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5"])
        question_types = []
        
        if type_choice == "1":
            question_types = ["mcq"]
        elif type_choice == "2":
            question_types = ["fill_blank"]
        elif type_choice == "3":
            question_types = ["true_false"]
        elif type_choice == "4":
            # Random option - will be handled in the generate_quiz methods
            question_types = ["random"]
        elif type_choice == "5":
            question_types = ["mcq", "fill_blank", "true_false"]
        
        if choice == "1":
            topic = Prompt.ask("Enter a topic for the quiz")
            console.print("\n[bold]Generating quiz from topic...[/bold]")
            questions = generator.generate_quiz_from_topic(topic, num_questions, question_types)
        
        elif choice == "2":
            console.print("\n[bold]Please select a file in the file dialog...[/bold]")
            file_path = generator.select_file()
            
            if not file_path:
                console.print("[yellow]No file selected. Skipping...[/yellow]")
                continue
                
            try:
                console.print(f"\n[bold]Generating quiz from file: {os.path.basename(file_path)}[/bold]")
                questions = generator.generate_quiz(file_path, num_questions, question_types)
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
                continue
        
        elif choice == "3":
            console.print("\nEnter your text (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    break
                lines.append(line)
            content = "\n".join(lines[:-1])  # Remove the last empty line
            console.print("\n[bold]Generating quiz from text...[/bold]")
            questions = generator.generate_quiz_from_content(content, num_questions, question_types)
        
        if questions:
            generator.display_quiz(questions)
        
        console.print("\n")

if __name__ == "__main__":
    main() 