# Writingway Web - AI-Powered Creative Writing Assistant

> **A modern web-based creative writing companion powered by AI**

Writingway Web is a complete rewrite of the original desktop application, now available as a modern web application. It provides writers with powerful AI assistance, project management, and collaborative writing tools through an intuitive web interface.

## ✨ Key Features

- **🤖 AI Writing Assistant:** Integrated OpenAI and Anthropic AI models for writing assistance, brainstorming, and content improvement
- **📝 Rich Text Editor:** Modern WYSIWYG editor with auto-save functionality
- **📁 Project Management:** Organize your writing projects with hierarchical document structure
- **💬 Interactive AI Chat:** Real-time conversation with AI for creative guidance and feedback
- **🎨 Modern UI:** Clean, responsive interface built with React and Material-UI
- **🔐 User Authentication:** Secure user accounts with JWT-based authentication
- **☁️ Web-Based:** Access your writing from anywhere with an internet connection
- **🚀 Fast & Responsive:** Built with modern web technologies for optimal performance

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** for the backend
- **Node.js 16+** for the frontend
- **Git** for version control

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Writingway
   ```

2. **Quick Start (Recommended):**

   **For Linux/macOS:**
   ```bash
   ./start_dev.sh
   ```

   **For Windows:**
   ```cmd
   start_dev.bat
   ```

3. **Manual Setup:**

   **Backend Setup:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your configuration
   uvicorn main:app --reload
   ```

   **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   cp .env.example .env
   # Edit .env with your configuration
   npm start
   ```

### Access the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
DATABASE_URL=sqlite:///./writingway.db
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

**Frontend (.env):**
```env
REACT_APP_API_URL=http://localhost:8000/api
```

## 🏗️ Architecture

### Backend (FastAPI)
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **JWT Authentication** - Secure user sessions
- **OpenAI/Anthropic Integration** - AI writing assistance

### Frontend (React)
- **React 18** - Modern UI framework
- **Material-UI** - Component library
- **React Query** - Data fetching and caching
- **Zustand** - State management
- **React Quill** - Rich text editor

### Database
- **SQLite** (development) / **PostgreSQL** (production)
- User management, projects, documents, AI conversations

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

## 📚 API Documentation

The API documentation is automatically generated and available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

### Backend Technologies
- **FastAPI** - High-performance web framework
- **SQLAlchemy** - Python SQL toolkit
- **OpenAI** - AI language models
- **Anthropic** - Claude AI models

### Frontend Technologies
- **React** - UI library
- **Material-UI** - React component library
- **React Query** - Data synchronization
- **React Quill** - Rich text editing

## 📞 Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Join our Discord community: <https://discord.gg/xkkGaRFXNX>

---

**Note:** This is the web version of Writingway. The original desktop application files have been replaced with this modern web-based implementation.
