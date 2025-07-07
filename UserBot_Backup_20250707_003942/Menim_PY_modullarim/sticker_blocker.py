from telethon import events
import json
import os
import time
from .log_server import add_log

MESHEDI_ID = 5257767076
LOCKED_STICKERS_FILE = "Menim_JSON_fayillarim/locked_stickers.json"
STICKER_BLOCKER_SETTINGS_FILE = "Menim_JSON_fayillarim/sticker_blocker_settings.json"
ALLOWED_USERS_FILE = "Menim_JSON_fayillarim/sticker_allowed_users.json"

def load_locked_stickers():
    if not os.path.exists(LOCKED_STICKERS_FILE):
        return {}
    with open(LOCKED_STICKERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_locked_stickers(data):
    with open(LOCKED_STICKERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_sticker_blocker_settings():
    if not os.path.exists(STICKER_BLOCKER_SETTINGS_FILE):
        return {"groups": []}
    with open(STICKER_BLOCKER_SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_sticker_blocker_settings(data):
    with open(STICKER_BLOCKER_SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_allowed_users():
    if not os.path.exists(ALLOWED_USERS_FILE):
        return []
    with open(ALLOWED_USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_allowed_users(data):
    with open(ALLOWED_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def register_sticker_handlers(client):
    @client.on(events.NewMessage(pattern=r"\.stikerlock"))
    async def lock_sticker_handler(event):
        await event.delete()

        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            add_log(f"Stiker kilidləmə: {sender.first_name} adlı istifadəçi icazəsiz əmr istifadə etdi", "warning")
            return

        reply = await event.get_reply_message()
        if not reply or not reply.sticker:
            await event.reply("🔒 Bu əmri yalnız stikerə reply edərək işlədə bilərsiniz.")
            add_log("Stiker kilidləmə: İstifadəçi stikerə cavab vermədən əmri işlətməyə çalışdı", "warning")
            return

        sticker_id = reply.sticker.id
        locked_stickers = load_locked_stickers()

        if str(sticker_id) in locked_stickers:
            await event.reply("⚠️ Bu stiker artıq bloklanıb.")
            add_log(f"Stiker kilidləmə: {sticker_id} stikeri artıq bloklanmışdı", "warning")
            return

        locked_stickers[str(sticker_id)] = {
            "file_id": sticker_id,
            "locked_by": sender.id,
            "locked_at": time.time()
        }

        save_locked_stickers(locked_stickers)
        await event.reply("🔒 Stiker bloklandı. İndi yalnız Məşədi bu stikeri göndərə bilər.")
        add_log(f"Stiker kilidləmə: {sticker_id} stikeri Məşədi tərəfindən bloklandı", "info")

    @client.on(events.NewMessage(pattern=r"\.stikerunlock"))
    async def unlock_sticker_handler(event):
        await event.delete()

        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            add_log(f"Stiker kilidləmə: {sender.first_name} adlı istifadəçi icazəsiz əmr istifadə etdi", "warning")
            return

        reply = await event.get_reply_message()
        if not reply or not reply.sticker:
            await event.reply("🔓 Bu əmri yalnız stikerə reply edərək işlədə bilərsiniz.")
            add_log("Stiker kilidləmə: İstifadəçi stikerə cavab vermədən əmri işlətməyə çalışdı", "warning")
            return

        sticker_id = reply.sticker.id
        locked_stickers = load_locked_stickers()

        if str(sticker_id) not in locked_stickers:
            await event.reply("⚠️ Bu stiker bloklanmayıb.")
            add_log(f"Stiker kilidləmə: {sticker_id} stikeri bloklanmamışdı", "warning")
            return

        del locked_stickers[str(sticker_id)]
        save_locked_stickers(locked_stickers)
        await event.reply("🔓 Stiker bloku götürüldü. İndi hamı bu stikeri göndərə bilər.")
        add_log(f"Stiker kilidləmə: {sticker_id} stikerinin kilidi Məşədi tərəfindən açıldı", "info")

    @client.on(events.NewMessage(pattern=r"\.stikerstart"))
    async def enable_sticker_blocker(event):
        await event.delete()

        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            add_log(f"Stiker bloklama: {sender.first_name} adlı istifadəçi icazəsiz əmr istifadə etdi", "warning")
            return

        if not event.is_group:
            await event.reply("Bu əmr yalnız qruplarda işləyir.")
            add_log("Stiker bloklama: İstifadəçi əmri qrupda işlətməyə çalışdı", "warning")
            return

        sticker_settings = load_sticker_blocker_settings()

        if "groups" not in sticker_settings:
            sticker_settings["groups"] = []

        if event.chat_id not in sticker_settings["groups"]:
            sticker_settings["groups"].append(event.chat_id)

        save_sticker_blocker_settings(sticker_settings)
        await event.reply("🔒 Stiker bloklaşdırma bu qrupda aktivləşdirildi! Bloklanmış stikerlər silinəcək.")
        add_log(f"Stiker bloklama: {event.chat_id} qrupunda stiker bloklama aktiv edildi", "info")

    @client.on(events.NewMessage(pattern=r"\.stikerstop"))
    async def disable_sticker_blocker(event):
        await event.delete()

        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            add_log(f"Stiker bloklama: {sender.first_name} adlı istifadəçi icazəsiz əmr istifadə etdi", "warning")
            return

        if not event.is_group:
            await event.reply("Bu əmr yalnız qruplarda işləyir.")
            add_log("Stiker bloklama: İstifadəçi əmri qrupda işlətməyə çalışdı", "warning")
            return

        sticker_settings = load_sticker_blocker_settings()

        if "groups" in sticker_settings and event.chat_id in sticker_settings["groups"]:
            sticker_settings["groups"].remove(event.chat_id)

        save_sticker_blocker_settings(sticker_settings)
        await event.reply("🔓 Stiker bloklaşdırma bu qrupda dayandırıldı.")
        add_log(f"Stiker bloklama: {event.chat_id} qrupunda stiker bloklama dayandırıldı", "info")

    @client.on(events.NewMessage(pattern=r"\.stikerstatus"))
    async def sticker_blocker_status(event):
        await event.delete()

        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            add_log(f"Stiker bloklama: {sender.first_name} adlı istifadəçi icazəsiz əmr istifadə etdi", "warning")
            return

        sticker_settings = load_sticker_blocker_settings()
        locked_stickers = load_locked_stickers()
        active_groups = sticker_settings.get("groups", [])

        status_text = "🔒 **STİKER BLOKLAMA SİSTEMİ**\n\n"

        # Sistem statusu
        allowed_users = load_allowed_users()
        status_text += f"📊 **Sistem Statusu:**\n"
        status_text += f"🔒 Bloklanmış stikerlər: {len(locked_stickers)} ədəd\n"
        status_text += f"🏢 Aktiv qruplar: {len(active_groups)} qrup\n"
        status_text += f"👥 İcazəli istifadəçilər: {len(allowed_users)} nəfər\n\n"

        # İcazəli istifadəçiləri göstər
        if allowed_users:
            status_text += "👥 **İcazəli İstifadəçilər:**\n"
            for user_id in allowed_users:
                try:
                    # İstifadəçi məlumatını əldə etməyə çalış
                    user = await client.get_entity(user_id)
                    user_name = user.first_name or "İstifadəçi"
                    if hasattr(user, 'last_name') and user.last_name:
                        user_name += f" {user.last_name}"
                    status_text += f"• [{user_name}](tg://user?id={user_id}) - `{user_id}`\n"
                except Exception:
                    # Əgər istifadəçi məlumatı alınmırsa, yalnız ID göstər
                    status_text += f"• İstifadəçi - `{user_id}`\n"
            status_text += "\n"
        else:
            status_text += "👥 **İcazəli İstifadəçilər:** Heç kim\n\n"

        # Bu qrupda aktiv olub olmadığını yoxla
        if event.is_group:
            is_active_here = event.chat_id in active_groups
            chat = await event.get_chat()
            group_name = chat.title if hasattr(chat, 'title') else "Bu Qrup"
            status_text += f"📍 **{group_name}:** {'✅ Aktiv' if is_active_here else '❌ Deaktiv'}\n\n"

        status_text += "**📋 İdarəetmə Əmrləri:**\n"
        status_text += "• `.stikerstart` - Qrupda stiker filtrini aktiv et\n"
        status_text += "• `.stikerstop` - Qrupda stiker filtrini dayandır\n"
        status_text += "• `.stikerstatus` - Stiker filtri statusunu göstər\n\n"
        status_text += "**🔒 Stiker İdarəsi:**\n"
        status_text += "• `.stikerlock` - Stikerə reply edərək blokla\n"
        status_text += "• `.stikerunlock` - Stikerə reply edərək bloku götür\n\n"
        status_text += "**👥 İstifadəçi İcazələri:**\n"
        status_text += "• `.stikericazə [id]` - İstifadəçiyə bloklanmış stiker icazəsi ver\n"
        status_text += "• `.stikericazəsil [id]` - İstifadəçinin icazəsini götür\n\n"
        status_text += "🤖 **Avtomatik İşləmə:** Bloklanmış stikerlər avtomatik silinir və istifadəçiyə xəbərdarlıq edilir."

        await event.reply(status_text, parse_mode='markdown')
        add_log(f"Stiker bloklama: {sender.first_name} stiker statusunu yoxladı", "info")

    @client.on(events.NewMessage(pattern=r"\.stikericazə"))
    async def allow_user_stickers(event):
        await event.delete()

        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            add_log(f"Stiker icazə: {sender.first_name} adlı istifadəçi icazəsiz əmr istifadə etdi", "warning")
            return

        command_parts = event.raw_text.split(maxsplit=1)
        if len(command_parts) < 2:
            await event.reply("📝 **İstifadə:** `.stikericazə [telegram_id]`\n\n**Nümunə:**\n`.stikericazə 123456789`\n\n**Qeyd:** Bu istifadəçi bloklanmış stikerləri göndərə biləcək.")
            add_log("Stiker icazə: İstifadəçi telegram id daxil etmədi", "warning")
            return

        try:
            user_id = int(command_parts[1].strip())
        except ValueError:
            await event.reply("❌ Düzgün Telegram ID daxil edin. Yalnız rəqəmlər olmalıdır.")
            add_log("Stiker icazə: İstifadəçi düzgün telegram id daxil etmədi", "warning")
            return

        if user_id == MESHEDI_ID:
            await event.reply("⚠️ Məşədi artıq bütün stikerlər üçün icazəyə malikdir.")
            add_log("Stiker icazə: İstifadəçi Məşədi ID-sini daxil etdi", "warning")
            return

        allowed_users = load_allowed_users()

        if user_id in allowed_users:
            add_log("Stiker icazə: İstifadəçi artıq icazəli istifadəçilər siyahısında var", "warning")
            return

        allowed_users.append(user_id)
        save_allowed_users(allowed_users)

        await event.reply(f"✅ **İstifadəçi icazəli siyahıya əlavə edildi!**\n\n👤 **Telegram ID:** `{user_id}`\n🔓 Bu istifadəçi indi bloklanmış stikerləri göndərə bilər.", parse_mode='markdown')
        add_log(f"Stiker icazə: {user_id} adlı istifadəçi icazəli istifadəçilər siyahısına əlavə edildi", "info")

    @client.on(events.NewMessage(pattern=r"\.stikericazəsil"))
    async def remove_user_permission(event):
        await event.delete()

        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            add_log(f"Stiker icazə silmə: {sender.first_name} adlı istifadəçi icazəsiz əmr istifadə etdi", "warning")
            return

        command_parts = event.raw_text.split(maxsplit=1)
        if len(command_parts) < 2:
            await event.reply("📝 **İstifadə:** `.stikericazəsil [telegram_id]`\n\n**Nümunə:**\n`.stikericazəsil 123456789`")
            add_log("Stiker icazə silmə: İstifadəçi telegram id daxil etmədi", "warning")
            return

        try:
            user_id = int(command_parts[1].strip())
        except ValueError:
            await event.reply("❌ Düzgün Telegram ID daxil edin. Yalnız rəqəmlər olmalıdır.")
            add_log("Stiker icazə silmə: İstifadəçi düzgün telegram id daxil etmədi", "warning")
            return

        allowed_users = load_allowed_users()

        if user_id not in allowed_users:
            await event.reply(f"⚠️ Bu istifadəçi (ID: {user_id}) icazəli siyahıda deyil.")
            add_log(f"Stiker icazə silmə: {user_id} adlı istifadəçi icazəli istifadəçilər siyahısında yoxdur", "warning")
            return

        allowed_users.remove(user_id)
        save_allowed_users(allowed_users)

        await event.reply(f"❌ **İstifadəçi icazəli siyahıdan silindi!**\n\n👤 **Telegram ID:** `{user_id}`\n🔒 Bu istifadəçi artıq bloklanmış stikerləri göndərə bilməz.", parse_mode='markdown')
        add_log(f"Stiker icazə silmə: {user_id} adlı istifadəçi icazəli istifadəçilər siyahısından silindi", "info")

    @client.on(events.NewMessage(incoming=True))
    async def sticker_blocker_handler(event):
        # Yalnız qruplarda işləsin
        if not event.is_group:
            return

        # Stiker mesajlarını yoxla
        if not event.message.sticker:
            return

        # Əvvəlcə userbot qrupda aktivdir mi yoxla
        from .group_activation import is_userbot_active_in_group
        if not await is_userbot_active_in_group(event.chat_id):
            return

        sticker_settings = load_sticker_blocker_settings()
        active_groups = sticker_settings.get("groups", [])

        if event.chat_id not in active_groups:
            return

        try:
            sender = await event.get_sender()

            if not sender or not hasattr(sender, 'id'):
                print("⚠️ Sender məlumatı əldə edilə bilmədi (sticker blocker)")
                return

            # Məşədi və icazəli istifadəçilər stiker göndərə bilər
            allowed_users = load_allowed_users()
            if sender.id == MESHEDI_ID or sender.id in allowed_users:
                return

            sticker_id = event.message.sticker.id
            locked_stickers = load_locked_stickers()

            if str(sticker_id) in locked_stickers:
                try:
                    await event.delete()
                    print(f"🔒 Bloklanmış stiker silindi. Göndərən: {sender.first_name or 'Unknown'} (ID: {sender.id})")

                    sender_name = sender.first_name or "İstifadəçi"
                    clean_name = "".join(c for c in sender_name if c.isalnum() or c.isspace())[:20]
                    if not clean_name.strip():
                        clean_name = "İstifadəçi"

                    sender_mention = f"[{clean_name}](tg://user?id={sender.id})"

                    try:
                        await client.send_message(event.chat_id, f"🔒 {sender_mention} Bu stikeri yalnız Məşədi göndərə bilər!", parse_mode='markdown')
                    except Exception as mention_error:
                        await client.send_message(event.chat_id, f"🔒 {clean_name} Bu stikeri yalnız Məşədi göndərə bilər!")

                except Exception as delete_error:
                    print(f"❌ Stiker silinərkən xəta: {delete_error}")

        except Exception as e:
            print(f"❌ Stiker blocker xətası: {e}")