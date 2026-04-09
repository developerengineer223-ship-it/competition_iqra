#!/usr/bin/env python
"""
Database schema verification script
"""
import os
import sys
from pathlib import Path

app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

def verify_database():
    """Verify database schema is correct"""
    print("🔍 Verifying database schema...")
    
    try:
        from app import create_app, db
        from sqlalchemy import inspect
        
        app = create_app('development')
        
        with app.app_context():
            inspector = inspect(db.engine)
            
            # Check if users table exists
            if 'users' not in inspector.get_table_names():
                print("❌ users table does not exist!")
                return False
            
            # Get columns from users table
            columns = [col['name'] for col in inspector.get_columns('users')]
            print(f"✅ users table columns: {columns}")
            
            # Verify required columns exist
            required_columns = ['id', 'username', 'email', 'password', 'language_preference', 'created_at']
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                print(f"❌ Missing columns: {missing_columns}")
                return False
            
            print("✅ All required columns exist!")
            return True
            
    except Exception as e:
        print(f"❌ Error verifying database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = verify_database()
    sys.exit(0 if success else 1)
