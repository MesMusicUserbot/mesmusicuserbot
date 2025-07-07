"""
Ümumi Köməkçi Funksiyalar
Bu modul bütün modullar tərəfindən istifadə edilən ümumi funksiyaları ehtiva edir.
"""

import json
import os
import time
from typing import Dict, List, Any, Optional
from .error_handler import safe_execute, ErrorHandler

# Sabitlər
MESHEDI_ID = int(os.getenv('MESHEDI_ID', 5257767076))
MESHBOT_USERBOT_ID = int(os.getenv('MESHBOT_USERBOT_ID', 4831999346))
JSON_DIR = "Menim_JSON_fayillarim"

class JSONManager:
    """JSON fayllarının idarə edilməsi üçün ümumi sinif"""

    JSON_DIR = "Menim_JSON_fayillarim"

    @staticmethod
    @safe_execute("JSON faylı oxunması")
    async def load_json(file_path: str, default_data: Any = None) -> Any:
        """
        JSON faylını yüklə

        Args:
            file_path (str): Faylın yolu
            default_data (Any): Default məlumat

        Returns:
            Any: JSON məlumatları
        """
        try:
            # Qovluğun mövcudluğunu təmin et
            os.makedirs(os.path.dirname(file_path), mode=0o755, exist_ok=True)

            if not os.path.exists(file_path):
                if default_data is not None:
                    await JSONManager.save_json(file_path, default_data)
                    return default_data
                return {}

            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            ErrorHandler.handle_json_error(e, f"oxunması - {file_path}")
            return default_data if default_data is not None else {}
        except Exception as e:
            ErrorHandler.handle_file_error(e, file_path)
            return default_data if default_data is not None else {}

    @staticmethod
    def load_json_sync(file_path: str, default_data: Any = None) -> Any:
        """
        Sync JSON faylını yüklə - köhnə funksiyalar üçün

        Args:
            file_path (str): Faylın yolu
            default_data (Any): Default məlumat

        Returns:
            Any: JSON məlumatları
        """
        try:
            if not os.path.exists(file_path):
                if default_data is not None:
                    JSONManager.save_json_sync(file_path, default_data)
                    return default_data
                return {}

            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"JSON oxuma xətası ({file_path}): {e}")
            if default_data is not None:
                JSONManager.save_json_sync(file_path, default_data)
                return default_data
            return {}

    @staticmethod
    @safe_execute("JSON faylı saxlanması")
    async def save_json(file_path: str, data: Any) -> bool:
        """
        JSON faylını saxla

        Args:
            file_path (str): Faylın yolu
            data (Any): Saxlanılacaq məlumat

        Returns:
            bool: Uğurlu olub olmadığı
        """
        try:
            # Qovluğun mövcudluğunu təmin et
            os.makedirs(os.path.dirname(file_path), mode=0o755, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            ErrorHandler.handle_file_error(e, file_path)
            return False

    @staticmethod
    def save_json_sync(file_path: str, data: Any) -> bool:
        """
        Sync JSON faylını saxla - köhnə funksiyalar üçün

        Args:
            file_path (str): Faylın yolu
            data (Any): Saxlanılacaq məlumat

        Returns:
            bool: Uğurlu olub olmadığı
        """
        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"JSON saxlama xətası ({file_path}): {e}")
            return False

class UserPermissions:
    """İstifadəçi icazələrinin yoxlanması"""

    @staticmethod
    def is_meshedi(user_id: int) -> bool:
        """İstifadəçinin Məşədi olub olmadığını yoxlayır"""
        return user_id == MESHEDI_ID

    @staticmethod
    async def is_admin(client, chat_id: int, user_id: int) -> bool:
        """İstifadəçinin admin olub olmadığını yoxlayır"""
        try:
            from telethon.tl.types import ChannelParticipantsAdmins

            chat_input = await client.get_input_entity(chat_id)
            admins = await client.get_participants(chat_input, filter=ChannelParticipantsAdmins())
            admin_ids = [admin.id for admin in admins]
            return user_id in admin_ids
        except Exception as e:
            ErrorHandler.handle_telegram_error(e, "admin yoxlanması")
            return False

    @staticmethod
    async def check_command_permission(event, required_level: str = "user") -> tuple[bool, str]:
        """
        Komanda icazəsini yoxlayır

        Args:
            event: Telegram hadisəsi
            required_level (str): Tələb olunan səviyyə (meshedi, admin, user)

        Returns:
            tuple[bool, str]: (icazə var, xəta mesajı)
        """
        try:
            sender = await event.get_sender()

            if required_level == "meshedi":
                if not UserPermissions.is_meshedi(sender.id):
                    mention = f"[{sender.first_name}](tg://user?id={sender.id})"
                    return False, f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər."

            elif required_level == "admin":
                if not UserPermissions.is_meshedi(sender.id):
                    is_admin = await UserPermissions.is_admin(event.client, event.chat_id, sender.id)
                    if not is_admin:
                        mention = f"[{sender.first_name}](tg://user?id={sender.id})"
                        return False, f"{mention} ❌ Bu əmri yalnız adminlər işlədə bilər."

            return True, ""

        except Exception as e:
            ErrorHandler.handle_telegram_error(e, "icazə yoxlanması")
            return False, "❌ İcazə yoxlanılarkən xəta baş verdi."

