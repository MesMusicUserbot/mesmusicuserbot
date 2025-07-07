
from telethon import events
from telethon.tl import functions
import asyncio
import os
import pickle

MESHEDI_ID = 5257767076
ORIGINAL_PHOTO_PATH = "original_profile_photo.jpg"
PROFILE_BACKUP_FILE = "original_profile.pkl"

def save_original_profile(profile_data):
    with open(PROFILE_BACKUP_FILE, "wb") as f:
        pickle.dump(profile_data, f)

def load_original_profile():
    if not os.path.exists(PROFILE_BACKUP_FILE):
        return None
    with open(PROFILE_BACKUP_FILE, "rb") as f:
        return pickle.load(f)

def register_profile_handlers(client):
    @client.on(events.NewMessage(pattern=r"\.klon"))
    async def clone_profile(event):
        await event.delete()

        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await client.send_message(event.chat_id, f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            return

        reply = await event.get_reply_message()
        if not reply:
            await client.send_message(event.chat_id, "🔁 Klonlama üçün kiminsə mesajına reply et.")
            return

        target = await reply.get_sender()
        self_user = await client.get_me()
        full_self = await client(functions.users.GetFullUserRequest(self_user.id))

        # Ad, bio profil məlumatlarını yadda saxla
        save_original_profile({
            "first_name": self_user.first_name,
            "last_name": self_user.last_name,
            "about": full_self.full_user.about or "",
        })

        # Orijinal profil şəklini yadda saxla
        photos = await client.get_profile_photos(self_user)
        if photos.total > 0:
            await client.download_media(photos[0], file=ORIGINAL_PHOTO_PATH)

        try:
            # Target istifadəçinin real Telegram profil məlumatlarını al
            target_entity = await client.get_entity(target.id)
            target_full = await client(functions.users.GetFullUserRequest(target.id))

            # Real Telegram profil adını götür
            first_name = target_entity.first_name or ""
            last_name = target_entity.last_name or ""
            bio = target_full.full_user.about or ""

            # Göstərmək üçün display name yarat
            display_name = f"{first_name} {last_name}".strip()
            if not display_name and target_entity.username:
                display_name = f"@{target_entity.username}"
            elif not display_name:
                display_name = "Naməlum"

            # Profil məlumatlarını yenilə
            await client(functions.account.UpdateProfileRequest(
                first_name=first_name,
                last_name=last_name,
                about=bio
            ))

            # Klon profil şəklini yüklə
            target_photos = await client.get_profile_photos(target)
            if target_photos.total > 0:
                try:
                    downloaded_photo = await client.download_media(target_photos[0], file="clone_photo")

                    file_size = os.path.getsize(downloaded_photo)
                    if file_size < 500:
                        await client.send_message(event.chat_id, "⚠️ Target istifadəçinin profil şəkli çox kiçikdir, klonlana bilməz.")
                    elif file_size > 10 * 1024 * 1024:
                        await client.send_message(event.chat_id, "⚠️ Target istifadəçinin profil şəkli çox böyükdür, klonlana bilməz.")
                    else:
                        import shutil
                        final_photo = "clone_photo_final.jpg"
                        shutil.copy2(downloaded_photo, final_photo)

                        with open(final_photo, "rb") as photo_file:
                            uploaded_file = await client.upload_file(photo_file)
                            await client(functions.photos.UploadProfilePhotoRequest(
                                file=uploaded_file
                            ))

                        if os.path.exists(downloaded_photo):
                            os.remove(downloaded_photo)
                        if os.path.exists(final_photo):
                            os.remove(final_photo)

                except Exception as photo_error:
                    await client.send_message(event.chat_id, f"⚠️ Profil şəkli klonlanarkən xəta: {str(photo_error)}")

            msg = await client.send_message(event.chat_id, f"✅ {display_name} adlı istifadəçinin profili klonlandı.")
            await asyncio.sleep(0)
            await msg.delete()
        except Exception as e:
            await client.send_message(event.chat_id, f"⚠️ Klonlaşdırma alınmadı: {e}")

    @client.on(events.NewMessage(pattern=r"\.qaytar"))
    async def restore_profile(event):
        await event.delete()

        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await client.send_message(event.chat_id, f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            return

        backup = load_original_profile()
        if not backup:
            await client.send_message(event.chat_id, "❌ Əvvəlki profil məlumatları tapılmadı.")
            return

        try:
            # Klon profil şəklini sil
            my_photos = await client.get_profile_photos('me')
            if my_photos.total > 0:
                await client(functions.photos.DeletePhotosRequest(id=[my_photos[0]]))

            # Əvvəlki profil şəklini geri yüklə
            if os.path.exists(ORIGINAL_PHOTO_PATH):
                try:
                    file_size = os.path.getsize(ORIGINAL_PHOTO_PATH)
                    if file_size >= 1024:
                        with open(ORIGINAL_PHOTO_PATH, "rb") as photo_file:
                            await client(functions.photos.UploadProfilePhotoRequest(
                                file=await client.upload_file(photo_file)
                            ))
                    else:
                        await client.send_message(event.chat_id, "⚠️ Əvvəlki profil şəkli çox kiçikdir, bərpa edilə bilməz.")
                except Exception as restore_error:
                    await client.send_message(event.chat_id, f"⚠️ Profil şəkli bərpa edilərkən xəta: {restore_error}")

            # Ad, soyad, bio bərpa
            await client(functions.account.UpdateProfileRequest(
                first_name=backup["first_name"],
                last_name=backup["last_name"],
                about=backup["about"]
            ))

            msg = await client.send_message(event.chat_id, "🔄 Profil tam şəkildə orijinal vəziyyətinə qaytarıldı.")
            await asyncio.sleep(0.1)
            await msg.delete()

            # Backup fayllarını təmizlə
            if os.path.exists(PROFILE_BACKUP_FILE):
                os.remove(PROFILE_BACKUP_FILE)
            if os.path.exists(ORIGINAL_PHOTO_PATH):
                os.remove(ORIGINAL_PHOTO_PATH)

        except Exception as e:
            await client.send_message(event.chat_id, f"⚠️ Bərpa zamanı xəta baş verdi: {e}")
