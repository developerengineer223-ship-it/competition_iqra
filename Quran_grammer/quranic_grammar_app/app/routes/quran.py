"""Quran routes blueprint"""
from flask import Blueprint, render_template, abort, flash, redirect, url_for
from app.models import Surah, Ayah

quran_bp = Blueprint('quran', __name__)

@quran_bp.route('/surahs')
def surahs():
    """Display all surahs"""
    try:
        all_surahs = Surah.query.all()
        return render_template('surahs.html', surahs=all_surahs, title='Surahs')
    except Exception as e:
        flash(f'سورتیں لوڈ کرنے میں خرابی | Error loading surahs: {str(e)}', 'danger')
        return redirect(url_for('main.index'))

@quran_bp.route('/surah/<int:surah_id>')
def surah(surah_id):
    """Display single surah with all ayahs"""
    try:
        surah_obj = Surah.query.get_or_404(surah_id)
        ayahs = Ayah.query.filter_by(surah_id=surah_id).all()
        return render_template('surah.html', surah=surah_obj, ayahs=ayahs, title=surah_obj.name)
    except Exception as e:
        flash(f'سورت لوڈ کرنے میں خرابی | Error loading surah: {str(e)}', 'danger')
        return redirect(url_for('quran.surahs'))

@quran_bp.route('/ayah/<int:ayah_id>')
def ayah(ayah_id):
    """Display single ayah with word-level analysis"""
    try:
        ayah_obj = Ayah.query.get_or_404(ayah_id)
        return render_template('ayah.html', ayah=ayah_obj, title=f'Ayah {ayah_obj.ayah_number}')
    except Exception as e:
        flash(f'آیت لوڈ کرنے میں خرابی | Error loading ayah: {str(e)}', 'danger')
        return redirect(url_for('main.index'))
