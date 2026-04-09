"""Morphology and grammar service"""

class MorphologyService:
    """Service for word-level morphological analysis"""
    
    @staticmethod
    def split_ayah_into_words(ayah_text):
        """Split ayah text into individual words"""
        words = ayah_text.split()
        return [w.strip() for w in words if w.strip()]
    
    @staticmethod
    def detect_word_type(word):
        """Detect word type (noun, verb, particle, etc.)"""
        # Placeholder for future implementation
        # This would use Arabic morphology analysis
        return 'noun'
    
    @staticmethod
    def extract_root(word):
        """Extract root from word"""
        # Placeholder for future implementation
        # This would extract 3-letter Arabic root
        return word[:3] if len(word) >= 3 else word
    
    @staticmethod
    def analyze_word(word_text):
        """Comprehensive word analysis"""
        return {
            'word': word_text,
            'root': MorphologyService.extract_root(word_text),
            'word_type': MorphologyService.detect_word_type(word_text),
            'tags': []
        }
