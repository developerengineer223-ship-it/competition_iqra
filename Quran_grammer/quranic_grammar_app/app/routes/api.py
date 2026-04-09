"""API routes blueprint for JSON endpoints"""
from flask import Blueprint, jsonify
from app.models import Surah, Ayah, Word, GrammarTag

api_bp = Blueprint('api', __name__)

@api_bp.route('/surahs', methods=['GET'])
def get_surahs():
    """Get all surahs as JSON"""
    all_surahs = Surah.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'total_ayahs': s.total_ayahs
    } for s in all_surahs])

@api_bp.route('/surah/<int:surah_id>/ayahs', methods=['GET'])
def get_ayahs(surah_id):
    """Get ayahs for a surah"""
    ayahs = Ayah.query.filter_by(surah_id=surah_id).all()
    return jsonify([{
        'id': a.id,
        'ayah_number': a.ayah_number,
        'text_arabic': a.text_arabic,
        'translation': a.translation
    } for a in ayahs])

@api_bp.route('/ayah/<int:ayah_id>/words', methods=['GET'])
def get_words(ayah_id):
    """Get words for an ayah"""
    words = Word.query.filter_by(ayah_id=ayah_id).order_by(Word.position).all()
    return jsonify([{
        'id': w.id,
        'word_text': w.word_text,
        'root': w.root,
        'word_type': w.word_type,
        'position': w.position,
        'tags': [{'tag_type': t.tag_type, 'description': t.description} for t in w.grammar_tags]
    } for w in words])

@api_bp.route('/word/<int:word_id>/grammar', methods=['GET'])
def get_word_grammar(word_id):
    """Get grammar tags for a word"""
    word = Word.query.get_or_404(word_id)
    return jsonify({
        'word_text': word.word_text,
        'root': word.root,
        'word_type': word.word_type,
        'tags': [{'tag_type': t.tag_type, 'description': t.description} for t in word.grammar_tags]
    })
