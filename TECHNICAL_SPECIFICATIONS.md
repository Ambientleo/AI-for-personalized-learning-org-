# AI Learning Platform - Technical Specifications

## 🏗️ System Architecture Overview

### **Technology Stack**

| **Layer** | **Technology** | **Version** | **Purpose** |
|-----------|----------------|-------------|-------------|
| **Frontend** | React | 18.3.1 | User interface framework |
| **Frontend** | TypeScript | 5.5.3 | Type-safe JavaScript |
| **Frontend** | Vite | 5.4.1 | Build tool and dev server |
| **Frontend** | Tailwind CSS | 3.4.11 | Utility-first CSS framework |
| **Frontend** | React Router | 6.26.2 | Client-side routing |
| **Frontend** | React Query | 5.56.2 | Data fetching and caching |
| **Backend** | Python | 3.x | Server-side programming |
| **Backend** | Flask | Latest | Web framework |
| **Backend** | Flask-CORS | Latest | Cross-origin resource sharing |
| **AI** | Ollama | Latest | Local LLM framework |
| **AI** | llama3:latest | Latest | Large language model |

## 📊 Detailed Component Analysis

### **1. Frontend Architecture**

#### **Core Components**
```typescript
// Main Application Structure
App.tsx
├── Authentication (Protected Routes)
├── Navigation (Header + Sidebar)
├── Page Components
│   ├── Dashboard
│   ├── CourseRecommender
│   ├── RoadmapGenerator
│   ├── AITeacher
│   ├── QuizGenerator
│   ├── Profile
│   └── Settings
└── UI Components (shadcn/ui)
```

#### **State Management Strategy**
- **Local State**: React hooks for component-specific state
- **Global State**: LocalStorage for persistent data
- **Server State**: React Query for API data management
- **Event System**: Custom events for cross-component communication

#### **Key Features**
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Dark Mode**: Theme switching capability
- **Real-time Updates**: Event-driven architecture
- **Offline Support**: LocalStorage-based data persistence

### **2. Backend Microservices**

#### **Service 1: Course Recommender (Port 5001)**
```python
# Core Functionality
- Course recommendation engine
- Content similarity analysis
- Web scraping for external courses
- Hybrid recommendation system

# API Endpoints
GET  /health                    # Health check
POST /api/recommend            # Get course recommendations
GET  /api/search?q=<query>     # Search courses
GET  /api/courses              # Get all courses
GET  /api/topics               # Get available topics
```

#### **Service 2: Roadmap Generator (Port 5002)**
```python
# Core Functionality
- Learning path generation
- Template-based AI generation
- Structured roadmap creation
- Customizable learning paths

# API Endpoints
GET  /health                    # Health check
POST /api/generate             # Generate roadmap
GET  /api/generate/<topic>     # Generate roadmap by topic
GET  /api/templates            # Get roadmap templates
GET  /api/template/<id>        # Get specific template
```

#### **Service 3: AI Teacher (Port 5003)**
```python
# Core Functionality
- Educational chatbot
- Ollama LLM integration
- Knowledge base search
- Context-aware responses

# API Endpoints
GET  /health                    # Health check
POST /api/chat                 # Chat with AI teacher
GET  /api/chat/<message>       # Chat via GET request
GET  /api/suggestions          # Get suggested questions
GET  /api/topics               # Get available topics
GET  /api/status               # Get service status
```

#### **Service 4: Quiz Generator (Port 5004)**
```python
# Core Functionality
- Multi-modal quiz generation
- Ollama LLM integration
- File processing (PDF, DOCX, TXT)
- Web scraping for content
- User history management

# API Endpoints
GET  /health                    # Health check
POST /api/generate             # Generate quiz
POST /api/generate/file        # Generate quiz from file
GET  /api/generate/<topic>     # Generate quiz from topic
POST /api/scrape-url           # Scrape URL content
POST /api/validate             # Validate quiz
GET  /api/supported-types      # Get supported file types
GET  /api/history/<user_id>    # Get user history
GET  /api/history/<user_id>/stats  # Get user statistics
DELETE /api/history/<user_id>/clear # Clear user history
POST /api/chat                 # Add chat history
```

### **3. AI Integration Architecture**

