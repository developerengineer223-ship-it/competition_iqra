#!/usr/bin/env python
"""Application entry point"""
import os
from app import create_app, db

# Get environment from env variable (default to development)
config_name = os.getenv('FLASK_ENV', 'development')

# Create Flask app instance
app = create_app(config_name)

@app.shell_context_processor
def make_shell_context():
    """Register database and models for shell context"""
    return {'db': db}

if __name__ == '__main__':
    with app.app_context():
        # Verify database tables exist (don't recreate if they exist)
        try:
            # Check if tables exist by querying
            from app.models import User
            User.query.first()
            print("✅ Database and tables already exist")
        except Exception as e:
            # Tables don't exist, create them
            try:
                print("🔧 Creating database tables...")
                db.create_all()
                print("✅ Database tables created successfully")
            except Exception as creation_error:
                print(f"❌ Error creating database: {creation_error}")
                try:
                    # Last resort: drop and recreate
                    print("🔄 Attempting database recovery...")
                    db.drop_all()
                    db.create_all()
                    print("✅ Database recovered and recreated")
                except Exception as recovery_error:
                    print(f"❌ Failed to recover database: {recovery_error}")
    
    # Run the development server
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
