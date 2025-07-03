#!/usr/bin/env python3
"""
Database Migration Script: Add Age-Related Fields
Adds birth_date and age_group fields to existing users table
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from database.database import engine, SessionLocal
from database.models import User
from core.age_groups import AgeGroupConfig

def migrate_add_age_fields():
    """Add age-related fields to users table"""
    print("🔧 Starting database migration: Adding age fields...")

    # Create database connection
    db = SessionLocal()

    try:
        # Check if fields already exist
        result = db.execute(text("DESCRIBE users"))
        columns = [row[0] for row in result.fetchall()]

        # Add birth_date field
        if 'birth_date' not in columns:
            print("📅 Adding birth_date field...")
            db.execute(text("ALTER TABLE users ADD COLUMN birth_date DATE NULL"))
            print("✅ birth_date field added successfully")
        else:
            print("⚠️  birth_date field already exists")

        # Add age_group field
        if 'age_group' not in columns:
            print("👥 Adding age_group field...")
            db.execute(text("ALTER TABLE users ADD COLUMN age_group VARCHAR(20) NULL"))
            print("✅ age_group field added successfully")
        else:
            print("⚠️  age_group field already exists")

        # Commit changes
        db.commit()
        print("✅ Database migration completed!")

        # Display available age groups
        print("\n📊 Available age groups:")
        age_groups = AgeGroupConfig.get_all_age_groups()
        for group in age_groups:
            print(f"   - {group['name']}: {group['value']}")

        print("\n💡 Tips:")
        print("   - Users can select age groups in registration or settings page")
        print("   - System will provide appropriate AI suggestions based on age group")
        print("   - If birth date is set, system will automatically calculate age group")

    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_add_age_fields()
