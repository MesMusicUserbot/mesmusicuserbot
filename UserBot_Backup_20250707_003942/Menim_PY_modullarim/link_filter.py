"""
Link Filter Modulu
Bu modul qruplarda link paylaşımını idarə edir və tənzimləyir.
"""

from telethon import events
from telethon.tl.types import ChannelParticipantsAdmins
import re
import asyncio
from .log_server import add_log
from .common_utils import JSONManager, UserPermissions, MessageUtils, FilterManager, require_permission, require_group, MESHEDI_ID
from .error_handler import safe_execute, ErrorHandler
from .group_activation import is_userbot_active_in_group

# Sabitlər
LINK_FILTER_NAME = "link_filter"

def load_link_filter_settings():
    """Link filter ayarlarını yüklə"""
    try:
        import json
        import os
        file_path = f"{JSONManager.JSON_DIR}/link_filter_settings.json"

        # Qovluğun mövcudluğunu təmin et
        os.makedirs(JSONManager.JSON_DIR, mode=0o755, exist_ok=True)

        if not os.path.exists(file_path):
            default_data = {
                "enabled": False,
                "groups": [],
                "group_allowed_links": {},
                "global_allowed_link": "",
                "excluded_users": [],
                "excluded_chats": [],
                "auto_delete": True,
                "warn_user": True
            }
            save_link_filter_settings(default_data)
            return default_data

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        ErrorHandler.handle_file_error(e, "link_filter_settings.json")
        return {"enabled": False, "groups": []}

