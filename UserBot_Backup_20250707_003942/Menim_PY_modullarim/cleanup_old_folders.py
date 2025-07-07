
import os
import shutil
import stat

def cleanup_old_folders():
    """Köhnə qovluqları təmizləyir və yaranmasını qarşısını alır"""
    old_folders = [
        "Menim_JSON_fayillarim",
        "mənim JSON fayıllarım", 
        "Mənim json fayıllarım",
        "Mənim JSON fayıllarım",
        "mənim json fayıllarım"
    ]

    for folder in old_folders:
        if os.path.exists(folder):
            try:
                # Əvvəlcə bütün faylları yazıla bilər et
                def make_writable(path):
                    try:
                        os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
                    except:
                        pass

                # Qovluqdakı bütün faylları yazıla bilər et
                if os.path.isdir(folder):
                    for root, dirs, files in os.walk(folder):
                        for d in dirs:
                            make_writable(os.path.join(root, d))
                        for f in files:
                            make_writable(os.path.join(root, f))
                    make_writable(folder)

                # Qovluğu tamamilə sil
                if os.path.isdir(folder):
                    shutil.rmtree(folder, ignore_errors=True)
                    print(f"🗑️ Köhnə qovluq silindi: {folder}")
                else:
                    os.remove(folder)
                    print(f"🗑️ Köhnə fayl silindi: {folder}")

            except Exception as e:
                print(f"❌ Qovluq silinərkən xəta: {folder} - {e}")
                # Daha radikal yanaşma
                try:
                    if os.path.exists(folder):
                        # Sistemdən zorla sil
                        import subprocess
                        result = subprocess.run(['rm', '-rf', folder], capture_output=True)
                        if result.returncode == 0:
                            print(f"🗑️ Sistem əmri ilə silindi: {folder}")
                        else:
                            print(f"❌ Sistem əmri də uğursuz: {folder}")
                except Exception as e2:
                    print(f"❌ Sistem əmri xətası: {e2}")

    # Əmin olmaq üçün Menim_JSON_fayillarim qovluğunu yarad
    if not os.path.exists("Menim_JSON_fayillarim"):
        os.makedirs("Menim_JSON_fayillarim", mode=0o755)
        print("✅ Yeni JSON qovluğu yaradıldı: Menim_JSON_fayillarim")

    # Qovluğun icazələrini düzgün təyin et
    try:
        os.chmod("Menim_JSON_fayillarim", 0o755)
        print("✅ JSON qovluğunun icazələri təyin edildi")
    except Exception as e:
        print(f"❌ JSON qovluq icazələri təyin edilərkən xəta: {e}")
