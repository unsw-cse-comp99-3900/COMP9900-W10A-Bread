#!/usr/bin/env python3
"""
Database Migration Script: Update Age Groups
Updates existing age group values from old system to new system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from database.database import engine, SessionLocal
from database.models import User

def migrate_age_groups():
    """Update age group values from old system to new system"""
    print("🔧 Starting age group migration...")

    # Age group mapping from old to new
    age_group_mapping = {
        'preschool': 'early_years',
        'early_primary': 'lower_primary', 
        'late_primary': 'upper_primary',
        'early_middle': 'lower_secondary',
        'late_middle': 'upper_secondary',
        'high_school': 'upper_secondary'
    }

    # Create database connection
    db = SessionLocal()
    
    try:
        # Get all users with old age group values
        users = db.query(User).all()
        updated_count = 0
        
        for user in users:
            if user.age_group and user.age_group in age_group_mapping:
                old_age_group = user.age_group
                new_age_group = age_group_mapping[old_age_group]
                
                print(f"👤 Updating user {user.username}: {old_age_group} → {new_age_group}")
                user.age_group = new_age_group
                updated_count += 1
            elif user.age_group and user.age_group not in age_group_mapping:
                # Check if it's already a new age group value
                new_age_groups = ['early_years', 'lower_primary', 'upper_primary', 'lower_secondary', 'upper_secondary']
                if user.age_group not in new_age_groups:
                    print(f"⚠️  Unknown age group for user {user.username}: {user.age_group}")
                    # Set to default
                    user.age_group = 'upper_primary'
                    updated_count += 1

        # Commit changes
        db.commit()
        print(f"✅ Age group migration completed! Updated {updated_count} users.")

        # Display current age group distribution
        print("\n📊 Current age group distribution:")
        age_group_counts = {}
        for user in db.query(User).all():
            if user.age_group:
                age_group_counts[user.age_group] = age_group_counts.get(user.age_group, 0) + 1
        
        for age_group, count in age_group_counts.items():
            print(f"   - {age_group}: {count} users")

        print("\n💡 New age group system:")
        print("   - early_years: Ages 3-5 (Preschool/Prep)")
        print("   - lower_primary: Ages 6-9 (Year 1-3)")
        print("   - upper_primary: Ages 10-12 (Year 4-6)")
        print("   - lower_secondary: Ages 12-15 (Year 7-9)")
        print("   - upper_secondary: Ages 16-18 (Year 10-12)")

    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate_age_groups()