class MessageUtils:
    """Mesaj utilləri"""

    @staticmethod
    def clean_user_name(name: str, max_length: int = 20) -> str:
        """İstifadəçi adını təmizləyir"""
        if not name:
            return "İstifadəçi"

        clean_name = "".join(c for c in name if c.isalnum() or c.isspace())[:max_length]
        return clean_name.strip() or "İstifadəçi"

    @staticmethod
    def create_mention(user_id: int, name: str) -> str:
        """İstifadəçi mention-u yaradır"""
        clean_name = MessageUtils.clean_user_name(name)
        return f"[{clean_name}](tg://user?id={user_id})"

class FilterManager:
    """Ümumi filter idarəetməsi"""

    @staticmethod
    def load_filter_settings(filter_name: str) -> Dict:
        """Filter ayarlarını yüklə"""
        file_path = f"{JSON_DIR}/{filter_name}_settings.json"
        default_settings = {
            "enabled": False,
            "groups": [],
            "excluded_users": [],
            "excluded_chats": [],
            "auto_delete": True,
            "warn_user": True
        }
        return JSONManager.load_json_sync(file_path, default_settings)

    @staticmethod
    def save_filter_settings(filter_name: str, settings: Dict) -> bool:
        """Filter ayarlarını saxla"""
        file_path = f"{JSON_DIR}/{filter_name}_settings.json"
        return JSONManager.save_json_sync(file_path, settings)

    @staticmethod
    def is_filter_active(settings: Dict, chat_id: int) -> bool:
        """Filterin aktivliyini yoxlayır"""
        return (settings.get("enabled", False) and 
                chat_id in settings.get("groups", []))

    @staticmethod
    @safe_execute("Link yoxlama və silmə")
    async def check_and_delete_links(event, settings: Dict, client) -> bool:
        """Link yoxla və sil"""
        try:
            import re
            message_text = event.message.text or ""

            # Link pattern
            link_patterns = [
                r'https?://[^\s]+',
                r'www\.[^\s]+', 
                r't\.me/[^\s]+',
                r'@[a-zA-Z0-9_]+'
            ]

            has_link = False
            for pattern in link_patterns:
                if re.search(pattern, message_text, re.IGNORECASE):
                    has_link = True
                    break

            if has_link and settings.get("auto_delete", True):
                await event.delete()

                if settings.get("warn_user", True):
                    sender = await event.get_sender()
                    sender_mention = MessageUtils.create_mention(sender.id, sender.first_name)
                    await client.send_message(event.chat_id, 
                        f"🚫 {sender_mention}, link paylaşmaq qadağandır!", 
                        parse_mode='markdown')
                return True
            return False

        except Exception as e:
            ErrorHandler.handle_telegram_error(e, "link yoxlama")
            return False

# Decoratorlar
def require_permission(level: str = "user"):
    """İcazə tələb edən decorator"""
    def decorator(func):
        async def wrapper(event):
            permission_ok, error_msg = await UserPermissions.check_command_permission(event, level)
            if not permission_ok:
                await event.reply(error_msg, parse_mode='markdown')
                return
            return await func(event)
        return wrapper
    return decorator

def require_group():
    """Qrupda olduğunu tələb edən decorator"""
    def decorator(func):
        async def wrapper(event):
            if not event.is_group:
                await event.reply("❌ Bu əmr yalnız qruplarda işləyir.")
                return
            return await func(event)
        return wrapper
    return decorator