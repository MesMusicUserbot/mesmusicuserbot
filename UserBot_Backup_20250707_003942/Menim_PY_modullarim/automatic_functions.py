from telethon import events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import os
import json
import random
from datetime import datetime, timezone, timedelta
from .log_server import add_log

MEDIA_LOG_FILE = "Menim_JSON_fayillarim/media_log.json"

def load_media_log():
    # JSON qovluğunu yarat
    os.makedirs("Menim_JSON_fayillarim", exist_ok=True)

    if not os.path.exists(MEDIA_LOG_FILE):
        return []
    with open(MEDIA_LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_media_log(data):
    # JSON qovluğunu yarat
    os.makedirs("Menim_JSON_fayillarim", exist_ok=True)

    with open(MEDIA_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def register_automatic_handlers(client):
    @client.on(events.NewMessage(incoming=True))
    async def media_saver_handler(event):
        # Yalnız PM-lərdə (şəxsi mesajlarda) işləsin
        if event.is_group or event.is_channel:
            return

        message = event.message
        media = message.media

        # Yalnız view-once (tək səfərlik) media saxlanacaq
        if not media or not hasattr(media, 'ttl_seconds') or media.ttl_seconds is None:
            return  # Adi şəkil/video saxlanmayacaq, yalnız view-once

        # Yalnız foto, video və səs fayllarını saxla
        if isinstance(media, MessageMediaPhoto):
            pass
        elif isinstance(media, MessageMediaDocument):
            if media.document:
                mime_type = media.document.mime_type or ""
                if mime_type.startswith('video/'):
                    if mime_type == 'video/webm':
                        if media.document.size < 5 * 1024 * 1024:
                            return
                        for attr in media.document.attributes:
                            if hasattr(attr, 'supports_streaming') and not attr.supports_streaming:
                                return
                    pass
                elif mime_type.startswith('audio/') or any(attr.voice for attr in media.document.attributes if hasattr(attr, 'voice')):
                    pass
                else:
                    return
        else:
            return

        try:
            os.makedirs("saved_media", exist_ok=True)

            sender = await event.get_sender()

            if not sender:
                print("⚠️ Sender məlumatı əldə edilə bilmədi (media saver)")
                return

            sender_name = getattr(sender, 'first_name', None) or "Naməlum"
            sender_id = getattr(sender, 'id', None)
            # Bakı vaxtı (UTC+4)
            baku_tz = timezone(timedelta(hours=4))
            timestamp = datetime.now(baku_tz).strftime("%Y-%m-%d %H:%M:%S")

            file_name = f"saved_media/{message.id}_{random.randint(1000,9999)}"
            path = await client.download_media(message, file=file_name)

            # Faylı istifadəçinin "Saved Messages" bölməsinə göndər
            await client.send_file("me", path, caption=f"📸 {sender_name} tərəfindən göndərilən view-once media\n⏰ {timestamp}", force_document=False)

            # Loga yaz
            media_log = load_media_log()
            media_log.append({
                "sender_id": sender_id,
                "sender_name": sender_name,
                "file_path": path,
                "timestamp": timestamp,
                "message_id": message.id
            })
            save_media_log(media_log)

            print(f"📥 Media saxlanıldı: {sender_name} - {timestamp}")
            add_log(f"View-once media saxlanıldı: {sender_name} - {timestamp}", "info")


        except Exception as e:
            print(f"Media saxlanarkən xəta: {e}")