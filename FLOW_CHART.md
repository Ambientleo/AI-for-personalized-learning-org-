# AI Learning Platform - System Flow Chart

## 🔄 Complete System Flow

```mermaid
graph TB
    A[User Access] --> B{Authentication}
    B -->|Not Authenticated| C[Login Page]
    B -->|Authenticated| D[Main Dashboard]
    
    C --> E[Login Form]
    E --> F[LocalStorage Auth]
    F --> D
    
    D --> G[Navigation Menu]
    G --> H[Dashboard]
    G --> I[Course Recommender]
    G --> J[Roadmap Generator]
    G --> K[AI Teacher]
    G --> L[Quiz Generator]
    G --> M[Profile]
    G --> N[Settings]
    
    %% Course Recommender Flow
    I --> I1[User Interests Input]
    I1 --> I2[Course Recommender API]
    I2 --> I3[Internal Course Database]
    I2 --> I4[External Course Scraping]
    I3 --> I5[Personalized Recommendations]
    I4 --> I5
    I5 --> I6[Display Results]
    
    %% Roadmap Generator Flow
    J --> J1[Topic/Skill Input]
    J1 --> J2[Roadmap Generator API]
    J2 --> J3[AI Roadmap Generation]
    J3 --> J4[Template Matching]
    J4 --> J5[Structured Learning Path]
    J5 --> J6[Display Roadmap]
    
    %% AI Teacher Flow
    K --> K1[User Question]
    K1 --> K2[Teacher Chatbot API]
    K2 --> K3[Ollama LLM Processing]
    K3 --> K4[Knowledge Base Search]
    K4 --> K5[Response Generation]
    K5 --> K6[Display Answer + Sources]
    
    %% Quiz Generator Flow
    L --> L1{Input Method}
    L1 -->|Topic| L2[Topic-based Quiz]
    L1 -->|File Upload| L3[File Processing]
    L1 -->|URL| L4[Web Scraping]
    L1 -->|Text Input| L5[Text Processing]
    
    L2 --> L6[Quiz Generator API]
    L3 --> L7[File Content Extraction]
    L4 --> L8[URL Content Scraping]
    L5 --> L9[Text Analysis]
    
    L6 --> L10[Ollama LLM Quiz Generation]
    L7 --> L10
    L8 --> L10
    L9 --> L10
    
    L10 --> L11[Question Validation]
    L11 --> L12[Quiz Display]
    L12 --> L13[User Answers]
    L13 --> L14[Score Calculation]
    L14 --> L15[Results & History]
    
    %% Profile & Settings
    M --> M1[User Profile Management]
    N --> N1[App Preferences]
    N --> N2[Security Settings]
    N --> N3[Data Export]
    
    %% Data Flow
    H --> H1[Activity Tracking]
    H1 --> H2[LocalStorage Stats]
    H2 --> H3[Progress Visualization]
    
    L15 --> H1
    K6 --> H1
    I6 --> H1
    J6 --> H1
    
    %% Backend Services
    subgraph "Backend Microservices"
        I2
        J2
        K2
        L6
    end
    
    %% External APIs
    subgraph "External Services"
        I4
        L4
    end
    
    %% AI Models
    subgraph "AI Models"
        K3
        L10
        J3
    end
    
    %% Styling
    classDef frontend fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef backend fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef ai fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef external fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
    class A,C,D,E,F,G,H,I,J,K,L,M,N frontend
    class I2,J2,K2,L6,I3 backend
    class K3,L10,J3 ai
    class I4,L4 external
```

## 📋 Flow Description

### **1. Authentication Flow**
- User accesses the application
- System checks authentication status
- If not authenticated, redirects to login page
- After successful login, stores auth in localStorage
- Redirects to main dashboard

### **2. Main Navigation**
- Dashboard: Overview and progress tracking
- Course Recommender: Find relevant courses
- Roadmap Generator: Create learning paths
- AI Teacher: Get educational help
- Quiz Generator: Create and take assessments
- Profile: Manage user information
- Settings: Configure app preferences

### **3. Course Recommender Flow**
- User inputs interests or searches
- API processes request
- Combines internal database and external scraping
- Returns personalized recommendations
- Displays results to user

### **4. Roadmap Generator Flow**
- User selects topic or skill
- API generates learning roadmap
- Uses AI and template matching
- Creates structured learning path
- Displays roadmap to user

### **5. AI Teacher Flow**
- User asks educational question
- API processes with Ollama LLM
- Searches knowledge base
- Generates comprehensive response
- Displays answer with sources

### **6. Quiz Generator Flow**
- User chooses input method (topic/file/URL/text)
- System processes content accordingly
- Uses Ollama LLM to generate questions
- Validates question quality
- Displays interactive quiz
- Tracks user answers and calculates scores

### **7. Data Integration**
- All user activities feed into dashboard
- Activity tracking updates localStorage
- Progress visualization shows learning insights
- Real-time updates across components

## 🔧 Technical Architecture

### **Frontend (React + TypeScript)**
- Component-based architecture
- LocalStorage for state persistence
- Real-time event handling
- Responsive UI with Tailwind CSS

### **Backend (Flask Microservices)**
- Independent services on different ports
- RESTful API design
- JSON data exchange
- File-based storage

### **AI Integration**
- Ollama LLM for natural language processing
- Content analysis for recommendations
- Template-based generation for roadmaps
- Multi-modal input processing

### **External Services**
- Web scraping for course discovery
- URL content extraction for quizzes
- Knowledge base integration for AI teacher 