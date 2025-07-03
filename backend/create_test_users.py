#!/usr/bin/env python3
"""
Create test users for different age groups
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import User, UserSettings
from core.security import get_password_hash
from core.age_groups import AgeGroup, AgeGroupConfig
from datetime import date, datetime

def create_test_users():
    """Create test users for each age group"""
    print("🧪 Creating test users for different age groups...")
    
    db = SessionLocal()
    
    try:
        # Test users data with different age groups
        test_users = [
            {
                "username": "preschool_kid",
                "email": "preschool@test.com",
                "full_name": "Little Emma",
                "age_group": AgeGroup.PRESCHOOL.value,
                "birth_date": date(2020, 5, 15),  # 4 years old
                "description": "Preschool child learning basic writing"
            },
            {
                "username": "early_primary",
                "email": "early_primary@test.com", 
                "full_name": "Young Alex",
                "age_group": AgeGroup.EARLY_PRIMARY.value,
                "birth_date": date(2017, 8, 20),  # 7 years old
                "description": "Early primary school student"
            },
            {
                "username": "late_primary",
                "email": "late_primary@test.com",
                "full_name": "Smart Sarah",
                "age_group": AgeGroup.LATE_PRIMARY.value,
                "birth_date": date(2014, 3, 10),  # 10 years old
                "description": "Late primary school student"
            },
            {
                "username": "early_middle",
                "email": "early_middle@test.com",
                "full_name": "Teen Mike",
                "age_group": AgeGroup.EARLY_MIDDLE.value,
                "birth_date": date(2011, 11, 5),  # 13 years old
                "description": "Early middle school student"
            },
            {
                "username": "late_middle",
                "email": "late_middle@test.com",
                "full_name": "Student Lisa",
                "age_group": AgeGroup.LATE_MIDDLE.value,
                "birth_date": date(2008, 7, 25),  # 16 years old
                "description": "Late middle school student"
            },
            {
                "username": "high_school",
                "email": "high_school@test.com",
                "full_name": "Senior David",
                "age_group": AgeGroup.HIGH_SCHOOL.value,
                "birth_date": date(2006, 12, 1),  # 18 years old
                "description": "High school senior"
            }
        ]
        
        created_users = []
        
        for user_data in test_users:
            # Check if user already exists
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
            if existing_user:
                print(f"⚠️  User {user_data['username']} already exists, skipping...")
                continue
            
            # Create new user
            print(f"👤 Creating user: {user_data['username']} ({user_data['description']})")
            
            new_user = User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=get_password_hash("test123"),  # Same password for all test users
                birth_date=user_data["birth_date"],
                age_group=user_data["age_group"],
                is_active=True
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Create default settings for the user
            user_settings = UserSettings(
                user_id=new_user.id,
                theme="light",
                language="en",
                font_size=14,
                auto_save=True,
                ai_settings={}
            )
            
            db.add(user_settings)
            db.commit()
            
            created_users.append({
                "username": new_user.username,
                "age_group": new_user.age_group,
                "age_group_name": AgeGroupConfig.AGE_GROUP_NAMES.get(AgeGroup(new_user.age_group), "Unknown")
            })
            
            print(f"✅ Created user: {new_user.username}")
        
        print(f"\n🎉 Successfully created {len(created_users)} test users!")
        
        if created_users:
            print("\n📋 Test Users Summary:")
            print("=" * 60)
            print(f"{'Username':<15} {'Age Group':<15} {'Description'}")
            print("-" * 60)
            
            for user in created_users:
                print(f"{user['username']:<15} {user['age_group']:<15} {user['age_group_name']}")
            
            print("\n🔑 Login Information:")
            print("- Password for all test users: test123")
            print("- You can now test age-appropriate AI suggestions!")
            
            print("\n💡 Testing Tips:")
            print("1. Login with different age group users")
            print("2. Create writing projects and test AI assistance")
            print("3. Compare AI suggestions across different age groups")
            print("4. Verify that suggestions match the user's developmental stage")
        
    except Exception as e:
        print(f"❌ Error creating test users: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_users()
