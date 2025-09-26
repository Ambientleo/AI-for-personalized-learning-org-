🎓 AI Teacher Chatbot

An intelligent educational assistant powered by web search, content scraping, and large language models

🌟 What It Is
The AI Teacher Chatbot is a cutting-edge educational assistant that transforms the way students learn. By combining web search capabilities, intelligent content scraping, and advanced large language models, it delivers clear, detailed explanations tailored to each learner's needs.
✨ Key Features

🔍 Smart Web Search - Finds relevant educational content
🧠 AI-Powered Responses - Uses Ollama LLM for intelligent answers
📱 Modern Interface - Responsive design that works everywhere
🎯 Subject Classification - Automatically detects question topics
💾 Smart Caching - Avoids redundant processing
📝 Markdown Support - Beautiful, formatted responses


🏗️ Architecture Overview
mermaidgraph TD
    A[Student Question] --> B[Flask Web Interface]
    B --> C[Question Classifier]
    C --> D[Web Search Engine]
    D --> E[Content Scraper]
    E --> F[Ollama LLM]
    F --> G[Formatted Response]
    G --> H[Student]
🔧 Core Components
1. 🌐 Web Interface

Framework: Flask-powered backend
Design: Modern, mobile-responsive UI
Features: Real-time chat, typing indicators
Formatting: Full Markdown support for rich content

2. ⚙️ Backend System

Intelligence: Advanced question understanding
Search: Automated web content discovery
AI Engine: Ollama large language model integration
Storage: Efficient disk-based caching system

3. 📊 Data Processing

Sources: Trusted educational websites only
Performance: Parallel processing for speed
Quality: Intelligent text cleaning and organization
Classification: Automatic subject tagging


📚 Supported Subjects
<div align="center">
🔢 Math🔬 Science📜 History💻 Programming📖 Literature🗣️ Language🎨 Art🌍 Geography💰 Economics🤔 Philosophy
</div>

🚀 Development Journey
Phase 1: 🏗️ Foundation

 Flask application setup
 Basic chat interface implementation
 Logging and error handling system
 Initial project structure

Phase 2: 🧩 Core Features

 Question processing and classification
 Web search integration
 Content scraping engine
 Ollama LLM connection

Phase 3: ✨ Enhancement

 Intelligent subject detection
 Response caching system
 Markdown formatting support
 Error handling improvements

Phase 4: ⚡ Optimization

 Parallel content scraping
 Performance caching
 Text processing refinements
 Prompt engineering optimization


🎯 Core Capabilities
🧠 Question Understanding

Automatic subject classification
Context-aware response generation
Source attribution and crediting
Graceful error handling

🌐 Information Retrieval

Educational website targeting
Concurrent multi-source scraping
Intelligent content cleaning
Reliability verification

💬 Response Generation

LLM-powered answer creation
Subject-specific customization
Rich Markdown formatting
Comprehensive source listing

👤 User Experience

Real-time chat interaction
Live typing indicators
Auto-scrolling message display
Cross-platform compatibility


🛠️ Installation & Setup
Prerequisites

Python 3.8+
Ollama installed and running
Internet connection for web search

Quick Start
bash# Clone the repository
git clone https://github.com/Ambientleo/AI-for-personalized-learning-org-.git
cd AI-for-personalized-learning-org-

# Install dependencies
pip install -r requirements.txt

# Start the application
python app.py
🚀 One-Click Start
bash# Windows
./start_all.bat

# PowerShell
./start_all.ps1


🤝 Contributing
We welcome contributions! Please see our Contributing Guidelines for details.
🐛 Bug Reports
Found a bug? Please open an issue with detailed information.
💡 Feature Requests
Have an idea? We'd love to hear it! Start a discussion.

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments

🤖 Ollama for providing the LLM infrastructure
🌐 Flask for the web framework
📚 Educational content providers for making knowledge accessible
👥 Open source community for inspiration and support


<div align="center">
🌟 Star this project if you find it helpful!
Made with ❤️ for educators and learners worldwide
