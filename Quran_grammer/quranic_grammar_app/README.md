# 🕌 Quranic Grammar Web App

A Flask-based web application for Quranic grammar analysis with MySQL backend.

## Features

- Word-level grammar analysis
- Surah and Ayah browsing
- User authentication
- RESTful API endpoints
- Interactive UI with Arabic RTL support

## Project Structure

```
quranic_grammar_app/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/              # Database models
│   ├── routes/              # Route blueprints
│   │   ├── main.py         # Main routes
│   │   ├── auth.py         # Authentication
│   │   ├── quran.py        # Quran routes
│   │   └── api.py          # API endpoints
│   ├── services/            # Business logic
│   │   └── morphology.py   # Grammar analysis
│   ├── templates/           # Jinja2 templates
│   └── static/              # CSS, JS, images
├── config.py                # Configuration
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Installation & Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
Copy .env.example to .env
Edit .env with your MySQL credentials
```

### 4. Setup MySQL Database

```bash
CREATE DATABASE quran_grammar_db;
```

### 5. Run Application

```bash
python run.py
```

Visit `http://localhost:5000` in your browser.

## API Endpoints

- `GET /api/surahs` - Get all surahs
- `GET /api/surah/<id>/ayahs` - Get ayahs for a surah
- `GET /api/ayah/<id>/words` - Get words for an ayah
- `GET /api/word/<id>/grammar` - Get grammar tags for a word

## Development Phases

1. ✅ Project Setup (COMPLETED)
2. 🔄 MySQL Database Setup
3. 🔄 Flask App Structure
4. 🔄 Quran Data Integration
5. 🔄 Word-Level Grammar System
6. 🔄 UI Development
7. 🔄 Search + Learning Module
8. 🔄 Deployment & Optimization

## License

MIT
