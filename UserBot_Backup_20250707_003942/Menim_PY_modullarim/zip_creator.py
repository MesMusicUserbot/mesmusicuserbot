"""Layihəni ZIP arxivə çevirən modul

Bu modul bütün layihə qovluqlarını və fayllarını zip arxivə yığır.
"""

import os
import zipfile
import datetime
from pathlib import Path
from telethon import events
from .log_server import add_log
from .group_activation import is_userbot_active_in_group

MESHEDI_ID = 5257767076

def create_project_zip():
    """Bütün layihəni zip arxivə çevirir"""

    # Zip faylının adı və tarixi
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"UserBot_Backup_{timestamp}.zip"

    # Zip faylını yaradırıq
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:

        # Bütün qovluqları və faylları gəzirik
        for root, dirs, files in os.walk("."):
            # Bəzi qovluqları istisna edirik
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                # Bəzi faylları istisna edirik
                if file.endswith(('.pyc', '.pyo', '.log')) or file.startswith('.'):
                    continue

                file_path = os.path.join(root, file)

                # Zip faylının özünü əlavə etmirik
                if file == zip_filename:
                    continue

                # Faylı zip-ə əlavə edirik
                arcname = os.path.relpath(file_path, '.')
                zipf.write(file_path, arcname)
                print(f"📁 Əlavə edildi: {arcname}")

    # Zip faylının məlumatlarını göstəririk
    zip_size = os.path.getsize(zip_filename)
    zip_size_mb = zip_size / (1024 * 1024)

    print(f"\n🎉 ZIP arxiv uğurla yaradıldı!")
    print(f"📦 Fayl adı: {zip_filename}")
    print(f"📊 Həcm: {zip_size_mb:.2f} MB")
    print(f"📍 Yerləşdirmə: {os.path.abspath(zip_filename)}")

    return zip_filename

def list_zip_contents(zip_filename):
    """ZIP arxivinin məzmununu göstərir"""

    if not os.path.exists(zip_filename):
        print(f"❌ ZIP fayl tapılmadı: {zip_filename}")
        return

    with zipfile.ZipFile(zip_filename, 'r') as zipf:
        file_list = zipf.namelist()

        print(f"\n📋 ZIP arxivinin məzmunu ({len(file_list)} fayl):")
        print("-" * 50)

        # Qovluqları qruplaşdırırıq
        folders = {}
        for file_path in file_list:
            folder = os.path.dirname(file_path)
            if folder not in folders:
                folders[folder] = []
            folders[folder].append(os.path.basename(file_path))

        for folder, files in sorted(folders.items()):
            if folder == '':
                folder = '📁 Kök qovluq'
            else:
                folder = f"📁 {folder}"

            print(f"\n{folder}:")
            for file in sorted(files):
                print(f"  📄 {file}")

