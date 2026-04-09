#!/usr/bin/env python
"""
Database initialization script
This script properly initializes the database with the correct schema
"""
import os
import sys
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

def init_database():
    """Initialize database with fresh schema"""
    print("🔧 Initializing database...")
    
    try:
        # Import after path is set
        from app import create_app, db
        
        # Create app context
        app = create_app('development')
        
        with app.app_context():
            # Drop all tables first (fresh start)
            print("🗑️  Dropping all existing tables...")
            db.drop_all()
            
            # Create all tables with new schema
            print("📝 Creating new tables with correct schema...")
            db.create_all()
            
            # Verify tables were created
            from app.models import User, Surah, Ayah, Word, GrammarTag
            
            print("✅ Database initialized successfully!")
            print("📊 Tables created:")
            print("   ✓ users (with language_preference column)")
            print("   ✓ surahs")
            print("   ✓ ayahs")
            print("   ✓ words")
            print("   ✓ grammar_tags")
            
            return True
            
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)
