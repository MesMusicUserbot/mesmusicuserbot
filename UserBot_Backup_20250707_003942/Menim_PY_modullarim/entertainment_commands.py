# Adding the is_userbot_active_in_group import and correcting the group activation check.
from telethon import events
import random
import asyncio
from datetime import datetime, timedelta
from .log_server import add_log
import time
import difflib
from .group_activation import is_userbot_active_in_group

MESHEDI_ID = 5257767076

# Global variables for fal command
used_fortunes = []
last_fal_times = {}

async def is_group_active(chat_id):
    """Qrupun aktiv olub olmadığını yoxlayır."""
    try:
        return await is_userbot_active_in_group(chat_id)
    except:
        return True  # Xəta varsa, default olaraq aktiv hesab et

async def find_user_flexible(client, search_term):
    try:
        if search_term.startswith('@'):
            return await client.get_entity(search_term)
        else:
            try:
                return await client.get_entity(int(search_term))
            except ValueError:
                try:
                    return await client.get_entity(f"@{search_term}")
                except:
                    try:
                        contacts = await client.get_contacts()
                        lowered_search = search_term.lower().strip()
                        best_match = None
                        highest_ratio = 0.0

                        for contact in contacts:
                            full_name = f"{contact.first_name or ''} {contact.last_name or ''}".strip()
                            for name_variant in [contact.first_name, contact.last_name, full_name]:
                                if not name_variant:
                                    continue
                                ratio = difflib.SequenceMatcher(None, lowered_search, name_variant.lower()).ratio()
                                if ratio > highest_ratio and ratio > 0.6:
                                    highest_ratio = ratio
                                    best_match = contact

                        return best_match
                    except:
                        return None
    except Exception as e:
        print(f"User axtarış xətası: {e}")
        return None

