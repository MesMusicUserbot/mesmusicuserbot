import os
import re
from telethon import events
import asyncio
import psutil
import time
import os
from .log_server import add_log

MESHEDI_ID = 5257767076

def scan_command_files():
    """Bütün modul fayllarını skan edib əmrləri tapır"""
    commands = {}
    module_dir = "Menim_PY_modullarim"

    try:
        # Hər modul faylını oxuyaq
        for filename in os.listdir(module_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                filepath = os.path.join(module_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Pattern əmrlərini tap
                    pattern_matches = re.findall(r'@.*\.on\(events\.NewMessage\(pattern=r?[\'"]([^\'\"]+)[\'"]\)\)', content)

                    for match in pattern_matches:
                        command = match.replace('\\', '')
                        if command.startswith('.'):
                            # Modul adından kategoriyanı çıxar
                            module_name = filename.replace('.py', '').replace('_', ' ').title()

                            # Əmr haqqında məlumat topla
                            command_info = extract_command_info(content, command)

                            if module_name not in commands:
                                commands[module_name] = []

                            commands[module_name].append({
                                'command': command,
                                'description': command_info['description'],
                                'permission': command_info['permission']
                            })

                except Exception as e:
                    print(f"Fayl oxunarkən xəta ({filename}): {e}")
                    continue

    except Exception as e:
        print(f"Modul qovluğu oxunarkən xəta: {e}")

    return commands

def extract_command_info(content, command):
    """Əmr haqqında məlumat çıxarır"""
    # Əmrlərin müəyyən edilmiş təsvirləri
    command_descriptions = {
        '.status': 'Bot işləklik statusunu yoxlayır və cavab verir',
        '.test': 'Bot testini icra edir (status əmri ilə birləşib)',
        '.əmrlər': 'Bütün əmrlərin dinamik siyahısını göstərir',
        '.tagall': 'Qrupdakı bütün üzvləri bir-bir etiketləyir',
        '.rtag': 'Üzvləri yumorlu random mesajlarla etiketləyir',
        '.cancel': 'Aktiv taglama prosesini dayandırır',
        '.zipyarat': 'Layihəni ZIP arxivə çevirir (yalnız Məşədi)',
        '.ziplist': 'ZIP arxivinin məzmununu göstərir (yalnız Məşədi)',
        '.fal': 'Random və əyləncəli fal açır (5 dəqiqə limit)',
        '.esq': 'İki istifadəçi arasında sevgi faizini hesablayır',
        '.kosmos': 'Kosmik planet animasiyası göstərir',
        '.klon': 'Başqa istifadəçinin profilini klonlayır',
        '.qaytar': 'Orijinal profili bərpa edir',
        '.söyüş': 'Söyüş filtri ayarlarını göstərir',
        '.soyusstart': 'Söyüş filtrini qrupda aktivləşdirir',
        '.soyusstop': 'Söyüş filtrini qrupda dayandırır',
        '.stiker': 'Stiker bloklama ayarlarını göstərir',
        '.stikerstart': 'Stiker bloklamasını aktivləşdirir',
        '.stikerstop': 'Stiker bloklamasını dayandırır',
        '.stikerstatus': 'Stiker bloklama statusunu göstərir',
        '.stikerəlavə': 'Müəyyən stikeri blok siyahısına əlavə edir',
        '.stikersil': 'Stikeri blok siyahısından çıxarır',
        '.stikericazə': 'İstifadəçiyə bloklanmış stiker icazəsi verir',
        '.stikericazəsil': 'İstifadəçinin stiker icazəsini götürür',
        '.stikerlock': 'Stikeri bloklamaq üçün (stikerə reply)',
        '.stikerunlock': 'Stiker blokunu götürmək üçün (stikerə reply)',
        '.linklist': 'Qrupun icazəli linklərini göstərir',
        '.linkstart': 'Link filtrini qrupda aktivləşdirir',
        '.linkstop': 'Link filtrini qrupda dayandırır',
        '.linkəlavə': 'Qrupa xüsusi link əlavə edir',
        '.linksil': 'Qrupdan xüsusi link silir',
        '.linkglobal': 'Global icazəli link təyin edir',
        '.linkstatus': 'Link filtri statusunu göstərir',
        '.ai': 'OpenAI GPT-4 ilə sual-cavab',
        '#ai': 'OpenAI GPT-4 ilə sual-cavab (alternativ sintaksis)',
        '.play': 'Musiqi çalır (YouTube/Spotify linkləri)',
        '.stop': 'Musiqi dayandırır',
        '.skip': 'Sonrakı mahnıya keçir',
        '.queue': 'Musiqi növbəsini göstərir',
        '.volume': 'Səs həcmini tənzimləyir',
        '.aktivol': 'Userbotu qrupda aktivləşdir',
        '.deaktivol': 'Userbotu qrupda deaktivləşdir',
        '.aktivstatus': 'Aktivləşdirmə statusunu yoxla',
        '.söyüşstatus': 'Söyüş filtri statusunu göstərir',
        '.cancel': 'Aktiv taglama prosesini dayandırır'
    }

    # Müəyyən edilmiş təsviri götür, yoxsa default
    description = command_descriptions.get(command, "Əmr haqqında ətraflı məlumat yoxdur")
    permission = "🌍 Hər kəs"

    # Funksiya adını tap
    func_pattern = rf'async def (\w+).*?pattern=r?[\'\"]{re.escape(command)}[\'\"]'
    func_match = re.search(func_pattern, content, re.DOTALL)

    if func_match:
        func_name = func_match.group(1)

        # Funksiya docstring-ini tap
        doc_pattern = rf'async def {re.escape(func_name)}.*?\n\s*"""([^"]+)"""'
        doc_match = re.search(doc_pattern, content, re.DOTALL)
        if doc_match:
            docstring_desc = doc_match.group(1).strip()
            # Əgər docstring daha uzundursa, onu istifadə et
            if len(docstring_desc) > len(description):
                description = docstring_desc

    # İcazə yoxlamasını tap
    if 'MESHEDI_ID' in content and f'sender.id != MESHEDI_ID' in content:
        permission = "👑 Məşədi"
    elif 'is_admin' in content or 'get_permissions' in content or 'admin_perms' in content:
        permission = "🛡️ Admin"
    elif command in ['.tagall', '.rtag', '.cancel', '.soyusstart', '.soyusstop', '.söyüş', '.söyüşstatus',
                     '.stikerstart', '.stikerstop', '.stikerəlavə', '.stikersil', '.stikerstatus', '.stiker',
                     '.stikericazə', '.stikericazəsil', '.stikerlock', '.stikerunlock',
                     '.linkstart', '.linkstop', '.linkəlavə', '.linksil', '.linklist', '.linkstatus']:
        permission = "🛡️ Admin"
    elif command in ['.esq', '.klon', '.qaytar', '.ai', '#ai', '.linkglobal', '.əmrlər', '.aktivol', '.deaktivol', '.aktivstatus']:
        permission = "👑 Məşədi"

    return {
        'description': description,
        'permission': permission
    }

def generate_commands_text():
    """Dinamik əmrlər siyahısı yaradır"""
    try:
        commands = scan_command_files()

        text = "🤖 **MəşBot - Bütün Əmrlər** (Dinamik)\n\n"

        # Kategoriyaları müəyyən et
        category_emojis = {
            'Tag Commands': '🏷️',
            'Entertainment Commands': '🔮',
            'Cosmic Commands': '🚀',
            'Profile Commands': '👤',
            'Profanity Filter': '🛡️',
            'Sticker Blocker': '🔒',
            'Link Filter': '🔗',
            'Ai Commands': '🤖',
            'Music Player': '🎵',
            'System Commands': 'ℹ️',
            'Automatic Functions': '🔄',
            'Suggestion Commands': '📋'
        }

        if not commands:
            return get_fallback_commands_text()

        for category, command_list in commands.items():
            if not command_list:  # Boş kategoriyaları keç
                continue

            emoji = category_emojis.get(category, '📝')
            text += f"**{emoji} {category.upper()}:**\n"

            for cmd in command_list:
                try:
                    # Əmr haqqında qısa məlumat
                    command_text = cmd.get('command', 'Unknown')
                    desc = cmd.get('description', 'Təsvir yoxdur')
                    desc = desc[:50] + "..." if len(desc) > 50 else desc
                    perm = cmd.get('permission', '🌍 Hər kəs')

                    text += f"• `{command_text}` - {desc} {perm}\n"
                except Exception as e:
                    print(f"Komanda formatlanarkən xəta: {e}")
                    continue

            text += "\n"

        # Avtomatik funksiyalar
        text += "**🔄 AVTOMATIK FUNKSİYALAR:**\n"
        text += "🔹 View-once media saxlama (PM-də)\n"
        text += "🔹 Söyüş filtri (qruplarda)\n"
        text += "🔹 Link filtri (qruplarda)\n"
        text += "🔹 Stiker bloklaması (qruplarda)\n\n"

        text += "**İcazə səviyyələri:**\n"
        text += "👑 Məşədi - 🛡️ Admin - 🌍 Hər kəs\n\n"

        try:
            total_commands = sum(len(cmds) for cmds in commands.values())
            text += f"📊 **Cəmi əmr sayı:** {total_commands}"
        except:
            text += f"📊 **Cəmi əmr sayı:** Məlum deyil"

        return text

    except Exception as e:
        print(f"Commands text yaradılarkən xəta: {e}")
        return get_fallback_commands_text()

def get_fallback_commands_text():
    """Xəta halında köhnə siyahı"""
    return """🤖 **MəşBot - Əmrlər Siyahısı** 

**🏷️ TAĞ ƏMRLƏRİ:**
• `.tagall` - Hamını tağla 🛡️ Admin
• `.rtag` - Random tağ 🛡️ Admin
• `.cancel` - Taglama ləğvi 🛡️ Admin

**🔮 ƏYLƏNCƏ ƏMRLƏRİ:**
• `.fal` - Fal bax 🌍 Hər kəs
• `.esq` - Sevgi hesabla 👑 Məşədi

**🚀 KOSMIK ƏMRLƏRİ:**
• `.kosmos` - Kosmik animasiya 🌍 Hər kəs

**👤 PROFİL ƏMRLƏRİ:**
• `.klon` - Profil klonla 👑 Məşədi
• `.qaytar` - Profili bərpa et 👑 Məşədi

**🛡️ SÖYÜŞ FİLTRİ:**
• `.söyüş` - Söyüş filtri 🛡️ Admin
• `.soyusstart` - Filtri aktiv et 🛡️ Admin
• `.soyusstop` - Filtri dayandır 🛡️ Admin

**🔒 STİKER BLOKLAMA:**
• `.stiker` - Stiker bloklama 🛡️ Admin
• `.stikerstart` - Bloklamanı aktiv et 🛡️ Admin
• `.stikerstop` - Bloklamanı dayandır 🛡️ Admin

**🔗 LİNK FİLTRİ:**
• `.linklist` - İcazəli linklər 🛡️ Admin
• `.linkstart` - Link filtrini aktiv et 🛡️ Admin
• `.linkstop` - Link filtrini dayandır 🛡️ Admin

**🤖 AI ƏMRLƏRİ:**
• `.ai` - AI sual-cavab 👑 Məşədi
• `#ai` - AI sual-cavab 👑 Məşədi

**ℹ️ SİSTEM ƏMRLƏRİ:**
• `.status` - Bot statusu 🌍 Hər kəs
• `.əmrlər` - Əmrlər siyahısı 👑 Məşədi

**İcazə səviyyələri:**
👑 Məşədi - 🛡️ Admin - 🌍 Hər kəs"""

def register_system_handlers(client):
    # Universal command logger - bütün . ilə başlayan əmrləri izləyir
    @client.on(events.NewMessage(pattern=r'^\.(.+)'))
    async def universal_command_logger(event):
        try:
            # Qrup aktivləşdirmə yoxlaması - yalnız qruplarda
            if event.is_group:
                from .group_activation import is_userbot_active_in_group
                if not await is_userbot_active_in_group(event.chat_id):
                    return

            sender = await event.get_sender()
            command_text = event.text.strip()

            # Əmri Azərbaycan dilinə tərcümə et
            azerbaijani_commands = {
                '.status': 'Status yoxlaması',
                '.əmrlər': 'Əmrlər siyahısı',
                '.tagall': 'Hamını tağlama',
                '.rtag': 'Random tağlama',
                '.cancel': 'Taglama ləğvi',
                '.fal': 'Fal baxma',
                '.esq': 'Sevgi hesablama',
                '.kosmos': 'Kosmik animasiya',
                '.klon': 'Profil klonlama',
                '.qaytar': 'Profil bərpası',
                '.söyüş': 'Söyüş filtri',
                '.söyüşstart': 'Söyüş filtri aktivləşdirmə',
                '.söyüşstop': 'Söyüş filtri dayandırma',
                '.stiker': 'Stiker bloklama',
                '.stikerstart': 'Stiker bloklama aktivləşdirmə',
                '.stikerstop': 'Stiker bloklama dayandırma',
                '.stikerəlavə': 'Stiker blok siyahısına əlavə',
                '.stikersil': 'Stiker blok siyahısından silmə',
                '.linklist': 'İcazəli linklər',
                '.linkstart': 'Link filtri aktivləşdirmə',
                '.linkstop': 'Link filtri dayandırma',
                '.linkəlavə': 'Link əlavə etmə',
                '.linksil': 'Link silmə',
                '.linkglobal': 'Global link təyini',
                '.ai': 'AI sual-cavab',
                '#ai': 'AI sual-cavab',
                '.play': 'Musiqi çalma',
                '.stop': 'Musiqi dayandırma',
                '.skip': 'Mahnı atlama',
                '.queue': 'Musiqi növbəsi',
                '.volume': 'Səs həcmi tənzimi',
                '.zipyarat': 'ZIP yaratma',
                '.ziplist': 'ZIP siyahısı'
            }

            # Əmri birinci space-ə qədər götür
            base_command = command_text.split(' ')[0]
            azerbaijani_name = azerbaijani_commands.get(base_command, f"{base_command} əmri")

            # Chat tipini müəyyən et
            chat_type = "Private" if event.is_private else "Group"
            chat_name = "PM" if event.is_private else getattr(event.chat, 'title', 'Unknown')

            # Tam command-ı log et
            full_command = command_text[:50] + "..." if len(command_text) > 50 else command_text

            # İstifadəçi məlumatları
            user_name = sender.first_name or "Unknown"
            user_id = sender.id
            username = getattr(sender, 'username', None)

            # İstifadəçi formatını yarat
            if username:
                user_display = f"{user_name} → @{username} → {user_id}"
            else:
                user_display = f"{user_name} → {user_id}"

            # Yalnız istifadəçi məlumatını göstər
            log_message = f"👤 {user_display}"
            add_log(log_message, "commands", sender.id, sender.first_name)

        except Exception as e:
            # Xəta olarsa silent keç ki, digər handler-lər işləsin
            pass

        # Event-i başqa handler-lərə burax - tam propagation
        return

    @client.on(events.NewMessage(pattern=r'\.status'))
    async def status_handler(event):
        """Sistem statusu"""
        await event.delete()

        # PM-də həmişə işləsin
        if event.is_private:
            await event.reply("🤖 Bot aktivdir və işlək vəziyyətdədir ✅")
            return

        # Qrup aktivləşdirmə yoxlaması
        if event.is_group:
            try:
                from .group_activation import is_userbot_active_in_group
                if not await is_userbot_active_in_group(event.chat_id):
                    return
            except Exception:
                pass  # Xəta varsa, davam et

        sender = await event.get_sender()
        await event.reply("🤖 Bot aktivdir və işlək vəziyyətdədir ✅")


    @client.on(events.NewMessage(pattern=r"\.əmrlər"))
    async def commands_list_handler(event):
        try:
            await event.delete()
            sender = await event.get_sender()

            # PM-də həmişə işləsin
            if event.is_private:
                if sender.id != MESHEDI_ID:
                    mention = f"[{sender.first_name}](tg://user?id={sender.id})"
                    await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
                    return
            else:
                # Qrup aktivləşdirmə yoxlaması
                if event.is_group:
                    try:
                        from .group_activation import is_userbot_active_in_group
                        if not await is_userbot_active_in_group(event.chat_id):
                            return
                    except:
                        pass  # Aktivləşdirmə modulu işləmirsə, davam et

                if sender.id != MESHEDI_ID:
                    mention = f"[{sender.first_name}](tg://user?id={sender.id})"
                    await event.reply(f"{mention} ❌ Bu əmri yalnız Məşədi işlədə bilər.", parse_mode='markdown')
                    return

            # Dinamik əmrlər siyahısını yarat
            try:
                commands_text = generate_commands_text()
                await event.reply(commands_text, parse_mode='markdown')
                add_log(f"Commands list generated successfully", "info", sender.id, sender.first_name)

            except Exception as e:
                print(f"Əmrlər siyahısı yaradılarkən xəta: {e}")
                # Xəta olduqda köhnə sistem işləsin
                fallback_text = get_fallback_commands_text()
                await event.reply(fallback_text, parse_mode='markdown')
                add_log(f"Fallback commands list shown due to error: {e}", "warning", sender.id, sender.first_name)

        except Exception as e:
            print(f"Commands handler xətası: {e}")
            try:
                fallback_text = "❌ Əmrlər siyahısı yüklənərkən xəta baş verdi."
                await event.reply(fallback_text)
            except:
                pass


# Geriyə uyğunluq üçün alias
def register_system_commands(client):
    return register_system_handlers(client)