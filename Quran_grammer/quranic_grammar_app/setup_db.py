#!/usr/bin/env python
"""
Database setup and initialization script for Quranic Grammar App
"""
import os
import sys
from run import create_app

def init_database():
    """Initialize the database"""
    
    # Get the application instance
    app = create_app()
    
    with app.app_context():
        # Print database info
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"\n{'='*60}")
        print(f"🔧 Quranic Grammar App - Database Setup")
        print(f"{'='*60}")
        print(f"\n📦 Database URI: {db_uri}")
        
        # Import db and models
        from app import db
        from app.models import User, Surah, Ayah, Word, GrammarTag
        
        try:
            # Create all tables
            print("\n📋 Creating database tables...")
            db.create_all()
            print("✅ All tables created successfully!")
            
            # Print summary
            print(f"\n📊 Database Summary:")
            print(f"   • Users table: created")
            print(f"   • Surahs table: created")
            print(f"   • Ayahs table: created")
            print(f"   • Words table: created")
            print(f"   • Grammar Tags table: created")
            
            # Check for existing data
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"\n✓ Total tables in database: {len(tables)}")
            print(f"  Tables: {', '.join(tables)}")
            
            print(f"\n{'='*60}")
            print("✨ Database initialized successfully!")
            print(f"{'='*60}\n")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error during database initialization:")
            print(f"   {type(e).__name__}: {str(e)}")
            print(f"{'='*60}\n")
            return False

def reset_database():
    """Drop all tables and reinitialize"""
    
    app = create_app()
    
    with app.app_context():
        from app import db
        
        print(f"\n{'='*60}")
        print("⚠️  Resetting Database - This will DELETE all data!")
        print(f"{'='*60}\n")
        
        confirm = input("Are you sure? Type 'YES' to confirm: ").strip().upper()
        
        if confirm == 'YES':
            try:
                print("\n🗑️  Dropping all tables...")
                db.drop_all()
                print("✅ All tables dropped!")
                
                print("\n🔨 Recreating tables...")
                db.create_all()
                print("✅ All tables recreated!")
                
                print(f"\n{'='*60}")
                print("✨ Database reset successfully!")
                print(f"{'='*60}\n")
                return True
            except Exception as e:
                print(f"\n❌ Error during database reset:")
                print(f"   {type(e).__name__}: {str(e)}")
                return False
        else:
            print("\n⏸️  Reset cancelled.\n")
            return False

if __name__ == '__main__':
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'init':
            success = init_database()
            sys.exit(0 if success else 1)
        elif command == 'reset':
            success = reset_database()
            sys.exit(0 if success else 1)
        else:
            print(f"Unknown command: {command}")
            print("\nUsage:")
            print("  python setup_db.py init   - Initialize/create database")
            print("  python setup_db.py reset  - Reset database (WARNING: deletes all data)")
            sys.exit(1)
    else:
        # Default: initialize
        success = init_database()
        sys.exit(0 if success else 1)
