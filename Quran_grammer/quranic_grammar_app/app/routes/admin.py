"""Admin and data management routes"""
from flask import Blueprint, jsonify, redirect, url_for, flash
from app import db
from app.services import QuranDataSyncService

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/sync-data', methods=['GET', 'POST'])
def sync_data():
    """Sync Quran data from API to database"""
    try:
        # Sync all Surahs
        surahs_result = QuranDataSyncService.sync_surahs_to_db(db)
        
        if not surahs_result:
            flash('سورتیں ڈاؤن لوڈ میں خرابی | Failed to sync Surahs', 'danger')
            return redirect(url_for('main.index'))
        
        flash('تمام سورتیں کامیابی سے ڈاؤن لوڈ ہو گئیں | All Surahs synced successfully', 'success')
        return redirect(url_for('main.index'))
    
    except Exception as e:
        flash(f'ڈیٹا سنک میں خرابی | Error syncing data: {str(e)}', 'danger')
        return redirect(url_for('main.index'))

@admin_bp.route('/sync-surah/<int:surah_number>', methods=['GET', 'POST'])
def sync_surah(surah_number):
    """Sync a specific Surah with translations"""
    try:
        if surah_number < 1 or surah_number > 114:
            flash('غلط سورت نمبر | Invalid Surah number', 'danger')
            return redirect(url_for('quran.surahs'))
        
        result = QuranDataSyncService.sync_ayahs_with_translations(db, surah_number)
        
        if not result:
            flash(f'سورت {surah_number} کو ڈاؤن لوڈ کرنے میں خرابی | Failed to sync Surah {surah_number}', 'danger')
            return redirect(url_for('quran.surahs'))
        
        flash(f'سورت {surah_number} کامیابی سے ڈاؤن لوڈ ہو گیا | Surah {surah_number} synced successfully', 'success')
        return redirect(url_for('quran.surah', surah_id=surah_number))
    
    except Exception as e:
        flash(f'سورت سنک میں خرابی | Error syncing surah: {str(e)}', 'danger')
        return redirect(url_for('quran.surahs'))

@admin_bp.route('/sync-all-ayahs', methods=['GET', 'POST'])
def sync_all_ayahs():
    """Sync all Ayahs with translations for all Surahs"""
    try:
        success_count = 0
        fail_count = 0
        
        # Iterate through all 114 Surahs
        for surah_num in range(1, 115):
            result = QuranDataSyncService.sync_ayahs_with_translations(db, surah_num)
            if result:
                success_count += 1
            else:
                fail_count += 1
        
        flash(f'کامیاب: {success_count}, ناکام: {fail_count} | Synced: {success_count} Surahs, Failed: {fail_count}', 'info')
        return redirect(url_for('main.index'))
    
    except Exception as e:
        flash(f'بڑی تبدیلی میں خرابی | Error syncing all: {str(e)}', 'danger')
        return redirect(url_for('main.index'))

@admin_bp.route('/status')
def status():
    """Get data sync status"""
    try:
        from app.models import Surah, Ayah
        
        surah_count = Surah.query.count()
        ayah_count = Ayah.query.count()
        
        return jsonify({
            'status': 'ok',
            'surahs': surah_count,
            'ayahs': ayah_count,
            'message': f'{surah_count} Surahs, {ayah_count} Ayahs in database'
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
