# WritingWay Project Structure

## 📁 Directory Overview

```
Writingway/
├── 📄 README.md                    # Project overview and basic info
├── 📄 SETUP_GUIDE.md              # Quick setup instructions for team members
├── 📄 DEPLOYMENT.md               # Production deployment guide
├── 📄 MySQL_Setup_Guide.md        # Detailed database setup
├── 📄 LICENSE                     # Project license
├── 📄 .gitignore                  # Git ignore rules
├── 📄 docker-compose.yml          # Docker configuration
├── 📄 ai_syory_mysql_schema.sql   # Database schema
├── 📄 database_schema.sql         # Alternative schema
├── 📄 start_dev.sh               # Development startup script (Unix)
├── 📄 start_dev.bat              # Development startup script (Windows)
│
├── 📁 assets/                     # Static assets
│   ├── 📁 icons/                 # Application icons
│   ├── 📁 quotes/                # Sample quotes/content
│   └── 🖼️ logo.png               # Application logo
│
├── 📁 backend/                    # Python FastAPI backend
│   ├── 📄 main.py                # FastAPI application entry point
│   ├── 📄 requirements.txt       # Python dependencies
│   ├── 📄 Dockerfile            # Backend Docker configuration
│   ├── 📄 init_db.py            # Database initialization script
│   ├── 📄 create_users.py       # Create default users
│   │
│   ├── 📁 core/                  # Core application modules
│   │   ├── 📄 __init__.py
│   │   ├── 📄 config.py          # Application configuration
│   │   └── 📄 security.py        # Authentication & security
│   │
│   ├── 📁 database/              # Database related modules
│   │   ├── 📄 __init__.py
│   │   ├── 📄 database.py        # Database connection
│   │   └── 📄 models.py          # SQLAlchemy models
│   │
│   ├── 📁 routers/               # API route handlers
│   │   ├── 📄 __init__.py
│   │   ├── 📄 auth.py            # Authentication routes
│   │   ├── 📄 projects.py        # Project management routes
│   │   ├── 📄 documents.py       # Document management routes
│   │   ├── 📄 ai_assistant.py    # AI assistance routes
│   │   └── 📄 settings.py        # User settings routes
│   │
│   ├── 📁 schemas/               # Pydantic schemas for API
│   │   ├── 📄 __init__.py
│   │   ├── 📄 user.py            # User-related schemas
│   │   └── 📄 project.py         # Project-related schemas
│   │
│   └── 📁 services/              # Business logic services
│       ├── 📄 __init__.py
│       ├── 📄 ai_service.py      # AI integration service
│       └── 📄 mock_ai_service.py # Fallback AI service
│
└── 📁 frontend/                   # React frontend application
    ├── 📄 package.json           # Node.js dependencies
    ├── 📄 Dockerfile            # Frontend Docker configuration
    │
    ├── 📁 public/                # Public static files
    │   ├── 📄 index.html         # Main HTML template
    │   ├── 📄 manifest.json      # PWA manifest
    │   └── 🖼️ favicon.ico        # Favicon
    │
    └── 📁 src/                   # React source code
        ├── 📄 index.js           # Application entry point
        ├── 📄 App.js             # Main App component
        ├── 📄 index.css          # Global styles
        │
        ├── 📁 components/        # Reusable React components
        │   ├── 📁 AI/            # AI-related components
        │   ├── 📁 Layout/        # Layout components
        │   ├── 📁 Project/       # Project components
        │   └── 📁 Document/      # Document components
        │
        ├── 📁 pages/             # Page components
        │   ├── 📁 Auth/          # Authentication pages
        │   ├── 📁 Dashboard/     # Dashboard page
        │   ├── 📁 Project/       # Project pages
        │   └── 📁 Document/      # Document editor pages
        │
        ├── 📁 services/          # API service modules
        │   ├── 📄 api.js         # Base API configuration
        │   ├── 📄 authService.js # Authentication service
        │   ├── 📄 projectService.js # Project service
        │   └── 📄 aiService.js   # AI service
        │
        └── 📁 utils/             # Utility functions
            └── 📄 constants.js   # Application constants
```

## 🔧 Key Components

### Backend (FastAPI)
- **Authentication**: JWT-based auth with bcrypt password hashing
- **Database**: SQLAlchemy ORM with MySQL support
- **AI Integration**: OpenAI GPT and Google Gemini APIs
- **API Documentation**: Auto-generated with FastAPI/OpenAPI

### Frontend (React)
- **UI Framework**: Material-UI (MUI) components
- **State Management**: React Query for server state
- **Routing**: React Router for navigation
- **Editor**: ReactQuill for rich text editing

### Database
- **Primary**: MySQL 8.0+
- **Models**: Users, Projects, Documents, Settings
- **Relationships**: Hierarchical project/document structure

## 🚀 Getting Started

1. Follow `SETUP_GUIDE.md` for initial setup
2. Configure `.env` file in backend directory
3. Run database initialization scripts
4. Start backend and frontend servers
5. Access application at http://localhost:3000

## 📝 Development Notes

- All interfaces are in English
- Responsive design for desktop and mobile
- AI features have fallback services
- Comprehensive error handling and logging