def register_handlers(client):
    """ZIP yaradma handler-lərini qeydiyyata alır"""

    from telethon import events

    @client.on(events.NewMessage(pattern=r"^\.zipyarat$"))
    async def create_zip_command(event):
        """Layihəni zip arxivə çevirir"""
        await event.delete()
        
        add_log("📦 .zipyarat əmri çağırıldı", "info")
        
        # Yalnız Məşədi işlədə bilər
        sender = await event.get_sender()
        MESHEDI_ID = 5257767076  # Məşədi ID

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            add_log(f"❌ Yanlış istifadəçi ZIP əmri işlətdi: {sender.id}", "warning")
            return

        try:
            await event.reply("📦 ZIP arxiv yaradılır, gözləyin...")

            # ZIP yaradırıq
            zip_filename = create_project_zip()

            # Uğurlu mesaj
            await event.reply(f"✅ **ZIP arxiv hazırdır!**\n\n"
                            f"📦 **Fayl adı:** `{zip_filename}`\n"
                            f"📊 **Həcm:** {os.path.getsize(zip_filename) / (1024 * 1024):.2f} MB\n"
                            f"📍 **Yol:** `{os.path.abspath(zip_filename)}`\n\n"
                            f"💡 **Məsləhət:** Faylı yükləmək üçün fayl menecerindən istifadə edin.",
                            parse_mode='markdown')
            
            add_log(f"✅ ZIP arxiv yaradıldı: {zip_filename}", "success")

        except Exception as e:
            await event.reply(f"❌ **ZIP yaradılarkən xəta:**\n```\n{str(e)}\n```", parse_mode='markdown')

    @client.on(events.NewMessage(pattern=r"^\.ziplist$"))
    async def list_zip_command(event):
        """ZIP arxivinin məzmununu göstərir"""
        await event.delete()

        # Yalnız Məşədi işlədə bilər
        sender = await event.get_sender()
        MESHEDI_ID = 5257767076

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            return

        # Son yaradılan ZIP faylını tapırıq
        zip_files = [f for f in os.listdir('.') if f.startswith('UserBot_Backup_') and f.endswith('.zip')]

        if not zip_files:
            await event.reply("❌ Heç bir ZIP arxiv tapılmadı. Əvvəlcə `.zipyarat` əmri ilə yaradın.")
            return

        # Ən yeni ZIP faylını seçirik
        latest_zip = max(zip_files, key=lambda f: os.path.getmtime(f))

        try:
            with zipfile.ZipFile(latest_zip, 'r') as zipf:
                file_list = zipf.namelist()

                # Qısa məlumat
                response = f"📋 **ZIP Arxiv Məzmunu**\n\n"
                response += f"📦 **Fayl:** `{latest_zip}`\n"
                response += f"📊 **Fayl sayı:** {len(file_list)}\n"
                response += f"📊 **Həcm:** {os.path.getsize(latest_zip) / (1024 * 1024):.2f} MB\n\n"

                # Qovluqları sayırıq
                folders = set()
                for file_path in file_list:
                    folder = os.path.dirname(file_path)
                    if folder:
                        folders.add(folder)

                response += f"📁 **Qovluqlar ({len(folders)}):**\n"
                for folder in sorted(folders):
                    response += f"  • `{folder}`\n"

                await event.reply(response, parse_mode='markdown')

        except Exception as e:
            await event.reply(f"❌ **ZIP oxunarkən xəta:**\n```\n{str(e)}\n```", parse_mode='markdown')

def register_zip_handlers(client):
    """ZIP yaradma handler-lərini qeydiyyata alır"""
    import shutil

    @client.on(events.NewMessage(pattern=r'^/zip (.+)'))
    async def create_zip(event):
        """Faylları ZIP arxivində birləşdirir"""
        if event.is_group and not await is_userbot_active_in_group(event.chat_id):
            return

        await event.delete()

        if event.sender_id != MESHEDI_ID:
            await event.reply("❌ Bu əmr yalnız admin tərəfindən istifadə edilə bilər!")
            return

        folder_path = event.pattern_match.group(1).strip()

        if not os.path.exists(folder_path):
            await event.reply(f"❌ Qovluq tapılmadı: {folder_path}")
            return

        try:
            zip_name = f"{os.path.basename(folder_path)}.zip"
            shutil.make_archive(zip_name.replace('.zip', ''), 'zip', folder_path)

            await event.reply(f"✅ ZIP arxivi yaradıldı: {zip_name}")
            add_log(f"ZIP arxivi yaradıldı: {zip_name}", "success")

        except Exception as e:
            await event.reply(f"❌ ZIP yaradma xətası: {str(e)}")
            add_log(f"ZIP yaradma xətası: {str(e)}", "error")

    add_log("ZIP yaradma sistemi yükləndi", "success")

if __name__ == "__main__":
    # Terminal əmri kimi işlətsək
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "create":
            create_project_zip()
        elif sys.argv[1] == "list":
            zip_files = [f for f in os.listdir('.') if f.startswith('UserBot_Backup_') and f.endswith('.zip')]
            if zip_files:
                latest_zip = max(zip_files, key=lambda f: os.path.getmtime(f))
                list_zip_contents(latest_zip)
            else:
                print("❌ ZIP fayl tapılmadı")
        else:
            print("İstifadə: python zip_creator.py [create|list]")
    else:
        create_project_zip()