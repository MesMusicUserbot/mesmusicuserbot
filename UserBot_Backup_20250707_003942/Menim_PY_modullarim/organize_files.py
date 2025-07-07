

import os
import shutil

def organize_files():
    """Faylları müvafiq qovluqlara təşkil edir"""
    
    # 1. Menim_METN_fayillarim qovluğunu yarat
    metn_folder = "Menim_METN_fayillarim"
    if not os.path.exists(metn_folder):
        os.makedirs(metn_folder)
        print(f"✅ {metn_folder} qovluğu yaradıldı")
    
    # Marker faylını köçür
    marker_file = "Menim_JSON_fayillarim_DELETED_DO_NOT_CREATE"
    if os.path.exists(marker_file):
        shutil.move(marker_file, os.path.join(metn_folder, marker_file))
        print(f"✅ {marker_file} köçürüldü")
    
    # 2. Menim_SESSION_fayillarim qovluğunu yarat
    session_folder = "Menim_SESSION_fayillarim"
    if not os.path.exists(session_folder):
        os.makedirs(session_folder)
        print(f"✅ {session_folder} qovluğu yaradıldı")
    
    # Session fayllarını köçür
    session_files = [
        "userbot_session.session",
        "userbot_session.session-journal"
    ]
    
    for file in session_files:
        if os.path.exists(file):
            shutil.move(file, os.path.join(session_folder, file))
            print(f"✅ {file} köçürüldü")
    
    print("🎉 Bütün fayllar uğurla təşkil edildi!")

if __name__ == "__main__":
    organize_files()
