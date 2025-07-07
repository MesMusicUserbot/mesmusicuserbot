# Setting the global_active flag to False to ensure the userbot is inactive by default in all groups.
"""
Qrupspesifik Userbot Aktivləşdirmə Sistemi
Bu modul hər qrup üçün ayrıca userbot funksiyalarını idarə edir.
Bot yenidən başladıqda aktivləşdirilmiş qrupları yadında saxlayır.
"""

from telethon import events
import json
import os
from .log_server import add_log
from .common_utils import JSONManager

# Məşədi ID
MESHEDI_ID = int(os.getenv('MESHEDI_ID', 5257767076))

# JSON fayl yolu
ACTIVATION_SETTINGS_FILE = "Menim_JSON_fayillarim/group_activation_settings.json"

async def initialize_group_activation_system():
    """Qrup aktivləşdirmə sistemini başlat və köhnə ayarları yüklə"""
    try:
        settings = await load_activation_settings()

        # Əgər aktivləşdirilmiş qruplar varsa, log-a yaz
        if settings and settings.get("active_groups"):
            active_count = len(settings["active_groups"])
            add_log(f"🔄 {active_count} aktivləşdirilmiş qrup yaddaşdan yükləndi", "info")

            # Hər qrup üçün log
            for group_id in settings["active_groups"]:
                add_log(f"✅ Qrup ID: {group_id} - Aktivləşdirilmiş vəziyyətdə", "success")
        else:
            add_log("📋 Heç bir qrup aktivləşdirilməyib - Bot default olaraq bütün qruplarda deaktivdir", "info")

        return settings
    except Exception as e:
        add_log(f"❌ Qrup aktivləşdirmə sistemi yüklənərkən xəta: {e}", "error")
        return None

async def load_activation_settings():
    """Qrup aktivləşdirmə ayarlarını yüklə"""
    default_settings = {
        "active_groups": [],  # Aktivləşdirilmiş qrupların siyahısı
        "global_active": False,  # Global aktivlik (default olaraq deaktiv)
        "persistent_activation": True,  # Aktivləşdirmələr daimi saxlanılsın
        "last_updated": None
    }
    return await JSONManager.load_json(ACTIVATION_SETTINGS_FILE, default_settings)

async def save_activation_settings(settings):
    """Qrup aktivləşdirmə ayarlarını saxla"""
    return JSONManager.save_json(ACTIVATION_SETTINGS_FILE, settings)

async def is_userbot_active_in_group(chat_id):
    """Userbot qrupda aktivdir mi?"""
    try:
        settings = await JSONManager.load_json("Menim_JSON_fayillarim/group_activation_settings.json", {
            "global_active": False,
            "active_groups": [],
            "persistent_activation": True
        })

        # Əgər settings None olarsa, default yarad
        if settings is None:
            settings = {"active_groups": [], "global_active": False, "persistent_activation": True}

        # Yalnız aktivləşdirilmiş qruplarda işləsin
        return chat_id in settings.get("active_groups", [])

    except Exception as e:
        print(f"Qrup aktivləşdirmə yoxlaması xətası: {e}")
        return False  # Xəta varsa, təhlükəsizlik üçün deaktiv hesab et

