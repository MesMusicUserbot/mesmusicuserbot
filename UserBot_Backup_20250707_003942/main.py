from telethon import TelegramClient
import asyncio
import threading
import logging

# Telethon log seviyyəsini azalt
logging.getLogger('telethon').setLevel(logging.WARNING)

# Log server və fayl meneceri import et
from Menim_PY_modullarim.log_server import add_log, set_bot_status, start_log_server
from Menim_PY_modullarim.file_manager import create_py_file

# Modulları import et
from Menim_PY_modullarim import (
    tag_commands, entertainment_commands, cosmic_commands, 
    profile_commands, profanity_filter, sticker_blocker, 
    link_filter, ai_commands, music_player, system_commands, 
    automatic_functions, group_activation, zip_creator,
    log_server, cleanup_old_folders
)

# Environment variables
import os
from dotenv import load_dotenv

# .env faylını yüklə
load_dotenv()

# Telegram API məlumatları
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
phone = os.getenv('PHONE')
password = os.getenv('PASSWORD')

# Session qovluğunu yarat və icazələri təyin et
session_dir = 'Menim_SESSION_fayillarim'
if not os.path.exists(session_dir):
    os.makedirs(session_dir, mode=0o755)

# Session faylının icazələrini yoxla və düzəlt
session_path = os.path.join(session_dir, 'userbot_session')
try:
    if os.path.exists(f"{session_path}.session"):
        os.chmod(f"{session_path}.session", 0o644)
except:
    pass

client = TelegramClient(session_path, api_id, api_hash)

async def main():
    """Ana funksiya"""
    try:
        add_log("🚀 Userbot başladı", "info")

        # Bot status aktiv et
        set_bot_status(True)

        # Köhnə qovluqları təmizlə
        cleanup_old_folders.cleanup_old_folders()

        # JSON qovluğunu yarat
        json_folder = "Menim_JSON_fayillarim"
        if not os.path.exists(json_folder):
            os.makedirs(json_folder, mode=0o755)
            add_log("✅ JSON qovluğunun icazələri təyin edildi", "success")

        # Telethon client-i başlat
        await client.start(phone=phone, password=password)
        add_log("✅ Userbot avtorizasiyası tamamlandı", "success")

        print("📋 Əmr handler-ləri qeydiyyata alınır...")
        add_log("📋 Modullar yüklənməyə başladı", "info")

        # Modulları qeydiyyata al
        tag_commands.register_tag_handlers(client)
        add_log("✅ TAĞ ƏMRLƏRİ yükləndi", "success")
        print("✅ TAĞ ƏMRLƏRİ yükləndi")

        entertainment_commands.register_entertainment_handlers(client)
        add_log("✅ ƏYLƏNCƏ ƏMRLƏRİ yükləndi", "success")
        print("✅ ƏYLƏNCƏ ƏMRLƏRİ yükləndi")

        cosmic_commands.register_cosmic_handlers(client)
        add_log("✅ KOSMIK ƏMRLƏRİ yükləndi", "success")
        print("✅ KOSMIK ƏMRLƏRİ yükləndi")

        profile_commands.register_profile_handlers(client)
        add_log("✅ PROFİL ƏMRLƏRİ yükləndi", "success")
        print("✅ PROFİL ƏMRLƏRİ yükləndi")

        profanity_filter.register_profanity_handlers(client)
        add_log("✅ SÖYÜŞ FİLTRİ yükləndi", "success")
        print("✅ SÖYÜŞ FİLTRİ yükləndi")

        sticker_blocker.register_sticker_handlers(client)
        add_log("✅ STİKER BLOKLAMA yükləndi", "success")
        print("✅ STİKER BLOKLAMA yükləndi")

        link_filter.register_link_handlers(client)
        add_log("✅ LİNK FİLTRİ yükləndi", "success")
        print("✅ LİNK FİLTRİ yükləndi")

        ai_commands.register_ai_handlers(client)
        add_log("✅ AI ƏMRLƏRİ yükləndi", "success")
        print("✅ AI ƏMRLƏRİ yükləndi")

        music_player.register_music_handlers(client)
        add_log("✅ MUSİQİ SİSTEMİ yükləndi", "success")
        print("✅ MUSİQİ SİSTEMİ yükləndi")

        system_commands.register_system_handlers(client)
        add_log("✅ SİSTEM ƏMRLƏRİ yükləndi", "success")
        print("✅ SİSTEM ƏMRLƏRİ yükləndi")

        automatic_functions.register_automatic_handlers(client)
        add_log("✅ AVTOMATIK FUNKSIYALAR yükləndi", "success")
        print("✅ AVTOMATIK FUNKSIYALAR yükləndi")

        group_activation.register_group_handlers(client)
        add_log("✅ QRUP AKTİVLƏŞDİRMƏ SİSTEMİ yükləndi", "success")
        print("✅ QRUP AKTİVLƏŞDİRMƏ SİSTEMİ yükləndi")

        # ZIP handler-lərini qeydiyyata al - bu əsas düzəliş
        zip_creator.register_handlers(client)
        add_log("✅ ZIP YARADMA SİSTEMİ yükləndi", "success")
        print("✅ ZIP YARADMA SİSTEMİ yükləndi")

        # Qrup aktivləşdirmə məlumatlarını yüklə
        await group_activation.initialize_group_activation_system()

        add_log("🎉 Bütün modullar yükləndi - Bot tamamilə hazırdır!", "success")
        print("\n🎉 Bütün modullar uğurla yükləndi və bot hazırdır!")

        # Modul siyahısını göstər
        print("\n📋 Mövcud modullar:")
        modules = [
            "🏷️ TAĞ ƏMRLƏRİ",
            "🔮 ƏYLƏNCƏ ƏMRLƏRİ", 
            "🚀 KOSMIK ƏMRLƏRİ",
            "👤 PROFİL ƏMRLƏRİ",
            "🛡️ SÖYÜŞ FİLTRİ",
            "🔒 STİKER BLOKLAMA",
            "🔗 LİNK FİLTRİ",
            "🤖 AI ƏMRLƏRİ",
            "🎵 MUSİQİ SİSTEMİ",
            "ℹ️ SİSTEM ƏMRLƏRİ",
            "🔄 AVTOMATIK FUNKSIYALAR",
            "ℹ️ QRUP AKTİVLƏŞDİRMƏ SİSTEMİ",
            "📦 ZIP YARADMA SİSTEMİ"
        ]

        for i, module in enumerate(modules, 1):
            print(f"   {i:2}. {module}")

        # Log serveri məlumatı
        add_log("🌐 Log serveri: Məxfi Server Portu", "info")
        print("\n🌐 Log serveri: Məxfi Server Portu")

        # Bot-u işlək vəziyyətdə saxla
        await client.run_until_disconnected()

    except Exception as e:
        add_log(f"❌ Kritik xəta: {str(e)}", "error")
        print(f"❌ Kritik xəta: {str(e)}")

if __name__ == '__main__':
    print("Userbot işə hazırdır...")

    # Log serverini başlat
    threading.Thread(target=start_log_server, daemon=True).start()

    # Ana funksiyani çalışdır
    asyncio.run(main())