def save_link_filter_settings(settings):
    """Link filter ayarlarını saxla"""
    try:
        import json
        import os
        file_path = f"{JSONManager.JSON_DIR}/link_filter_settings.json"

        # Qovluğun mövcudluğunu təmin et
        os.makedirs(JSONManager.JSON_DIR, mode=0o755, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        ErrorHandler.handle_file_error(e, "link_filter_settings.json")
        return False

# Köhnə funksiyalar silindi - yeni sistem istifadə edilir

def register_link_handlers(client):
    @client.on(events.NewMessage(pattern=r"\.linkstart"))
    async def enable_link_filter(event):
        await event.delete()

        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            return

        if not event.is_group:
            await event.reply("Bu əmr yalnız qruplarda işləyir.")
            return

        link_settings = load_link_filter_settings()

        if "groups" not in link_settings:
            link_settings["groups"] = []

        if event.chat_id not in link_settings["groups"]:
            link_settings["groups"].append(event.chat_id)

        save_link_filter_settings(link_settings)
        await event.reply("🔗 Link filtri bu qrupda aktivləşdirildi! İcazəsiz linklər silinəcək.")

    @client.on(events.NewMessage(pattern=r"\.linkstop"))
    async def disable_link_filter(event):
        await event.delete()

        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            return

        if not event.is_group:
            await event.reply("Bu əmr yalnız qruplarda işləyir.")
            return

        link_settings = load_link_filter_settings()

        if "groups" in link_settings and event.chat_id in link_settings["groups"]:
            link_settings["groups"].remove(event.chat_id)

        save_link_filter_settings(link_settings)
        await event.reply("🔗 Link filtri bu qrupda dayandırıldı.")

    @client.on(events.NewMessage(pattern=r"\.linkəlavə"))
    async def add_group_allowed_link(event):
        await event.delete()

        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            return

        if not event.is_group:
            await event.reply("Bu əmr yalnız qruplarda işləyir.")
            return

        command_parts = event.raw_text.split(maxsplit=1)
        if len(command_parts) < 2:
            await event.reply("📝 **İstifadə:** `.linkəlavə https://t.me/+your_link`\n\n**Nümunə:**\n`.linkəlavə https://t.me/+ehgPQ1kXjzM1NDRi`")
            return

        new_link = command_parts[1].strip()

        if not new_link.startswith('http'):
            if new_link.startswith('t.me'):
                new_link = f"https://{new_link}"
            else:
                await event.reply("❌ Düzgün link formatı daxil edin. Nümunə: `https://t.me/+link`")
                return

        link_settings = load_link_filter_settings()

        if "group_allowed_links" not in link_settings:
            link_settings["group_allowed_links"] = {}

        group_id = str(event.chat_id)
        if group_id not in link_settings["group_allowed_links"]:
            link_settings["group_allowed_links"][group_id] = []

        if new_link in link_settings["group_allowed_links"][group_id]:
            await event.reply(f"⚠️ Bu link artıq bu qrupda icazəlidir:\n`{new_link}`")
            return

        link_settings["group_allowed_links"][group_id].append(new_link)
        save_link_filter_settings(link_settings)

        await event.reply(f"✅ **Link icazəli linklər siyahısına əlavə edildi!**\n\n🔗 Link: `{new_link}`\n📍 Bu link yalnız bu qrupda paylaşıla bilər.", parse_mode='markdown')

    @client.on(events.NewMessage(pattern=r"\.linksil"))
    async def remove_group_allowed_link(event):
        await event.delete()

        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            return

        if not event.is_group:
            await event.reply("Bu əmr yalnız qruplarda işləyir.")
            return

        command_parts = event.raw_text.split(maxsplit=1)
        if len(command_parts) < 2:
            await event.reply("📝 **İstifadə:** `.linksil https://t.me/+your_link`\n\n**Nümunə:**\n`.linksil https://t.me/+ehgPQ1kXjzM1NDRi`")
            return

        link_to_remove = command_parts[1].strip()

        if not link_to_remove.startswith('http'):
            if link_to_remove.startswith('t.me'):
                link_to_remove = f"https://{link_to_remove}"
            else:
                await event.reply("❌ Düzgün link formatı daxil edin. Nümunə: `https://t.me/+link`")
                return

        link_settings = load_link_filter_settings()

        group_id = str(event.chat_id)
        group_links = link_settings.get("group_allowed_links", {}).get(group_id, [])

        if link_to_remove not in group_links:
            await event.reply(f"⚠️ Bu link bu qrupun icazəli linklər siyahısında deyil:\n`{link_to_remove}`")
            return

        link_settings["group_allowed_links"][group_id].remove(link_to_remove)
        save_link_filter_settings(link_settings)

        await event.reply(f"❌ **Link icazəli linklər siyahısından silindi!**\n\n🔗 Silinən link: `{link_to_remove}`\n📍 Bu link artıq bu qrupda paylaşıla bilməz.", parse_mode='markdown')

    @client.on(events.NewMessage(pattern=r"\.linkglobal"))
    async def set_global_allowed_link(event):
        await event.delete()

        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            return

        command_parts = event.raw_text.split(maxsplit=1)
        if len(command_parts) < 2:
            await event.reply("📝 **İstifadə:** `.linkglobal https://t.me/+your_link`\n\n**Nümunə:**\n`.linkglobal https://t.me/+ehgPQ1kXjzM1NDRi`\n\n**Qeyd:** Bu link bütün qruplarda icazəli olacaq.")
            return

        new_global_link = command_parts[1].strip()

        if not new_global_link.startswith('http'):
            if new_global_link.startswith('t.me'):
                new_global_link = f"https://{new_global_link}"
            else:
                await event.reply("❌ Düzgün link formatı daxil edin. Nümunə: `https://t.me/+link`")
                return

        link_settings = load_link_filter_settings()

        if "global_allowed_link" not in link_settings:
            link_settings["global_allowed_link"] = ""

        old_global_link = link_settings.get("global_allowed_link", "")
        link_settings["global_allowed_link"] = new_global_link

        save_link_filter_settings(link_settings)

        if old_global_link:
            await event.reply(f"🌍 **Global link yeniləndi!**\n\n🔄 **Köhnə:** `{old_global_link}`\n✅ **Yeni:** `{new_global_link}`\n\n📍 Bu link bütün qruplarda icazəlidir.", parse_mode='markdown')
        else:
            await event.reply(f"🌍 **Global link təyin edildi!**\n\n✅ **Link:** `{new_global_link}`\n\n📍 Bu link bütün qruplarda icazəlidir.", parse_mode='markdown')

    @client.on(events.NewMessage(pattern=r"\.linkglobalsil"))
    async def remove_global_allowed_link(event):
        await event.delete()

        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            return

        link_settings = load_link_filter_settings()

        current_global_link = link_settings.get("global_allowed_link", "")

        if not current_global_link:
            await event.reply("⚠️ **Global link təyin edilməyib!**\n\nHəmişə `.linkglobal` komandası ilə əvvəlcə global link təyin etməlisiniz.", parse_mode='markdown')
            return

        link_settings["global_allowed_link"] = ""
        save_link_filter_settings(link_settings)

        await event.reply(f"❌ **Global link silindi!**\n\n🗑️ **Silinən link:** `{current_global_link}`\n\n📍 İndi heç bir global icazəli link yoxdur. Yalnız qrup-spesifik linklər keçərlidir.", parse_mode='markdown')

    @client.on(events.NewMessage(pattern=r"\.linkstatus"))
    async def list_group_allowed_links(event):
        await event.delete()

        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            return

        if not event.is_group:
            await event.reply("Bu əmr yalnız qruplarda işləyir.")
            return

        link_settings = load_link_filter_settings()

        group_id = str(event.chat_id)
        group_links = link_settings.get("group_allowed_links", {}).get(group_id, [])

        chat = await event.get_chat()
        group_name = chat.title if hasattr(chat, 'title') else "Bu Qrup"

        response_text = f"🔗 **{group_name} - İcazəli Linklər**\n\n"

        global_link = link_settings.get("global_allowed_link", "")
        if global_link:
            response_text += f"🌍 **Global İcazəli Link:**\n`{global_link}`\n\n"
        else:
            response_text += f"🌍 **Global İcazəli Link:**\nTəyin edilməyib (.linkglobal ilə təyin edin)\n\n"

        if group_links:
            response_text += f"📍 **Bu Qrupun Xüsusi İcazəli Linkləri ({len(group_links)} ədəd):**\n"
            for i, link in enumerate(group_links, 1):
                response_text += f"{i}. `{link}`\n"
        else:
            response_text += "📍 **Bu Qrupun Xüsusi İcazəli Linkləri:**\nHeç bir xüsusi link yoxdur.\n"

        response_text += f"\n**📋 Əmrlər:**\n"
        response_text += f"• `.linkglobal [link]` - Global link təyin et (bütün qruplarda)\n"
        response_text += f"• `.linkəlavə [link]` - Qrupa xüsusi link əlavə et\n"
        response_text += f"• `.linksil [link]` - Qrupdan xüsusi link sil\n"
        response_text += f"• `.linkstatus` - Bu qrupun link filtri statusunu və icazəli linklərini göstər\n"
        response_text += f"• `.linkstart` - Link filtrini qrupda aktiv et\n"
        response_text += f"• `.linkstop` - Link filtrini qrupda dayandır"

        await event.reply(response_text, parse_mode='markdown')

    @client.on(events.NewMessage(incoming=True))
    async def link_filter_handler(event):
        # Yalnız qruplarda işləsin
        if not event.is_group:
            return

        # Qrupda userbotun aktiv olub olmadığını yoxla
        if not await is_userbot_active_in_group(event.chat_id):
            return

        link_settings = load_link_filter_settings()
        active_groups = link_settings.get("groups", [])

        if event.chat_id not in active_groups:
            return

        try:
            sender = await event.get_sender()

            if not sender or not hasattr(sender, 'id'):
                print("⚠️ Sender məlumatı əldə edilə bilmədi (link filter)")
                return

            if sender.id == MESHEDI_ID:
                return

            message_text = event.message.message or ""

            all_patterns = [
                r'https?://t\.me/[^\s\)]+',
                r'http://t\.me/[^\s\)]+',
                r't\.me/[^\s\)]+',
                r'@[a-zA-Z0-9_]+',
            ]

            found_links = []
            for pattern in all_patterns:
                matches = re.findall(pattern, message_text, re.IGNORECASE)
                found_links.extend(matches)

            if found_links:
                should_delete = False

                group_allowed_links = link_settings.get("group_allowed_links", {}).get(str(event.chat_id), [])

                global_link = link_settings.get("global_allowed_link", "")
                global_allowed = [global_link] if global_link else []

                all_allowed_links = global_allowed + group_allowed_links

                for link in found_links:
                    normalized_link = link
                    if not link.startswith('http'):
                        if link.startswith('t.me'):
                            normalized_link = f"https://{link}"
                        elif link.startswith('@'):
                            continue

                    is_allowed = False
                    for allowed_link in all_allowed_links:
                        if normalized_link == allowed_link or normalized_link.startswith(allowed_link):
                            is_allowed = True
                            break

                    if not is_allowed and not link.startswith('@'):
                        should_delete = True
                        print(f"🚫 Qadağan edilmiş link tapıldı: {link}")
                        print(f"📋 İcazəli linklər bu qrupda: {all_allowed_links}")
                        break

                if should_delete:
                    try:
                        await event.delete()
                        print(f"🚫 Mesaj silindi. Göndərən: {sender.first_name or 'Unknown'} (ID: {sender.id})")

                        # Real Telegram adını al (emoji və xüsusi simvollarla birlikdə)
                        first_name = getattr(sender, 'first_name', None) or ""
                        last_name = getattr(sender, 'last_name', None) or ""

                        # Tam adı yarat - emojini saxla
                        full_name = f"{first_name} {last_name}".strip()
                        if not full_name:
                            username = getattr(sender, 'username', None)
                            if username:
                                full_name = f"@{username}"
                            else:
                                full_name = f"User {sender.id}"

                        # Real adı mention üçün istifadə et (emoji və bütün simvollarla)
                        display_name = full_name[:50]  # Yalnız uzunluğu məhdudlaşdır
                        if not display_name.strip():
                            display_name = f"User {sender.id}"

                        sender_mention = f"[{display_name}](tg://user?id={sender.id})"

                        try:
                            await client.send_message(event.chat_id, f"{sender_mention} 🚫 Bu qrupda icazəsiz link paylaşmaq olmaz!", parse_mode='markdown')
                        except Exception as mention_error:
                            await client.send_message(event.chat_id, f"🚫 {clean_name} Bu qrupda icazəsiz link paylaşmaq olmaz!")

                        return

                    except Exception as delete_error:
                        print(f"❌ Mesaj silinərkəən xəta: {delete_error}")
                        try:
                            user_info = await client.get_entity(event.sender_id)
                            username = user_info.username or "İstifadəçi"
                            await event.reply(f"⚠️ @{username}, link göndərmək qadağandır!")
                        except:
                            await event.reply("⚠️ Link göndərmək qadağandır!")

        except Exception as e:
            print(f"❌ Link filter xətası: {e}")