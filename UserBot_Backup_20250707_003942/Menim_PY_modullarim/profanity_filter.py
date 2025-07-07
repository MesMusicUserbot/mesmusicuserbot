from telethon import events
from telethon.tl.types import ChannelParticipantsAdmins
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
import json
import os
import re
import asyncio
from .log_server import add_log
from .common_utils import JSONManager
from .group_activation import is_userbot_active_in_group

MESHEDI_ID = 5257767076
PROFANITY_FILTER_FILE = "Menim_JSON_fayillarim/profanity_settings.json"
MESHBOT_USERBOT_ID = 4831999346

def load_profanity_settings():
    try:
        if os.path.exists(PROFANITY_FILTER_FILE):
            with open(PROFANITY_FILTER_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Profanity settings load error: {e}")

    return {"enabled": True, "groups": []}

def save_profanity_settings(data):
    try:
        os.makedirs(os.path.dirname(PROFANITY_FILTER_FILE), exist_ok=True)
        with open(PROFANITY_FILTER_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Profanity settings save error: {e}")

# Güclü söyüş sözlüyü
STRONG_PROFANITY = {
    'strong': [
        'orospu', 'orospuçucu', 'orospucocugu', 'orospucocu', 'orspu', 'orsbum', 'orusp', 'orosp',
        'piç', 'pic', 'pezevenk', 'pezeveng', 'götlük', 'gotluk', 'götbaşı', 
        'götveren', 'götsəvər', 'götsiken', 'götümdə', 'götünü', 'götünə', 'göt', 'gotun', 'gotverən', 'gotune',
        'siktir', 'sikdir', 'sikerim', 'sikiyim', 'sikisek', 'sikişek', 'sik', 'sikim', 'sikər', 'sikəcəm',
        'amcık', 'amcıq', 'amcığ', 'amcık', 'am', 'amını', 'amınakoyim', 'amına', 'amciq', 'amq',
        'yarrak', 'yarrag', 'yarraq', 'yarramı', 'yarrağı', 'yarrağım',
        'daşşak', 'daşşaq', 'dasak', 'daşağı', 'daşşağı', 'testis', 'daşaq', 'dassaq',
        'sikmek', 'sikdim', 'siktim', 'sikecem', 'sikərəm', 'sikişmek', 'sikilmişəm', 'sikməm',
        'sikməliyəm', 'sikməliyik',
        'döl', 'dol', 'sperm', 'boşalmaq', 'boşaldım',
        'fahişə', 'fahise', 'fahişəlik', 'qəhbə', 'qahbe', 'qəhbəlik', 'qehbe',
        'gey', 'homo', 'homoseksual',
        'pederast', 'pedofil',
        'götünü', 'götünə', 'götündə', 'gotunu', 'gotune', 'gotunde',
        'kaltak', 'kancık', 'kancik', 'sürtük', 'surtuk', 'sürtüklük', 'qancıq', 'qanciq',
        'cındır', 'cindir', 'dalbayob', 'gijdillaq', 'fuck', 'fucker', 'qoduğ',
        'vajina', 'sikdir', 'trans', 'lox', 'amk', 'pidaraz', 'bicbala',
        'qandon', 'blət', 'soxum', 'dıllaq', 'dıllağ', 'pidr', 'penis', 'pox'
    ],

    'combinations': [
        'amına koy', 'amina koy', 'amına qoy', 'amina qoy',
        'götünə sok', 'gotune sok', 'götündən çıxar', 'gotunden cixar',
        'sikə sikə', 'sike sike', 'sikərəm səni', 'sikerem seni',
        'ananın amı', 'ananin ami', 'ananı sikim', 'anani sikim',
        'allah siksin', 'allah sikin', 'tanrı siksin',
        'dünya siksin', 'dunye sisin', 'heç kim sikməsin',
        'özünü sik', 'ozunu sik', 'öz özünü', 'oz ozunu',
        'məni yala', 'meni yala', 'götümü yala', 'gotumu yala',
        'yarrağımı ye', 'yarragimi ye', 'sikimə gəl', 'sikime gel'
    ],

    'variations': [
        'orxpu', 'orxbu', '0r0spu', '0rospu', 'or0spu', 'oroşpu',
        'p1c', 'p1ç', 'picc', 'pijç', 'piş', 'pıç',
        's1kt1r', 's1kd1r', 'sıktır', 'sıkdır', 'şiktir', 'şikdir',
        'amj1k', 'amj1q', 'amcıgg', 'amşık', 'amşıq',
        'y4rr4k', 'y4rr4q', 'yarr4k', 'yarrax', 'yarrağ',
        'g0t', 'g0tl0k', 'gödt', 'göt', 'qöt', 'qot',
        'd4ss4k', 'daşş4k', 'daşşax', 'daşşagg',
        'f4hise', 'f4h1se', 'fahiş3', 'qəhb3', 'qahb3'
    ]
}

# Duplicate code removed - using unified functions above

def check_profanity(text):
    """Mətndə söyüş var mı yoxla"""
    if not text:
        return False

    text_lower = text.lower()

    # İstisna sözləri yoxla
    for exception in EXCEPTION_WORDS:
        if exception in text_lower:
            return False

    # Azərbaycan söyüşləri yoxla
    for word in PROFANITY_WORDS['azerbaijani']:
        if word in text_lower:
            return True

    return False

def register_profanity_handlers(client):

    @client.on(events.NewMessage)
    async def profanity_filter(event):
        """Söyüş filtri"""
        if not event.message or not event.message.text:
            return

        settings = load_profanity_settings()

        if not settings.get("enabled", False):
            return

        # İstisna istifadəçilər
        if event.sender_id in settings.get("excluded_users", []):
            return

        # İstisna chatlar
        if event.chat_id in settings.get("excluded_chats", []):
            return

        # Söyüş yoxla
        if check_profanity(event.message.text):
            try:
                if settings.get("auto_delete", True):
                    await event.delete()

                if settings.get("warn_user", True):
                    await event.reply("⚠️ Söyüş istifadə etmək qadağandır!")

            except Exception as e:
                if "readonly database" in str(e):
                    print(f"⚠️ Database readonly xətası - profanity filter deaktiv edildi")
                    return
                else:
                    print(f"Söyüş filtr xətası: {e}")



EXCEPTION_WORDS = [
    'hamı', 'hami', 'hamını', 'haminin', 'haminə', 'hamina', 
    'hamini', 'hamini yox', 'hamini var', 'hamini deyil',
    'hamisini', 'hamisini yox', 'hamisinin',
    'hamısını', 'hamisini', 'hamimizi', 'hamimiz',
    'hamam', 'hamama', 'hamamda', 'hamami',
    'salam', 'salama', 'salamı', 'salamın',
    'adam', 'adama', 'adamı', 'adamın',
    'islam', 'islama', 'islamı', 'islamın',
    'amsterdam', 'qalam', 'qalama', 'qalamı',
    'reklam', 'reklamı', 'reklamın',
    'program', 'proqram', 'proqramı',
    'sistem', 'sistemi', 'sistemin',
    'problematik', 'matematik', 'tematik',
    'dramatik', 'avtomatik', 'diplomatik'
]

def check_profanity(text):
    """Mətnin söyüş olub olmadığını yoxlayır"""
    if not text:
        return False, []

    text_lower = text.lower().strip()
    found_profanities = []

    # Təmizləmə - emoji və xüsusi simvolları sil
    clean_text = re.sub(r'[^\w\s]', ' ', text_lower)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    words = clean_text.split()

    # İlk öncə istisna sözləri yoxla
    for exception in EXCEPTION_WORDS:
        if exception.lower() in text_lower:
            print(f"🟢 İstisna söz tapıldı: '{exception}' mətndə: '{text_lower}'")
            return False, []

    # Güclü söyüşləri yoxla
    for category in STRONG_PROFANITY.values():
        for profanity in category:
            profanity_lower = profanity.lower()

            if len(profanity_lower) <= 2:
                if profanity_lower in words:
                    found_profanities.append(profanity_lower)
                continue

            if len(profanity_lower) == 3:
                pattern = r'\b' + re.escape(profanity_lower) + r'\b'
                if re.search(pattern, clean_text):
                    found_profanities.append(profanity_lower)
                continue

            if len(profanity_lower) >= 4:
                if profanity_lower in words:
                    found_profanities.append(profanity_lower)
                    continue

                if profanity_lower in clean_text:
                    index = clean_text.find(profanity_lower)
                    while index != -1:
                        before_char = clean_text[index-1] if index > 0 else ' '
                        after_char = clean_text[index+len(profanity_lower)] if index+len(clean_text) else ' '

                        if not (before_char.isalpha() and after_char.isalpha()):
                            found_profanities.append(profanity_lower)
                            break

                        index = clean_text.find(profanity_lower, index + 1)

    for combination in STRONG_PROFANITY['combinations']:
        if combination.lower() in text_lower:
            found_profanities.append(combination.lower())

    return len(found_profanities) > 0, found_profanities

def register_profanity_handlers(client):
    @client.on(events.NewMessage(pattern=r"\.soyusstart"))
    async def enable_profanity_filter(event):
        await event.delete()

        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            return

        if not event.is_group:
            await event.reply("Bu əmr yalnız qruplarda işləyir.")
            return

        settings = load_profanity_settings()
        settings["enabled"] = True

        if "groups" not in settings:
            settings["groups"] = []

        if event.chat_id not in settings["groups"]:
            settings["groups"].append(event.chat_id)

        save_profanity_settings(settings)
        await event.reply("🤬 Söyüş filteri bu qrupda aktivləşdirildi! Söyüşlər avtomatik silinəcək.")

    @client.on(events.NewMessage(pattern=r"\.soyusstop"))
    async def disable_profanity_filter(event):
        await event.delete()

        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            return

        if not event.is_group:
            await event.reply("Bu əmr yalnız qruplarda işləyir.")
            return

        settings = load_profanity_settings()

        if "groups" in settings and event.chat_id in settings["groups"]:
            settings["groups"].remove(event.chat_id)

        save_profanity_settings(settings)
        await event.reply("🔇 Söyüş filteri bu qrupda dayandırıldı.")

    @client.on(events.NewMessage(pattern=r"\.soyusstatus"))
    async def profanity_filter_status(event):
        await event.delete()

        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            return

        settings = load_profanity_settings()
        is_enabled = settings.get("enabled", True)
        active_groups = settings.get("groups", [])

        status_text = f"🛡️ **Söyüş Filteri Statusu**\n\n"
        status_text += f"🔧 Ümumi status: {'✅ Aktiv' if is_enabled else '❌ Deaktiv'}\n"
        status_text += f"📊 Aktiv qruplar: {len(active_groups)} qrup\n"
        status_text += f"📚 Söyüş bazası: {len(STRONG_PROFANITY['strong']) + len(STRONG_PROFANITY['combinations']) + len(STRONG_PROFANITY['variations'])} söz\n"
        status_text += f"🛡️ İstisna sözlər: {len(EXCEPTION_WORDS)} söz\n\n"

        if event.is_group:
            is_active_here = event.chat_id in active_groups
            status_text += f"📍 Bu qrupda: {'✅ Aktiv' if is_active_here else '❌ Deaktiv'}\n\n"

        status_text += "**Əmrlər:**\n"
        status_text += "• `.soyusstart` - qrupda aktivləşdir\n"
        status_text += "• `.soyusstop` - qrupda dayandır\n"
        status_text += "• `.soyusstatus` - status göstər\n"
        status_text += "• `.soyuslist` - söyüş siyahısını göstər\n\n"
        status_text += "🤖 **Avtomatik İşləmə:** Sistem söyüşləri avtomatik aşkar edib silir və istifadəçini mute edir.\n"
        status_text += "🔇 **Avtomatik Mute:** Söyüş yazan istifadəçi avtomatik mute edilir."

        await event.reply(status_text, parse_mode='markdown')

    @client.on(events.NewMessage(pattern=r"\.soyuslist"))
    async def profanity_filter_list(event):
        await event.delete()

        sender = await event.get_sender()

        if sender.id != MESHEDI_ID:
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
            return

        # Birinci mesaj - Güclü söyüşlər
        response_text = "🤬 **SÖYÜŞ FİLTERİ BAZASI - TAM SİYAHI**\n\n"
        response_text += f"**💀 Güclü söyüşlər ({len(STRONG_PROFANITY['strong'])} ədəd):**\n"

        for i, word in enumerate(STRONG_PROFANITY['strong']):
            response_text += f"`{word}` "
            if (i + 1) % 4 == 0:
                response_text += "\n"

        response_text += "\n\n**📊 Bu güclü söyüşlərin hamısıdır.**"

        await event.reply(response_text, parse_mode='markdown')

        # İkinci mesaj - Kombinasiyalar
        combo_text = f"**🔗 Kombinasiyalar ({len(STRONG_PROFANITY['combinations'])} ədəd):**\n\n"
        for combo in STRONG_PROFANITY['combinations']:
            combo_text += f"`{combo}`\n"

        combo_text += "\n**📊 Bu kombinasiyaların hamısıdır.**"
        await event.respond(combo_text, parse_mode='markdown')

        # Üçüncü mesaj - Variasiyalar
        var_text = f"**🔄 Variasiyalar ({len(STRONG_PROFANITY['variations'])} ədəd):**\n\n"
        for i, var in enumerate(STRONG_PROFANITY['variations']):
            var_text += f"`{var}` "
            if (i + 1) % 4 == 0:
                var_text += "\n"

        var_text += "\n\n**📊 Bu variasiyaların hamısıdır.**"
        await event.respond(var_text, parse_mode='markdown')

        # Dördüncü mesaj - İstisna sözlər
        exc_text = f"**✅ İstisna sözlər ({len(EXCEPTION_WORDS)} ədəd):**\n"
        exc_text += "Bu sözlər söyüşə oxşasa da silinməyəcək:\n\n"
        for i, exc in enumerate(EXCEPTION_WORDS):
            exc_text += f"`{exc}` "
            if (i + 1) % 4 == 0:
                exc_text += "\n"

        exc_text += "\n\n**📊 Bu istisnaların hamısıdır.**"
        await event.respond(exc_text, parse_mode='markdown')

        # Beşinci mesaj - Ümumi statistika
        total_words = len(STRONG_PROFANITY['strong']) + len(STRONG_PROFANITY['combinations']) + len(STRONG_PROFANITY['variations'])
        final_text = f"**📊 ÜMUMI STATİSTİKA:**\n\n"
        final_text += f"💀 **Güclü söyüşlər:** {len(STRONG_PROFANITY['strong'])} ədəd\n"
        final_text += f"🔗 **Kombinasiyalar:** {len(STRONG_PROFANITY['combinations'])} ədəd\n"
        final_text += f"🔄 **Variasiyalar:** {len(STRONG_PROFANITY['variations'])} ədəd\n"
        final_text += f"✅ **İstisna sözlər:** {len(EXCEPTION_WORDS)} ədəd\n\n"
        final_text += f"🛡️ **CƏMI SÖYÜŞ BAZASI:** {total_words} ədəd\n"
        final_text += f"⚡ **Güclü aşkarlama:** Aktiv ✅\n\n"
        final_text += "**Bu siyahıda əlavə etdiyiniz bütün söyüşlər də daxildir!**"

        await event.respond(final_text, parse_mode='markdown')

    @client.on(events.NewMessage(incoming=True))
    async def profanity_filter_handler(event):
        # Yalnız qruplarda işləsin
        if not event.is_group:
            return

        # Mesaj mətni yoxla
        if not event.message.message:
            return

        try:
            sender = await event.get_sender()

            if not sender or not hasattr(sender, 'id'):
                print("⚠️ Sender məlumatı əldə edilə bilmədi")
                return

            # Məşədi istisna
            if sender.id == MESHEDI_ID:
                return

            settings = load_profanity_settings()

            if not settings.get("enabled", True):
                return

            allowed_groups = settings.get("groups", [])
            if event.chat_id not in allowed_groups:
                return

            # Qrup aktivləşdirmə yoxlaması
            if not await is_userbot_active_in_group(event.chat_id):
                print(f"⚠️ Qrup deaktivdir, söyüş filtri işləməyəcək: {event.chat_id}")
                return

            message_text = event.message.message
            is_profane, found_words = check_profanity(message_text)

            if is_profane:
                try:
                    chat = await event.get_chat()
                    group_name = chat.title if hasattr(chat, 'title') else "Naməlum qrup"

                    chat_input = await event.get_input_chat()
                    admins = await client.get_participants(chat_input, filter=ChannelParticipantsAdmins())
                    admin_ids = [admin.id for admin in admins]
                    is_admin = sender.id in admin_ids

                    await event.delete()

                    sender = await event.get_sender()
                    mention = f"[{sender.first_name}](tg://user?id={sender.id})"

                    add_log(f"Söyüş filtri: {sender.first_name} tərəfindən söyüş silindi", "warning")

                    print(f"🤬 Söyüş silindi. Göndərən: {sender.first_name or 'Unknown'} (ID: {sender.id}) - {'Admin' if is_admin else 'User'}")
                    print(f"    Tapılan söyüşlər: {found_words}")

                    if not is_admin:
                        try:
                            banned_rights = ChatBannedRights(
                                until_date=None,
                                send_messages=True,
                                send_media=True,
                                send_stickers=True,
                                send_gifs=True,
                                send_games=True,
                                send_inline=True,
                                embed_links=True
                            )

                            await client(EditBannedRequest(
                                channel=event.chat_id,
                                participant=sender.id,
                                banned_rights=banned_rights
                            ))
                            print(f"🔇 İstifadəçi mute edildi: {sender.first_name or 'Unknown'} (ID: {sender.id})")

                        except Exception as mute_error:
                            print(f"❌ Mute etmə xətası: {mute_error}")
                    else:
                        print(f"👑 Admin məhdudiyyəti alınmadı: {sender.first_name or 'Unknown'} (ID: {sender.id})")

                    # Real Telegram adını al (emoji və xüsusi simvollarıla birlikdə)
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

                    # Real adı mention üçün istifadə et (emoji və bütün simvollarıla)
                    display_name = full_name[:50]  # Yalnız uzunluğu məhdudlaşdır
                    if not display_name.strip():
                        display_name = f"User {sender.id}"

                    sender_mention = f"[{display_name}](tg://user?id={sender.id})"

                    admin_status = " (Admin)" if is_admin else ""
                    report_text = f"{sender_mention} 🚫 bu sözü yazdı: {message_text}\n\n"
                    report_text += f"📍 Qrup: *{group_name}*\n"
                    report_text += f"👤 İstifadəçi ID: `{sender.id}`\n"
                    report_text += f"👑 Status: {'Admin' if is_admin else 'User'}\n"

                    try:
                        await client.send_message(MESHBOT_USERBOT_ID, report_text, parse_mode='markdown')
                        print(f"📤 Report göndərildi MəşBot Userbot-a")
                    except Exception as report_error:
                        print(f"❌ Report göndərilmədi: {report_error}")

                    # Xəbərdarlıq mesajı göndər
                    try:
                        warning_text = f"{sender_mention} 🚫 Söyüş istifadə etmək qadağandır! Məşədiyə report edildi!"
                        await client.send_message(event.chat_id, warning_text, parse_mode='markdown')
                        print(f"⚠️ Xəbərdarlıq mesajı göndərildi: {sender.first_name}")
                    except Exception as warning_error:
                        try:
                            # Mention işləməzsə sadə mesaj göndər
                            simple_warning = f"🚫 {display_name} Söyüş istifadə etmək qadağandır! Məşədiyə report edildi!"
                            await client.send_message(event.chat_id, simple_warning)
                        except Exception as simple_error:
                            print(f"❌ Xəbərdarlıq mesajı göndərilmədi: {simple_error}")

                except Exception as delete_error:
                    print(f"❌ Söyüş mesajı silinərkən xəta: {delete_error}")

        except Exception as e:
            print(f"❌ Profanity filter xətası: {e}")