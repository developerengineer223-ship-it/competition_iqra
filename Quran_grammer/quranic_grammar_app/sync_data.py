#!/usr/bin/env python
"""Data synchronization script - Fetch and sync Quran data from APIs to database"""
import os
import sys
import time
from app import create_app, db
from app.services import QuranDataSyncService

# Get app context
app = create_app('development')

def print_status(message, status_type='info'):
    """Print formatted status message"""
    icons = {
        'info': '📊',
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'loading': '🔄'
    }
    icon = icons.get(status_type, '➡️')
    print(f"{icon} {message}")

def sync_surahs():
    """Sync all Surahs"""
    with app.app_context():
        print_status("Starting Surah synchronization...", 'loading')
        try:
            result = QuranDataSyncService.sync_surahs_to_db(db)
            if result:
                print_status("All Surahs synced successfully!", 'success')
                return True
            else:
                print_status("Failed to sync Surahs", 'error')
                return False
        except Exception as e:
            print_status(f"Error syncing Surahs: {str(e)}", 'error')
            return False

def sync_all_ayahs():
    """Sync all Ayahs with translations"""
    with app.app_context():
        print_status("Starting Ayah synchronization for all Surahs...", 'loading')
        print_status("This may take several minutes. Please be patient.", 'info')
        
        success_count = 0
        fail_count = 0
        
        for surah_num in range(1, 115):
            try:
                result = QuranDataSyncService.sync_ayahs_with_translations(db, surah_num)
                if result:
                    success_count += 1
                    print(f"  [{surah_num:>3}/114] ✅ Surah {surah_num}")
                else:
                    fail_count += 1
                    print(f"  [{surah_num:>3}/114] ⚠️  Surah {surah_num} (skipped)")
                
                # Add small delay to avoid overwhelming API
                time.sleep(0.2)
                
            except Exception as e:
                fail_count += 1
                print(f"  [{surah_num:>3}/114] ❌ Surah {surah_num} - {str(e)}")
        
        print_status(f"Ayah synchronization complete!", 'success')
        print_status(f"Success: {success_count}/114, Failed: {fail_count}/114", 'info')
        
        return success_count > 0

def get_db_stats():
    """Get database statistics"""
    with app.app_context():
        from app.models import Surah, Ayah
        
        surah_count = Surah.query.count()
        ayah_count = Ayah.query.count()
        
        print_status("Database Statistics:", 'info')
        print(f"  • Surahs: {surah_count}")
        print(f"  • Ayahs: {ayah_count}")
        
        return surah_count, ayah_count

def main():
    """Main synchronization function"""
    print("\n" + "="*60)
    print("🕌 QURANIC GRAMMAR APP - DATA SYNCHRONIZATION")
    print("="*60 + "\n")
    
    # Show current status
    print_status("Checking current database status...", 'info')
    surah_count, ayah_count = get_db_stats()
    
    print("\n" + "="*60)
    print("OPTIONS:")
    print("  1. Sync only Surahs (names, numbers)")
    print("  2. Sync Ayahs with Translations for ALL Surahs")
    print("  3. Show Database Statistics")
    print("  4. Exit")
    print("="*60 + "\n")
    
    choice = input("Select option (1-4): ").strip()
    
    if choice == '1':
        if sync_surahs():
            print_status("\nSurahs are now loaded. You can view them in the app.", 'success')
        else:
            print_status("\nFailed to sync Surahs.", 'error')
    
    elif choice == '2':
        if sync_all_ayahs():
            print_status("\nAll Ayahs with translations are now loaded!", 'success')
            print_status("Go to the app and click on any Surah to view Ayahs with translations.", 'info')
        else:
            print_status("\nFailed to sync Ayahs.", 'error')
    
    elif choice == '3':
        get_db_stats()
    
    elif choice == '4':
        print_status("Exiting...", 'info')
        sys.exit(0)
    
    else:
        print_status("Invalid option. Please try again.", 'error')
    
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        print_status("Synchronization cancelled by user", 'warning')
        sys.exit(0)
    except Exception as e:
        print_status(f"Unexpected error: {str(e)}", 'error')
        sys.exit(1)