def register_group_activation_handlers(client):
    """Qrup aktivləşdirmə handler-lərini qeydiyyata al"""

    # Sistem başlayanda aktivləşdirilmiş qrupları yüklə
    async def load_persistent_groups():
        await initialize_group_activation_system()

    # İlk başlama zamanı çağır
    client.loop.create_task(load_persistent_groups())

    @client.on(events.NewMessage(pattern=r"\.aktivol"))
    async def activate_userbot_in_group(event):
        """Userbotu cari qrupda aktivləşdir"""
        await event.delete()

        sender = await event.get_sender()

        # Yalnız Məşədi işlədə bilər
        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            return

        # Yalnız qruplarda işləyir
        if not event.is_group:
            await event.reply("❌ Bu əmr yalnız qruplarda işləyir.")
            return

        chat = await event.get_chat()
        group_name = getattr(chat, 'title', 'Bu Qrup')
        chat_id = event.chat_id

        settings = await JSONManager.load_json(ACTIVATION_SETTINGS_FILE, {
            "active_groups": [],
            "global_active": False,
            "persistent_activation": True
        })

        # Əgər settings None olarsa, default yarad
        if settings is None:
            settings = {"active_groups": [], "global_active": False, "persistent_activation": True}

        if "active_groups" not in settings:
            settings["active_groups"] = []

        # Qrupu aktivləşdir və daimi saxla
        if chat_id not in settings["active_groups"]:
            settings["active_groups"].append(chat_id)
            settings["last_updated"] = str(chat_id)
            settings["persistent_activation"] = True
            await JSONManager.save_json(ACTIVATION_SETTINGS_FILE, settings)

            await event.reply(f"✅ **Userbot aktivləşdirildi!**\n\n🏷️ **Qrup:** {group_name}\n🤖 İndi bu qrupda bütün userbot funksiyaları işləyəcək.", parse_mode='markdown')
            add_log(f"🟢 Userbot aktivləşdirildi: {group_name} (ID: {chat_id})", "success", sender.id, sender.first_name)
        else:
            await event.reply(f"⚠️ **Userbot artıq aktivdir!**\n\n🏷️ **Qrup:** {group_name}\n🤖 Bu qrupda userbot funksiyaları hal-hazırda işləyir.", parse_mode='markdown')

    @client.on(events.NewMessage(pattern=r"\.deaktivol"))
    async def deactivate_userbot_in_group(event):
        """Userbotu cari qrupda deaktivləşdir"""
        await event.delete()

        sender = await event.get_sender()

        # Yalnız Məşədi işlədə bilər
        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            return

        # Yalnız qruplarda işləyir
        if not event.is_group:
            await event.reply("❌ Bu əmr yalnız qruplarda işləyir.")
            return

        chat = await event.get_chat()
        group_name = getattr(chat, 'title', 'Bu Qrup')
        chat_id = event.chat_id

        settings = await JSONManager.load_json(ACTIVATION_SETTINGS_FILE, {
            "active_groups": [],
            "global_active": False,
            "persistent_activation": True
        })

        # Əgər settings None olarsa, default yarad
        if settings is None:
            settings = {"active_groups": [], "global_active": False, "persistent_activation": True}

        # Qrupu deaktivləşdir və dəyişikliyi saxla
        if chat_id in settings.get("active_groups", []):
            settings["active_groups"].remove(chat_id)
            settings["last_updated"] = str(chat_id)
            await JSONManager.save_json(ACTIVATION_SETTINGS_FILE, settings)

            await event.reply(f"❌ **Userbot deaktivləşdirildi!**\n\n🏷️ **Qrup:** {group_name}\n🤖 İndi bu qrupda userbot funksiyaları işləməyəcək.", parse_mode='markdown')
            add_log(f"🔴 Userbot deaktivləşdirildi: {group_name} (ID: {chat_id})", "warning", sender.id, sender.first_name)
        else:
            await event.reply(f"⚠️ **Userbot artıq deaktivdir!**\n\n🏷️ **Qrup:** {group_name}\n🤖 Bu qrupda userbot funksiyaları hal-hazırda işləmir.", parse_mode='markdown')

    @client.on(events.NewMessage(pattern=r"\.aktivstatus"))
    async def check_activation_status(event):
        """Aktivləşdirmə statusunu yoxla"""
        await event.delete()

        sender = await event.get_sender()

        # Yalnız Məşədi işlədə bilər
        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            return

        settings = await JSONManager.load_json(ACTIVATION_SETTINGS_FILE, {
            "active_groups": [],
            "global_active": False
        })

        # Əgər settings None olarsa, default yarad
        if settings is None:
            settings = {"active_groups": [], "global_active": False}
        active_groups = settings.get("active_groups", [])

        status_text = "🤖 **Userbot Aktivləşdirmə Statusu**\n\n"

        if event.is_group:
            chat = await event.get_chat()
            group_name = getattr(chat, 'title', 'Bu Qrup')
            is_active = await is_userbot_active_in_group(event.chat_id)

            status_text += f"📍 **Cari Qrup:** {group_name}\n"
            status_text += f"🔧 **Status:** {'✅ Aktiv' if is_active else '❌ Deaktiv'}\n\n"

        status_text += f"📊 **Ümumi Statistika:**\n"
        status_text += f"🟢 Aktiv qruplar: {len(active_groups)} qrup\n"
        status_text += f"📋 Global ayar: {'✅ Aktiv' if settings.get('global_active', True) else '❌ Deaktiv'}\n\n"

        if active_groups:
            status_text += f"📝 **Aktiv Qruplar:**\n"
            for i, group_id in enumerate(active_groups[:5], 1):  # İlk 5 qrupu göstər
                status_text += f"{i}. Qrup ID: `{group_id}`\n"

            if len(active_groups) > 5:
                status_text += f"... və daha {len(active_groups) - 5} qrup\n"
        else:
            status_text += "📝 Heç bir qrup spesifik aktivləşdirilməyib.\n"

        status_text += f"\n💡 **Əmrlər:**\n"
        status_text += "• `.aktivol` - Userbotu bu qrupda aktivləşdir\n"
        status_text += "• `.deaktivol` - Userbotu bu qrupda deaktivləşdir\n"
        status_text += "• `.aktivstatus` - Aktivləşdirmə statusunu yoxla"

        await event.reply(status_text, parse_mode='markdown')

    @client.on(events.NewMessage(pattern=r"\.aktivtemizle"))
    async def clear_all_activations(event):
        """Bütün aktivləşdirmələri təmizlə"""
        await event.delete()

        sender = await event.get_sender()

        # Yalnız Məşədi işlədə bilər
        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            return

        settings = await JSONManager.load_json(ACTIVATION_SETTINGS_FILE, {
            "active_groups": [],
            "global_active": False
        })

        # Əgər settings None olarsa, default yarad
        if settings is None:
            settings = {"active_groups": [], "global_active": False}
        old_count = len(settings.get("active_groups", []))

        settings["active_groups"] = []
        await JSONManager.save_json(ACTIVATION_SETTINGS_FILE, settings)

        await event.reply(f"🗑️ **Bütün aktivləşdirmələr təmizləndi!**\n\n📊 Təmizlənən qrup sayı: {old_count}\n🤖 İndi userbot heç bir qrupda spesifik aktivləşdirilməyib.", parse_mode='markdown')
        add_log(f"🗑️ Bütün qrup aktivləşdirmələri təmizləndi ({old_count} qrup)", "info", sender.id, sender.first_name)

def check_group_activation_middleware(func):
    """Decorator - qrup aktivləşdirməsini yoxlayır"""
    async def wrapper(event):
        # PM-lərdə həmişə işləsin
        if event.is_private:
            return await func(event)

        # Qruplarda aktivlik yoxlanılır
        if event.is_group:
            if not await is_userbot_active_in_group(event.chat_id):
                # Userbot bu qrupda aktiv deyil - heç bir cavab vermə
                return

        # Aktivdirsə normal şəkildə işlə
        return await func(event)

    return wrapper

# Alias for backward compatibility
register_group_handlers = register_group_activation_handlers