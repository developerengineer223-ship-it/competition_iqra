"""Quran API Service - Fetch Quran data from external APIs"""
import requests
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# API Endpoints
ALQURAN_CLOUD_BASE = "https://api.alquran.cloud/v1"
QURAN_COM_BASE = "https://api.quran.com/api/v4"

class QuranAPIService:
    """Service for fetching Quran data from APIs"""
    
    @staticmethod
    def fetch_all_surahs() -> Optional[List[Dict]]:
        """Fetch all Surahs from Quran Cloud API
        
        Returns:
            List of Surahs with id, number, name, englishName, englishNameTranslation, numberOfAyahs
        """
        try:
            url = f"{ALQURAN_CLOUD_BASE}/surah"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('status') == 'ok':
                return data.get('data', [])
            else:
                logger.error(f"API error: {data.get('message')}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Error fetching Surahs: {str(e)}")
            return None
    
    @staticmethod
    def fetch_surah_ayahs(surah_number: int) -> Optional[List[Dict]]:
        """Fetch all Ayahs for a specific Surah
        
        Args:
            surah_number: Surah number (1-114)
            
        Returns:
            List of Ayahs with number, text, and metadata
        """
        try:
            url = f"{ALQURAN_CLOUD_BASE}/surah/{surah_number}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('status') == 'ok':
                surah_data = data.get('data', {})
                return surah_data.get('ayahs', [])
            else:
                logger.error(f"API error: {data.get('message')}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Error fetching Surah {surah_number}: {str(e)}")
            return None
    
    @staticmethod
    def fetch_translations(surah_number: int) -> Tuple[Optional[List[Dict]], Optional[List[Dict]]]:
        """Fetch English and Urdu translations for a Surah
        
        Args:
            surah_number: Surah number (1-114)
            
        Returns:
            Tuple of (english_translations, urdu_translations)
        """
        try:
            # Fetch English translations (Asad)
            en_url = f"{ALQURAN_CLOUD_BASE}/surah/{surah_number}/en.asad"
            en_response = requests.get(en_url, timeout=10)
            en_response.raise_for_status()
            
            # Fetch Urdu translations (Jalandhry)
            ur_url = f"{ALQURAN_CLOUD_BASE}/surah/{surah_number}/ur.jalandhry"
            ur_response = requests.get(ur_url, timeout=10)
            ur_response.raise_for_status()
            
            en_data = en_response.json()
            ur_data = ur_response.json()
            
            en_ayahs = en_data.get('data', {}).get('ayahs', []) if en_data.get('status') == 'ok' else []
            ur_ayahs = ur_data.get('data', {}).get('ayahs', []) if ur_data.get('status') == 'ok' else []
            
            return en_ayahs, ur_ayahs
            
        except requests.RequestException as e:
            logger.error(f"Error fetching translations for Surah {surah_number}: {str(e)}")
            return None, None
    
    @staticmethod
    def fetch_word_analysis(surah_number: int, ayah_number: int) -> Optional[List[Dict]]:
        """Fetch word-level analysis for a specific Ayah
        
        Args:
            surah_number: Surah number (1-114)
            ayah_number: Ayah number within the Surah
            
        Returns:
            List of words with text, root, lemma, and part_of_speech
        """
        try:
            # Quran.com verse key format is surah:ayah
            verse_key = f"{surah_number}:{ayah_number}"
            
            url = f"{QURAN_COM_BASE}/verses/by_key/{verse_key}"
            params = {
                'words': 'true',
                'word_fields': 'text_uthmani,transliteration,root,lemma,part_of_speech'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'verses' in data and len(data['verses']) > 0:
                verse = data['verses'][0]
                words = verse.get('words', [])
                
                # Extract word data
                word_data = []
                for word in words:
                    word_info = {
                        'text': word.get('text_uthmani', ''),
                        'transliteration': word.get('transliteration', ''),
                        'root': word.get('root', {}),
                        'lemma': word.get('lemma', ''),
                        'part_of_speech': word.get('part_of_speech', '')
                    }
                    word_data.append(word_info)
                
                return word_data if word_data else None
            else:
                logger.warning(f"No verse found for {verse_key}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Error fetching word analysis for {surah_number}:{ayah_number}: {str(e)}")
            return None
    
    @staticmethod
    def fetch_all_ayahs_with_translations(surah_number: int) -> Optional[List[Dict]]:
        """Fetch all Ayahs with translations for a Surah
        
        Args:
            surah_number: Surah number (1-114)
            
        Returns:
            List of Ayahs with Arabic text and translations
        """
        try:
            # Fetch Arabic Ayahs
            ar_url = f"{ALQURAN_CLOUD_BASE}/surah/{surah_number}"
            ar_response = requests.get(ar_url, timeout=10)
            ar_response.raise_for_status()
            ar_data = ar_response.json()
            ar_ayahs = ar_data.get('data', {}).get('ayahs', []) if ar_data.get('status') == 'ok' else []
            
            # Fetch English translations
            en_url = f"{ALQURAN_CLOUD_BASE}/surah/{surah_number}/en.asad"
            en_response = requests.get(en_url, timeout=10)
            en_response.raise_for_status()
            en_data = en_response.json()
            en_ayahs = en_data.get('data', {}).get('ayahs', []) if en_data.get('status') == 'ok' else []
            
            # Fetch Urdu translations
            ur_url = f"{ALQURAN_CLOUD_BASE}/surah/{surah_number}/ur.jalandhry"
            ur_response = requests.get(ur_url, timeout=10)
            ur_response.raise_for_status()
            ur_data = ur_response.json()
            ur_ayahs = ur_data.get('data', {}).get('ayahs', []) if ur_data.get('status') == 'ok' else []
            
            # Combine all data
            combined_ayahs = []
            for i, ar_ayah in enumerate(ar_ayahs):
                en_text = en_ayahs[i].get('text', '') if i < len(en_ayahs) else ''
                ur_text = ur_ayahs[i].get('text', '') if i < len(ur_ayahs) else ''
                
                combined = {
                    'number': ar_ayah.get('number'),
                    'numberInSurah': ar_ayah.get('numberInSurah'),
                    'text_arabic': ar_ayah.get('text', ''),
                    'translation_en': en_text,
                    'translation_ur': ur_text
                }
                combined_ayahs.append(combined)
            
            return combined_ayahs if combined_ayahs else None
            
        except requests.RequestException as e:
            logger.error(f"Error fetching Ayahs with translations for Surah {surah_number}: {str(e)}")
            return None


class QuranDataSyncService:
    """Service for syncing Quran data to database"""
    
    @staticmethod
    def sync_surahs_to_db(db):
        """Fetch all Surahs from API and save to database
        
        Args:
            db: SQLAlchemy database instance
        """
        try:
            from app.models import Surah
            
            # Fetch Surahs from API
            surahs_data = QuranAPIService.fetch_all_surahs()
            
            if not surahs_data:
                logger.error("Failed to fetch Surahs from API")
                return False
            
            # Clear existing Surahs
            Surah.query.delete()
            
            # Add new Surahs
            for surah in surahs_data:
                new_surah = Surah(
                    id=surah.get('number'),
                    name=surah.get('name', ''),
                    name_english=surah.get('englishName', ''),
                    total_ayahs=surah.get('numberOfAyahs', 0)
                )
                db.session.add(new_surah)
            
            db.session.commit()
            logger.info(f"Successfully synced {len(surahs_data)} Surahs to database")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error syncing Surahs to database: {str(e)}")
            return False
    
    @staticmethod
    def sync_ayahs_with_translations(db, surah_number: int) -> bool:
        """Fetch Ayahs with translations and save to database
        
        Args:
            db: SQLAlchemy database instance
            surah_number: Surah number to sync
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from app.models import Ayah
            
            # Fetch combined Ayahs with translations
            ayahs_data = QuranAPIService.fetch_all_ayahs_with_translations(surah_number)
            
            if not ayahs_data:
                logger.error(f"Failed to fetch Ayahs for Surah {surah_number}")
                return False
            
            # Clear existing Ayahs for this Surah
            Ayah.query.filter_by(surah_id=surah_number).delete()
            
            # Add new Ayahs
            for ayah in ayahs_data:
                new_ayah = Ayah(
                    surah_id=surah_number,
                    ayah_number=ayah.get('numberInSurah'),
                    text_arabic=ayah.get('text_arabic', ''),
                    translation_en=ayah.get('translation_en', ''),
                    translation_ur=ayah.get('translation_ur', '')
                )
                db.session.add(new_ayah)
            
            db.session.commit()
            logger.info(f"Successfully synced {len(ayahs_data)} Ayahs for Surah {surah_number}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error syncing Ayahs for Surah {surah_number}: {str(e)}")
            return False


__all__ = ['QuranAPIService', 'QuranDataSyncService']
