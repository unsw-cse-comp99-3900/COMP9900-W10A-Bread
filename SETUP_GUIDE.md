# WritingWay Project Setup Guide

## 🚀 Quick Start

This is a full-stack writing assistance application with AI-powered features.

### 📋 Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)
- **MySQL 8.0+** (for database)
- **Git** (for version control)

### 🛠️ Installation Steps

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd Writingway
```

#### 2. Database Setup
1. Install MySQL and create a database:
```sql
CREATE DATABASE ai_syory;
```

2. Import the schema:
```bash
mysql -u root -p ai_syory < ai_syory_mysql_schema.sql
```

3. Update database configuration in `backend/.env`:
```env
DATABASE_URL=mysql+pymysql://root:your_password@localhost/ai_syory
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=ai_syory
```

#### 3. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Create initial users
python create_users.py

# Start backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 4. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 🔑 API Keys Configuration

Create `backend/.env` file with your API keys:

```env
# Database Configuration
DATABASE_URL=mysql+pymysql://root:your_password@localhost/ai_syory
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=ai_syory

# AI Service API Keys (Optional - has fallback)
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 🌐 Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 👤 Default Users

After running `create_users.py`, you can login with:

- **Admin**: username: `admin`, password: `admin123`
- **Demo**: username: `demo`, password: `demo123`

### 🎯 Key Features

- **Dual-Panel Writing Interface**: Writing area + AI results panel
- **AI Writing Assistance**: Analyze, Improve, Continue writing
- **Project Management**: Organize documents in projects
- **Real-time Collaboration**: Multiple users can work on projects
- **Smart Analysis**: Detailed text analysis with specific suggestions

### 🔧 Development

#### Backend (FastAPI + SQLAlchemy)
- API endpoints in `backend/routers/`
- Database models in `backend/database/models.py`
- AI services in `backend/services/`

#### Frontend (React + Material-UI)
- Components in `frontend/src/components/`
- Pages in `frontend/src/pages/`
- Services in `frontend/src/services/`

### 📝 Notes

- The application includes fallback AI services if API keys are not provided
- MySQL is the primary database (SQLite fallback available)
- All text interfaces are in English
- Responsive design works on desktop and mobile

### 🐛 Troubleshooting

1. **Database Connection Issues**: Check MySQL service and credentials
2. **Port Conflicts**: Change ports in configuration if needed
3. **API Key Issues**: AI features will use fallback service without keys
4. **Node Modules**: Delete `node_modules` and run `npm install` again

### 📚 Additional Resources

- See `MySQL_Setup_Guide.md` for detailed database setup
- Check `DEPLOYMENT.md` for production deployment
- Review API documentation at http://localhost:8000/docs
