# Qrup aktivləşdirmə funksiyaları və tag əmrləri inteqrasiyası
from telethon import events
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch, ChannelParticipantsAdmins
import asyncio
import random
import time
from datetime import datetime
import os
import json
from .log_server import add_log

# Random message templates for rtag command
rtag_messages = [
    'Bu gün çay növbəsi {mention} ☕',
    'Səssizliyi poz, {mention} 🎤',
    'Yaz, yoxsa yazdırarıq, {mention} 😎',
    'Gizlənpaçda tapıldın, {mention} 😂',
    'Bot deyir ki, {mention} danışmasa qrup susacaq 😶',
    'Bu dəfə gizlənə bilmədin, {mention} 🔍',
    'Masa başında boş yer var: {mention} 🍽️',
    'Söhbətə səninlə başlayaq, {mention} 🗣️',
    'Qrupun ciyəri, nəfəsi, ruhu: {mention} 😇',
    'Hamının gözü səndədi, {mention} 👀',
    'Botun qurbanı oldun, {mention} 😈',
    'Bu günün şanslısı... yox e, bədbəxti: {mention} 😅',
    'Qrupda kim qalıb? {mention} hələ yazmayıb 🤔',
    'Bu sualı yalnız {mention} cavablandıra bilər 💬',
    'Məşədi susur, amma {mention} danışmalıdır 🔥',
    'Səni gözləyirik, {mention} ⏳',
    'Səssiz qalmayasan inşallah, {mention} 🤫',
    'Yaxşılığa yozduq səni, {mention} 🌈',
    'Bayaqdan səni seçmək istəyirdik, nəhayət sıra gəldi: {mention} 🎯',
    'Bu qrupun ümidi sənsən, {mention} 🙌',
    'İmtahanda ilk sualı sən cavabla, {mention} ✍️',
    'Bu qədər səssizlikdən sonra səhnəyə çıx: {mention} 🎭',
    'Əyləncə başlasın! İlk aktyorumuz: {mention} 🎬',
    'Təbii ki, {mention} cavab verəcək – kim olacaq ki? 😜',
    'Bot soruşur: {mention} online-dı? ✅',
    'Bu səssizlik qadağandır, {mention} səsini çıxar 🔊',
    'Söz sənin əlindədi, {mention} 🎙️',
    'Qaçmaq olmur, {mention} 😏',
    'Gecikdinsə, cavab ver də indi, {mention} ⌛',
    'Qrupun günah keçisi: {mention} 🐐',
    'Hamı susdu, səni gözləyir: {mention} 🤐',
    'Səninlə daha maraqlı olacaq, {mention} 😍',
    'Hər dəfə səni seçmirik axı, bu dəfə şanslısan: {mention} 💡',
    'Yenə düşdü sənə, {mention} 😬',
    'Bu gün heç kim səni xilas etməyəcək, {mention} 🛑',
    'Qrup səni tağladı, {mention} 😆',
    'Random seçsək də, təsadüf deyil: {mention} 🌀',
    'Bəli bəli, məhz sən! {mention} 😇',
    'Səndən başlayırıq, {mention} 🧠',
    'Gəlin alqışlayaq {mention} 👏',
    'Bu qrupda səssizliyə yer yoxdur, {mention} 🔇'
]

active_tagging = {}
active_rtagging = {}
cancel_tagging = {}  # Her chat üçün active proseslərin sayını saxlayır

MESHEDI_ID = 5257767076

async def is_group_active(chat_id):
    """Qrupun aktiv olub olmadığını yoxlayır."""
    try:
        from .group_activation import is_userbot_active_in_group
        return await is_userbot_active_in_group(chat_id)
    except:
        return True  # Xəta varsa, default olaraq aktiv hesab et

