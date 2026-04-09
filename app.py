from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

# Set template folder explicitly
app = Flask(__name__, template_folder='templates')

# This creates a file named 'quran_data.db' in your project folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quran_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the table structure
class QuranWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    surah = db.Column(db.Integer, nullable=False)
    ayah = db.Column(db.Integer, nullable=False)
    word_index = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(100), nullable=False)
    pos_type = db.Column(db.String(50))  # Noun, Verb, Particle
    root_word = db.Column(db.String(50))

    def __repr__(self):
        return f'<Word {self.text} - {self.pos_type}>'

# Home route: show all words grouped by ayah and stats
@app.route('/')
def index():
    words = QuranWord.query.all()
    # Group words by ayah
    data = {}
    for w in words:
        data.setdefault(w.ayah, []).append({
            'word': w.text,
            'type': w.pos_type,
            'role': w.root_word or '',
            'color': 'blue' if w.pos_type == 'Noun' else ('orange' if w.pos_type == 'Adjective' else 'green')
        })
    # Calculate stats
    stats = {'Nouns': 0, 'Particles': 0, 'Adjectives': 0}
    for w in words:
        if w.pos_type == 'Noun':
            stats['Nouns'] += 1
        elif w.pos_type == 'Adjective':
            stats['Adjectives'] += 1
        else:
            stats['Particles'] += 1
    return render_template('index.html', data=data, stats=stats)

# Recommendation route (returns similar words by pos_type)
@app.route('/recommend/<int:word_id>')
def recommend(word_id):
    word = QuranWord.query.get(word_id)
    if not word:
        return jsonify({'message': 'Word not found'}), 404
    # Find other words with the same pos_type (excluding itself)
    recommendations = QuranWord.query.filter(QuranWord.pos_type == word.pos_type, QuranWord.id != word.id).limit(5).all()
    result = [
        {'id': w.id, 'text': w.text, 'surah': w.surah, 'ayah': w.ayah, 'pos_type': w.pos_type, 'root_word': w.root_word}
        for w in recommendations
    ]
    return jsonify(result)

if __name__ == '__main__':
    # Create DB and add a test word if DB is empty
    if not os.path.exists('quran_data.db'):
        with app.app_context():
            db.create_all()
            test_word = QuranWord(surah=1, ayah=1, word_index=2, text="الله", pos_type="Noun", root_word="a-l-h")
            db.session.add(test_word)
            db.session.commit()
            print("Test word added!")
    app.run(debug=True)