#### **Ollama LLM Integration**
```python
# Model Configuration
- Model: llama3:latest
- Context Window: Large (supports complex queries)
- Response Format: Structured JSON
- Error Handling: Fallback mechanisms

# Usage Patterns
1. Quiz Generation: Content → Questions + Answers
2. Chatbot Responses: Query → Educational Answer
3. Content Analysis: Text → Structured Information
```

#### **Content Processing Pipeline**
```python
# Multi-Modal Input Processing
1. Text Input: Direct processing
2. File Upload: PDF/DOCX/TXT extraction
3. URL Scraping: Web content extraction
4. Topic-based: Pre-defined content generation

# Processing Steps
Input → Content Extraction → AI Processing → Validation → Output
```

### **4. Data Architecture**

#### **Frontend Data Storage**
```typescript
// LocalStorage Structure
{
  user: {
    id: string,
    name: string,
    email: string,
    // ... other profile data
  },
  learningStats: {
    coursesCompleted: number,
    studyHours: number,
    quizzesTaken: number,
    currentStreak: number,
    totalXP: number,
    level: number
  },
  userPreferences: {
    notifications: boolean,
    emailNotifications: boolean,
    darkMode: boolean,
    language: string
  },
  activities: Activity[]
}
```

#### **Backend Data Storage**
```python
# File-based Storage
- user_history.json: User activity and quiz history
- Course database: Internal course recommendations
- Template database: Roadmap templates
- Knowledge base: AI teacher knowledge sources
```

### **5. API Communication Patterns**

#### **Request/Response Patterns**
```typescript
// Standard API Response Format
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Error Handling
interface ErrorResponse {
  error: string;
  details?: string;
  status: number;
}
```

#### **Authentication Flow**
```typescript
// Client-side Authentication
const isAuthenticated = () => {
  return localStorage.getItem('isAuthenticated') === 'true';
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  return isAuthenticated() ? children : <Navigate to="/login" />;
};
```

### **6. Performance Optimizations**

#### **Frontend Optimizations**
- **Code Splitting**: Lazy loading of components
- **Memoization**: React.memo for expensive components
- **Debouncing**: Search input optimization
- **Caching**: React Query for API responses

#### **Backend Optimizations**
- **Async Processing**: Non-blocking operations
- **Connection Pooling**: Efficient database connections
- **Caching**: Response caching for repeated queries
- **Error Handling**: Graceful degradation

### **7. Security Considerations**

#### **Frontend Security**
- **Input Validation**: Client-side validation
- **XSS Prevention**: Sanitized content rendering
- **CSRF Protection**: Token-based protection
- **Secure Storage**: Sensitive data encryption

#### **Backend Security**
- **CORS Configuration**: Controlled cross-origin access
- **Input Sanitization**: Server-side validation
- **Rate Limiting**: API usage restrictions
- **Error Handling**: Secure error messages

### **8. Deployment Architecture**

#### **Development Environment**
```bash
# Service Startup Order
1. Frontend (npm run dev) - Port 5173
2. Course Recommender - Port 5001
3. Roadmap Generator - Port 5002
4. AI Teacher - Port 5003
5. Quiz Generator - Port 5004
```

#### **Production Considerations**
- **Containerization**: Docker for each service
- **Load Balancing**: Nginx reverse proxy
- **Monitoring**: Health check endpoints
- **Logging**: Structured logging system

### **9. Scalability Features**

#### **Horizontal Scaling**
- **Stateless Services**: Independent service scaling
- **Microservices**: Isolated service deployment
- **API Gateway**: Centralized request routing
- **Database Sharding**: Distributed data storage

#### **Vertical Scaling**
- **Resource Optimization**: Efficient memory usage
- **Caching Strategy**: Multi-level caching
- **Connection Pooling**: Optimized database connections
- **Async Processing**: Non-blocking operations

### **10. Monitoring & Analytics**

#### **User Analytics**
- **Activity Tracking**: User interaction monitoring
- **Progress Metrics**: Learning progress measurement
- **Performance Metrics**: System performance monitoring
- **Error Tracking**: Application error monitoring

#### **System Monitoring**
- **Health Checks**: Service availability monitoring
- **Performance Metrics**: Response time tracking
- **Resource Usage**: CPU/Memory monitoring
- **Error Rates**: Error frequency tracking

This technical specification provides a comprehensive overview of the AI Learning Platform's architecture, implementation details, and operational considerations. 