def register_tag_handlers(client):

    @client.on(events.NewMessage(pattern=r'\.rtag'))
    async def rtag_handler(event):
        """Bütün istifadəçiləri yumorlu mesajlarla tag edir"""
        if not await is_group_active(event.chat_id):
            return

        await event.delete()

        try:
            # Əmr göndərənin məlumatlarını al
            sender = await event.get_sender()
            sender_name = sender.first_name or "İstifadəçi"
            sender_mention = f"[{sender_name}](tg://user?id={sender.id})"

            # İcazə yoxlaması
            is_authorized = False
            if sender.id == MESHEDI_ID:
                is_authorized = True
            else:
                # Admin yoxlaması
                try:
                    async for admin in client.iter_participants(event.chat_id, filter=ChannelParticipantsAdmins):
                        if admin.id == sender.id:
                            is_authorized = True
                            break
                except:
                    pass

            if not is_authorized:
                await event.reply(f"{sender_mention} 🚫 Bu əmri Məşədi və adminlər yaza bilər!", parse_mode='markdown')
                return

            # Başlama xəbərdarlığı göstər
            await event.reply(f"{sender_mention} 🏷️ Tağlama başladı!", parse_mode='markdown')

            # Qrupda olan bütün istifadəçiləri al (botlar və silinmiş hesablar istisna)
            participants = await client.get_participants(event.chat_id)
            users = [p for p in participants if not p.bot and not p.deleted and p.id != sender.id]

            if not users:
                await event.reply("❌ Qrupda tag ediləcək heç kim yoxdur")
                return

            # Cancel sistemi üçün
            if event.chat_id not in cancel_tagging:
                cancel_tagging[event.chat_id] = 0
            cancel_tagging[event.chat_id] += 1

            # Mesajların surətini yaradın ki, təkrar olmasın
            available_messages = rtag_messages.copy()
            tagged_count = 0

            # Hər istifadəçini fərqli mesajla tag et
            for user in users:
                # Cancel yoxlaması - mesaj göstərmədən sadəcə çıx
                if cancel_tagging.get(event.chat_id, 0) <= 0:
                    return

                # Əgər mesajlar bitibsə, yenidən doldur
                if not available_messages:
                    available_messages = rtag_messages.copy()

                # Random mesaj seç və siyahıdan çıxar
                random_message = random.choice(available_messages)
                available_messages.remove(random_message)

                # İstifadəçini mention et
                mention = f"[{user.first_name}](tg://user?id={user.id})"

                # Mesajı formatla və göndər
                final_message = random_message.format(mention=mention)
                await event.reply(final_message, parse_mode='markdown')
                tagged_count += 1

                # 1 saniyə gözlə
                await asyncio.sleep(1)

            # Prosesi təmizlə
            if event.chat_id in cancel_tagging:
                cancel_tagging[event.chat_id] = max(0, cancel_tagging[event.chat_id] - 1)

            # Bitirmə xəbərdarlığı
            await event.reply(f"✅ Random tağlama tamamlandı! ({tagged_count} nəfər tag edildi)", parse_mode='markdown')

        except Exception as e:
            await event.reply(f"❌ Xəta baş verdi: {str(e)}")

    @client.on(events.NewMessage(pattern=r'\.tagall'))
    async def tagall_handler(event):
        """Qrupda hamını bir-bir tag edir - adminlər və Məşədi"""
        if not await is_group_active(event.chat_id):
            return
        await event.delete()

        try:
            sender = await event.get_sender()

            # Admin yoxlaması
            is_admin = False
            if sender.id == MESHEDI_ID:
                is_admin = True
            else:
                # Qrupda admin olub-olmadığını yoxla
                try:
                    async for admin in client.iter_participants(event.chat_id, filter=ChannelParticipantsAdmins):
                        if admin.id == sender.id:
                            is_admin = True
                            break
                except:
                    pass

            if not is_admin:
                sender_mention = f"[{sender.first_name}](tg://user?id={sender.id})"
                await event.reply(f"{sender_mention} 🚫 Bu əmri Məşədi və adminlər yaza bilər!", parse_mode='markdown')
                return

            # Əmrdən sonrakı mətni al
            command_parts = event.raw_text.split(maxsplit=1)
            extra_text = command_parts[1] if len(command_parts) > 1 else ""

            participants = await client.get_participants(event.chat_id)
            users = [p for p in participants if not p.bot and not p.deleted and p.id != sender.id]

            if not users:
                await event.reply("❌ Qrupda tag ediləcək heç kim yoxdur")
                return

            # Tağlama prosesini başlat
            if event.chat_id not in cancel_tagging:
                cancel_tagging[event.chat_id] = 0
            cancel_tagging[event.chat_id] += 1

            # Başlama xəbərdarlığı
            sender_name = sender.first_name or "Admin"
            sender_mention = f"[{sender_name}](tg://user?id={sender.id})"
            await event.reply(f"{sender_mention} 🏷️ Tağlama başladı!", parse_mode='markdown')

            # Hər istifadəçini ayrı-ayrı tag et
            tagged_count = 0
            for user in users:
                # Cancel yoxlaması - mesaj göstərmədən sadəcə çıx
                if cancel_tagging.get(event.chat_id, 0) <= 0:
                    return

                mention = f"[{user.first_name}](tg://user?id={user.id})"
                if extra_text:
                    message = f"{mention} {extra_text}"
                else:
                    message = mention

                await event.reply(message, parse_mode='markdown')
                tagged_count += 1

                # 1 saniyə gözlə
                await asyncio.sleep(1)

            # Prosesi təmizlə
            if event.chat_id in cancel_tagging:
                cancel_tagging[event.chat_id] = max(0, cancel_tagging[event.chat_id] - 1)

            # Bitirmə xəbərdarlığı
            await event.reply("✅ Tağlama tamamlandı!", parse_mode='markdown')

        except Exception as e:
            await event.reply(f"❌ Xəta baş verdi: {str(e)}")

    @client.on(events.NewMessage(pattern=r'\.cancel'))
    async def cancel_handler(event):
        """Tağlama prosesini dayandır - hamı istifadə edə bilər"""
        await event.delete()

        try:
            # Cancel əməliyyatını icra et
            if event.chat_id in cancel_tagging and cancel_tagging[event.chat_id] > 0:
                # Bütün prosesləri dayandır
                cancel_tagging[event.chat_id] = 0
                # Yalnız bir dəfə mesaj göstər
                await event.reply("🛑 Tağlama prosesi dayandırıldı!")
            else:
                await event.reply("⚠️ **Hazırda aktiv tağlama prosesi yoxdur!**\n\nDayandırılacaq heç nə yoxdur.")

        except Exception as e:
            await event.reply(f"❌ Xəta baş verdi: {str(e)}")