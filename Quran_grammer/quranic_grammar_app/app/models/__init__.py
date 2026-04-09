"""Database models"""
from flask_login import UserMixin
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    language_preference = db.Column(db.String(5), default='en', nullable=False)  # 'en' for English, 'ur' for Urdu
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Hash password before storing"""
        self.password = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Surah(db.Model):
    """Surah model"""
    __tablename__ = 'surahs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    name_english = db.Column(db.String(100), nullable=True)  # English transliteration
    total_ayahs = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    ayahs = db.relationship('Ayah', backref='surah', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Surah {self.name}>'

class Ayah(db.Model):
    """Ayah model"""
    __tablename__ = 'ayahs'
    
    id = db.Column(db.Integer, primary_key=True)
    surah_id = db.Column(db.Integer, db.ForeignKey('surahs.id'), nullable=False, index=True)
    ayah_number = db.Column(db.Integer, nullable=False)
    text_arabic = db.Column(db.Text, nullable=False)
    translation_en = db.Column(db.Text, nullable=True)  # English translation
    translation_ur = db.Column(db.Text, nullable=True)  # Urdu translation
    translation = db.Column(db.Text, nullable=True)  # Legacy field for backward compatibility
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    words = db.relationship('Word', backref='ayah', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Ayah {self.surah_id}:{self.ayah_number}>'

class Word(db.Model):
    """Word model for word-level analysis"""
    __tablename__ = 'words'
    
    id = db.Column(db.Integer, primary_key=True)
    ayah_id = db.Column(db.Integer, db.ForeignKey('ayahs.id'), nullable=False, index=True)
    word_text = db.Column(db.String(100), nullable=False)
    root = db.Column(db.String(20), nullable=True)
    word_type = db.Column(db.String(50), nullable=True)
    position = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    grammar_tags = db.relationship('GrammarTag', backref='word', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Word {self.word_text}>'

class GrammarTag(db.Model):
    """Grammar tag model for word annotations"""
    __tablename__ = 'grammar_tags'
    
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False, index=True)
    tag_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<GrammarTag {self.tag_type}>'