def register_entertainment_handlers(client):
    @client.on(events.NewMessage(pattern=r'\.fal'))
    async def fal_command(event):
        """Fal baxır və nəticəni göstərir"""
        # Qrup aktivləşdirmə yoxlaması
        if event.is_group and not await is_group_active(event.chat_id):
            return

        await event.delete()
        global used_fortunes, last_fal_times

        user_id = event.sender_id
        now = datetime.now()

        # Məşədi limitsiz, digərləri 5 dəqiqəlik limit
        if user_id != MESHEDI_ID:
            last_time = last_fal_times.get(user_id)
            if last_time and (now - last_time).total_seconds() < 300:
                sender = await event.get_sender()
                sender_mention = f"[{sender.first_name}](tg://user?id={sender.id})"
                await event.reply(
                    f"⏳ {sender_mention} Sən artıq fal açmısan. Zəhmət olmasa 5 dəqiqə sonra yenidən cəhd et.",
                    parse_mode='markdown'
                )
                return
            last_fal_times[user_id] = now

        fortunes = [
            "Bu gün sənə mesaj gələcək... amma spam olacaq 😂",
            "İşlərin yoluna düşəcək – sadəcə yatmağa davam et 😴",
            "Səni kimsə izləyir... internetdə, əlbəttə 👀",
            "Pul gələcək... amma qonşuya 😅",
            "Əgər bu mesajı 3 nəfərə göndərsən... heç nə olmayacaq 😈",
            "Gələcəkdə 3 seçim olacaq... sən səhv olanı seçəcəksən 😆",
            "Bu gün səni ancaq çay xilas edə bilər ☕",
            "Bir vaxtlar xəyalların var idi... indi botla danışırsan 🤖",
            "Səninlə bağlı qərar verildi... təxirə salındı 📆",
            "Tələb etdiyin uğur serverdə gecikir 🔄",
            "Yuxuda gördüyün o qız... sadəcə botdur 😬",
            "Sevgili axtarma... o səni axtarmır 💔",
            "Qismətində çox şey var... amma indi yox 😅",
            "Bu həftə səni stalklayan biri sənin postuna like edəcək 😲",
            "Özünü dəyişmək istəyirsənsə, şifrə ilə başla 🔐",
            "Bu gün heç nə etməsən belə, uğursuzluq səni tapacaq 🤷",
            "Arzuların çin olacaq... amma başqa adla ✨",
            "Birisi səni xatırlayacaq... sonra unudacaq 😌",
            "Falda çıxıb: bu gün wifi zəif olacaq 📶",
            "İçindəki səs susub... sən danışmalısan 🧘",
            "Bu gün sənin günündür! – amma keçdi ⏳",
            "Əgər bugün çox düşünürsənsə, sabah da eyni olacaq 💭",
            "Kimsə səni izləyir... amma kreditlə 📱",
            "Özünə inamın artacaq – səhv etdiyini başa düşəndə 🤦",
            "Biri sənə mesaj yazacaq... ama 'seen' edib cavab verməyəcək 🙄",
            "Sənin şansın elə böyükdü ki, heç bot belə təxmin edə bilmir 🤯",
            "Həyat bir filmdir... sənin hissən hələ başlamayıb 🎬",
            "Bu gün sənə 1 nəfər gülümsəyəcək... bəlkə güzgüdə 😅",
            "Əgər bu mesajı oxuyursansa, sən artıq seçilmisən... 'uşaq puluna' 😅",
            "Qrupun ən sakit adamı bu gün danışacaq... və sən susacaqsan 🤐"
        ]

        # İstifadə olunmamış cümlələri tapırıq
        available_fortunes = [f for f in fortunes if f not in used_fortunes]

        # Əgər hamısı istifadə olunubsa, sıfırla və yenidən başla
        if not available_fortunes:
            used_fortunes = []
            available_fortunes = fortunes.copy()

        # Random seç
        fortune = random.choice(available_fortunes)
        used_fortunes.append(fortune)

        # Kimə aid olduğunu təyin et
        reply = await event.get_reply_message()
        message_parts = event.message.message.split()

        if reply and reply.sender_id:
            user = await client.get_entity(reply.sender_id)
            name = f"[{user.first_name}](tg://user?id={user.id})"
        elif len(message_parts) > 1:
            try:
                mentioned = await client.get_entity(message_parts[1])
                name = f"[{mentioned.first_name}](tg://user?id={mentioned.id})"
            except:
                sender = await event.get_sender()
                name = f"[{sender.first_name}](tg://user?id={sender.id})"
        else:
            sender = await event.get_sender()
            name = f"[{sender.first_name}](tg://user?id={sender.id})"

        await event.reply(f"🔮 Fal açıldı: {name}\n\n{fortune}",
                          parse_mode='markdown')
        add_log(f"Fal açıldı: {name} - {fortune}", "info")

    @client.on(events.NewMessage(pattern='\.esq'))
    async def esq_handler(event):
        await event.delete()
        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bunu yalnız Məşədi yoxlaya bilər.", parse_mode='markdown')
            return

        # Reply mesajı yoxla
        reply = await event.get_reply_message()
        message_parts = event.message.message.split()

        user1 = None
        user2 = None

        # Birinci istifadəçini tap
        if reply and reply.sender_id:
            user1 = await client.get_entity(reply.sender_id)
        elif len(message_parts) >= 2:
            user1 = await find_user_flexible(client, message_parts[1])
            if not user1:
                await event.reply(f"❌ '{message_parts[1]}' istifadəçisini tapmaq mümkün olmadı.\n\n🔍 Axtardıqlarım:\n• @{message_parts[1]} username-i\n• ID nömrəsi\n• Kontaktlarda ad axtarışı\n\n💡 Məsləhət:\n• Reply et mesaja\n• Real @username yaz\n• ID nömrəsi yaz\n• Tam adı yaz")
                return
        else:
            await event.reply("İstifadə:\n• `.esq` (reply edərək)\n• `.esq @username` \n• `.esq @user1 @user2`\n• `.esq userid1 userid2`\n• `.esq tam_ad`")
            return

        # İkinci istifadəçini tap
        if len(message_parts) >= 3:
            user2 = await find_user_flexible(client, message_parts[2])
            if not user2:
                await event.reply(f"❌ '{message_parts[2]}' istifadəçisini tapmaq mümkün olmadı.\n\n🔍 Axtardıqlarım:\n• @{message_parts[2]} username-i\n• ID nömrəsi\n• Kontaktlarda ad axtarışı\n\n💡 Məsləhət:\n• Real @username yaz\n• ID nömrəsi yaz\n• Tam adı yaz")
                return
        else:
            user2 = sender

        mention1 = f"[{user1.first_name}](tg://user?id={user1.id})"
        mention2 = f"[{user2.first_name}](tg://user?id={user2.id})"

        # 40% ehtimal ilə 80%+ nəticə
        if random.random() < 0.4:
            final_percent = random.randint(80, 100)
        else:
            final_percent = random.randint(0, 79)

        # Steps yaratarkən minimum 1 elementi olduğundan əmin ol
        if final_percent <= 1:
            steps = [final_percent]
        else:
            num_steps = min(6, final_percent - 1)
            if num_steps > 0:
                steps = sorted(random.sample(range(1, final_percent), num_steps)) + [final_percent]
            else:
                steps = [final_percent]

        emojis = ["💔", "❤️", "💞", "🔥", "💍"]

        def progress_bar(percent):
            filled = int(percent / 10)
            empty = 10 - filled
            return "▰" * filled + "▱" * empty

        msg = await event.reply(f"❤️ Eşq faizi hesablanır...\n\n{mention1} ❤️ {mention2}", parse_mode='markdown')

        for p in steps:
            bar = progress_bar(p)
            emoji = random.choice(emojis)
            await asyncio.sleep(0.35)
            await msg.edit(f"{emoji} Eşq faizi: {p}%\n[{bar}]\n\n{mention1} ❤️ {mention2}", parse_mode='markdown')

        if final_percent >= 90:
            comment = "💍 Bunlar evlənməsə, bu bot bağlanacaq!"
        elif final_percent >= 70:
            comment = "🔥 Yanıblar! Gözlərdən məlum olur."
        elif final_percent >= 50:
            comment = "💞 Bir şeylər var... amma bir az riskli."
        elif final_percent >= 30:
            comment = "🤔 Hmm... bəlkə də bir az dostca."
        elif final_percent >= 10:
            comment = "🥶 Çox da ümid etmə, dondurmadı bu?"
        else:
            comment = "❌ Eşq yoxdu. Bot belə deyirsə, boşdu məsələ."

        await asyncio.sleep(0.6)
        await msg.edit(f"❤️ Eşq faizi: {final_percent}%\n[{progress_bar(final_percent)}]\n\n{mention1} ilə {mention2} arasında:\n{comment}", parse_mode='markdown')
        add_log(f"Eşq faizi hesablandı: {mention1} - {mention2} = {final_percent}%", "info")