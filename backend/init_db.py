#!/usr/bin/env python3
"""
Database initialization script for Writingway
Creates tables and adds a default admin user
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database.database import engine, SessionLocal
from database.models import Base, User, UserSettings
from core.security import get_password_hash

def init_database():
    """Initialize the database with tables and default data"""
    print("🔧 Initializing Writingway database...")
    
    # Create all tables
    print("📊 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
    
    # Create a session
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("⚠️  Admin user already exists!")
            print(f"   Username: admin")
            print(f"   Email: {existing_user.email}")
            return
        
        # Create default admin user
        print("👤 Creating default admin user...")
        admin_user = User(
            username="admin",
            email="admin@writingway.com",
            full_name="Administrator",
            hashed_password=get_password_hash("admin123"),
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        # Create default settings for admin user
        print("⚙️  Creating default user settings...")
        admin_settings = UserSettings(
            user_id=admin_user.id,
            theme="light",
            language="en",
            font_size=14,
            auto_save=True,
            ai_settings={}
        )
        
        db.add(admin_settings)
        db.commit()
        
        print("🎉 Database initialization completed successfully!")
        print("")
        print("📝 Default Login Credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Email: admin@writingway.com")
        print("")
        print("🔒 Please change the default password after first login!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_demo_user():
    """Create a demo user for testing"""
    db = SessionLocal()
    
    try:
        # Check if demo user already exists
        existing_user = db.query(User).filter(User.username == "demo").first()
        if existing_user:
            print("⚠️  Demo user already exists!")
            return
        
        print("👤 Creating demo user...")
        demo_user = User(
            username="demo",
            email="demo@writingway.com",
            full_name="Demo User",
            hashed_password=get_password_hash("demo123"),
            is_active=True
        )
        
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        
        # Create settings for demo user
        demo_settings = UserSettings(
            user_id=demo_user.id,
            theme="light",
            language="en",
            font_size=14,
            auto_save=True,
            ai_settings={}
        )
        
        db.add(demo_settings)
        db.commit()
        
        print("✅ Demo user created successfully!")
        print("   Username: demo")
        print("   Password: demo123")
        
    except Exception as e:
        print(f"❌ Error creating demo user: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Writingway Database Setup")
    print("=" * 40)
    
    try:
        init_database()
        create_demo_user()
        
        print("")
        print("🎯 Next Steps:")
        print("1. Open http://localhost:3000 in your browser")
        print("2. Use the login credentials above")
        print("3. Start creating your writing projects!")
        print("")
        
    except Exception as e:
        print(f"💥 Setup failed: {e}")
        sys.exit(1)
