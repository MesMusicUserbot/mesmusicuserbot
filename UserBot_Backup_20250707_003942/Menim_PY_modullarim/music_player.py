import asyncio
import os
import json
from telethon import events
from pytgcalls import PyTgCalls, filters
from pytgcalls.exceptions import NotInCallError
import yt_dlp
import subprocess

# For PyTgCalls v2.2.5
from pytgcalls.types import MediaStream as AudioPiped
from .log_server import add_log
from .group_activation import is_userbot_active_in_group

MESHEDI_ID = 5257767076
QUEUE_FILE = "Menim_JSON_fayillarim/music_queue.json"

# Global variables
music_queue = {}
current_playing = {}
pytg = None

def load_queue():
    """Musiqi növbəsini yaddaşdan yükləyir"""
    try:
        if os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except:
        return {}

def save_queue():
    """Musiqi növbəsini yaddaşa saxlayır"""
    try:
        os.makedirs("Menim_JSON_fayillarim", exist_ok=True)
        with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
            json.dump(music_queue, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Queue saxlama xətası: {e}")

async def search_youtube(query):
    """YouTube-da mahnı axtarır"""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # İlk olaraq axtarış et
            search_results = ydl.extract_info(f"ytsearch1:{query}", download=False)

            if search_results and 'entries' in search_results and search_results['entries']:
                video = search_results['entries'][0]
                return {
                    'url': video['url'],
                    'title': video['title'],
                    'duration': video.get('duration', 0),
                    'uploader': video.get('uploader', 'Unknown')
                }

        return None
    except Exception as e:
        print(f"YouTube axtarış xətası: {e}")
        return None

async def download_audio(url):
    """Mahnını yükləyir və tam yüklənməsini gözləyir"""
    try:
        # Əvvəlcə köhnə faylları təmizlə
        for file in ['song.webm', 'song.mp4', 'song.m4a', 'song.mp3']:
            if os.path.exists(file):
                os.remove(file)

        # yt-dlp ilə audio yüklə - tam bitməsini gözlə
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'song.%(ext)s',
            'noplaylist': True,
            'quiet': False,  # Progress görmək üçün
            'no_warnings': False,
        }

        add_log("Audio yükləmə başladı...", "info")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Sinkron yükləmə - tam bitməsini gözləyir
            ydl.download([url])
        
        add_log("Audio yükləmə tamamlandı", "success")

        # Yüklənmiş faylın adını tap
        downloaded_file = None
        for ext in ['webm', 'mp4', 'm4a', 'mp3']:
            if os.path.exists(f'song.{ext}'):
                downloaded_file = f'song.{ext}'
                break

        if not downloaded_file:
            add_log("Yüklənmiş audio fayl tapılmadı", "error")
            return None
        
        add_log(f"Audio fayl hazırdır: {downloaded_file}", "success")
        
        # MediaStream üçün direkt fayl qaytar (ffmpeg ehtiyacı yox)
        return downloaded_file

    except Exception as e:
        print(f"Audio yükləmə xətası: {e}")
        add_log(f"Audio yükləmə xətası: {e}", "error")
        return None

async def join_and_play(chat_id, event):
    """Səsli söhbətə qoşulur və mahnı çalmağa başlayır"""
    try:
        global pytg, current_playing

        if not pytg:
            return False

        # Növbədən ilk mahnını götür
        if str(chat_id) not in music_queue or not music_queue[str(chat_id)]:
            await event.reply("❌ Növbə boşdur!")
            return False

        song_info = music_queue[str(chat_id)][0]

        # Mahnını yüklə
        status_msg = await event.reply(f"⬇️ Yüklənir: **{song_info['title']}**\n📊 Gözləyin, fayl tam yüklənir...")

        audio_file = await download_audio(song_info['url'])
        if not audio_file:
            await status_msg.edit("❌ Mahnı yüklənə bilmədi!")
            return False
        
        await status_msg.edit(f"✅ Yükləndi: **{song_info['title']}**\n🎵 Səsli söhbətə qoşulur...")

        # Debug: Chat ID-ni yoxla
        print(f"Qrup ID-si: {chat_id}")
        add_log(f"Səsli söhbətə qoşulmağa çalışır: {chat_id}", "info")

        try:
            # Səsli söhbətə qoşul və mahnı çal
            await pytg.play(
                chat_id,
                AudioPiped(audio_file),
            )

            current_playing[str(chat_id)] = song_info

            requester_info = song_info.get('requester_mention', song_info.get('uploader', 'Bilinməyən'))
            await status_msg.edit(f"🎵 **Oxunur:**\n**{song_info['title']}**\n👤 **Tələb edən:** {requester_info}", parse_mode='markdown')

            add_log(f"Musiqi uğurla başladıldı: {song_info['title']}", "success")
            return True

        except Exception as join_error:
            error_msg = str(join_error)
            if "GROUPCALL_JOIN_MISSING" in error_msg:
                await status_msg.edit("❌ Səsli söhbət mövcud deyil! Əvvəlcə qrupda səsli söhbət başladın.")
            elif "CHAT_ADMIN_REQUIRED" in error_msg:
                await status_msg.edit("❌ Səsli söhbətə qoşulmaq üçün admin icazəsi lazımdır!")
            elif "USER_ALREADY_PARTICIPANT" in error_msg:
                await status_msg.edit("❌ Artıq səsli söhbətdəyəm!")
            else:
                await status_msg.edit(f"❌ Səsli söhbətə qoşula bilmədi: {error_msg}")
            add_log(f"Səsli söhbət qoşulma xətası: {error_msg}", "error")
            return False

    except Exception as e:
        print(f"Join and play xətası: {e}")
        return False

async def preload_next_song(chat_id):
    """Növbəti mahnını arxa planda yükləyir"""
    try:
        if str(chat_id) in music_queue and len(music_queue[str(chat_id)]) > 1:
            next_song = music_queue[str(chat_id)][1]  # İlk mahnı çalınır, ikinci mahnını yükləyirik
            await download_audio(next_song['url'])
            add_log(f"Növbəti mahnı yüklənir: {next_song['title']}", "info")
    except Exception as e:
        print(f"Preload xətası: {e}")
        add_log(f"Preload xətası: {e}", "error")

def register_music_handlers(client):
    """Musiqi handler-lərini qeydiyyata alır"""
    global pytg, music_queue

    # PyTgCalls-ı başlat
    pytg = PyTgCalls(client)
    music_queue = load_queue()

    @client.on(events.NewMessage(pattern=r'^/play (.+)'))
    async def play_command(event):
        """Musiqi çalmaq üçün əsas komanda"""
        # Qrup aktivləşdirmə yoxlaması
        if event.is_group and not await is_userbot_active_in_group(event.chat_id):
            return

        await event.delete()



        if not event.is_group:
            await event.reply("❌ Bu əmr yalnız qruplarda işləyir!")
            return

        query = event.pattern_match.group(1).strip()

        # Mahnı axtarışı
        search_msg = await event.reply(f"🔍 Axtarılır: **{query}**")

        song_info = await search_youtube(query)
        if not song_info:
            await search_msg.edit("❌ Mahnı tapılmadı!")
            return

        # İstifadəçi məlumatını əlavə et
        sender = await event.get_sender()
        requester_name = sender.first_name or "İstifadəçi"
        requester_mention = f"[{requester_name}](tg://user?id={sender.id})"

        # Mahnı məlumatına istifadəçi əlavə et
        song_info['requester_name'] = requester_name
        song_info['requester_mention'] = requester_mention
        song_info['requester_id'] = sender.id

        # Növbəyə əlavə et
        chat_id = str(event.chat_id)
        if chat_id not in music_queue:
            music_queue[chat_id] = []

        music_queue[chat_id].append(song_info)
        save_queue()

        await search_msg.edit(f"✅ Növbəyə əlavə edildi:\n**{song_info['title']}**\n👤 **Tələb edən:** {requester_mention}", parse_mode='markdown')

        add_log(f"Mahnı növbəyə əlavə edildi: {song_info['title']}", "info")

        # Əgər hazırda mahnı çalınmırsa, dərhal başlat
        if chat_id not in current_playing:
            await join_and_play(event.chat_id, event)

        # Növbəti mahnını arxa planda pre-load et (async)
        asyncio.create_task(preload_next_song(chat_id))

    @client.on(events.NewMessage(pattern=r'^/stop'))
    async def stop_command(event):
        """Musiqini dayandırır"""
        if event.is_group and not await is_userbot_active_in_group(event.chat_id):
            return

        await event.delete()



        if not event.is_group:
            await event.reply("❌ Bu əmr yalnız qruplarda işləyir!")
            return

        try:
            chat_id = str(event.chat_id)

            # Növbəni təmizlə
            if chat_id in music_queue:
                music_queue[chat_id] = []
                save_queue()

            # Hazırkı mahnını dayandır
            if chat_id in current_playing:
                del current_playing[chat_id]

            # Səsli söhbətdən çıx
            await pytg.leave_group_call(event.chat_id)

            await event.reply("⏹️ Musiqi dayandırıldı və növbə təmizləndi!")
            add_log("Musiqi dayandırıldı", "info")

        except Exception as e:
            await event.reply(f"❌ Dayandırma xətası: {str(e)}")

    @client.on(events.NewMessage(pattern=r'^/skip'))
    async def skip_command(event):
        """Hazırkı mahnını keçir"""
        if event.is_group and not await is_userbot_active_in_group(event.chat_id):
            return

        await event.delete()



        if not event.is_group:
            await event.reply("❌ Bu əmr yalnız qruplarda işləyir!")
            return

        try:
            chat_id = str(event.chat_id)

            # Hazırkı mahnını növbədən çıxar
            if chat_id in music_queue and music_queue[chat_id]:
                skipped_song = music_queue[chat_id].pop(0)
                save_queue()

                await event.reply(f"⏭️ Keçirildi: **{skipped_song['title']}**")

                # Növbətdə başqa mahnı varsa, onu çal
                if music_queue[chat_id]:
                    await join_and_play(event.chat_id, event)
                else:
                    # Növbə boşdursa, dayandır
                    if chat_id in current_playing:
                        del current_playing[chat_id]
                    await pytg.leave_group_call(event.chat_id)
                    await event.reply("📭 Növbə bitdi!")
            else:
                await event.reply("❌ Keçiləcək mahnı yoxdur!")

        except Exception as e:
            await event.reply(f"❌ Keçirmə xətası: {str(e)}")

    @client.on(events.NewMessage(pattern=r'^/queue'))
    async def queue_command(event):
        """Musiqi növbəsini göstərir"""
        if event.is_group and not await is_userbot_active_in_group(event.chat_id):
            return

        await event.delete()



        if not event.is_group:
            await event.reply("❌ Bu əmr yalnız qruplarda işləyir!")
            return

        chat_id = str(event.chat_id)

        if chat_id not in music_queue or not music_queue[chat_id]:
            await event.reply("📭 Musiqi növbəsi boşdur!")
            return

        queue_text = "🎵 **Musiqi Növbəsi:**\n\n"

        for i, song in enumerate(music_queue[chat_id][:10], 1):
            if i == 1:
                queue_text += f"▶️ **{i}.** {song['title']}\n"
            else:
                queue_text += f"🎵 **{i}.** {song['title']}\n"

        if len(music_queue[chat_id]) > 10:
            queue_text += f"\n➕ **Və daha {len(music_queue[chat_id]) - 10} mahnı...**"

        await event.reply(queue_text)

    # PyTgCalls 1.2.5 üçün event handler
    async def stream_end_handler(client, update):
        """Mahnı bitəndə avtomatik növbəti mahnıya keçir"""
        try:
            chat_id = str(update.chat_id)

            # Hazırkı mahnını növbədən çıxar
            if chat_id in music_queue and music_queue[chat_id]:
                finished_song = music_queue[chat_id].pop(0)
                save_queue()

                add_log(f"Mahnı bitdi: {finished_song['title']}", "info")

                # Növbətdə başqa mahnı varsa
                if music_queue[chat_id]:
                    # Növbəti mahnını çal
                    next_song = music_queue[chat_id][0]

                    audio_file = await download_audio(next_song['url'])
                    if audio_file:
                        await pytg.play(
                            update.chat_id,
                            AudioPiped(audio_file),
                        )

                        current_playing[chat_id] = next_song

                        # Qrupa məlumat göndər
                        requester_info = next_song.get('requester_mention', next_song.get('uploader', 'Bilinməyən'))
                        await client.send_message(
                            update.chat_id,
                            f"🎵 **Növbəti mahnı:**\n**{next_song['title']}**\n👤 **Tələb edən:** {requester_info}",
                            parse_mode='markdown'
                        )

                        add_log(f"Növbəti mahnı başladı: {next_song['title']}", "info")
                else:
                    # Növbə boşdursa
                    if chat_id in current_playing:
                        del current_playing[chat_id]

                    await pytg.leave_group_call(update.chat_id)

                    await client.send_message(
                        update.chat_id,
                        "📭 **Musiqi növbəsi tamamlandı!**\nBot səsli söhbətdən çıxdı."
                    )

                    add_log("Musiqi növbəsi tamamlandı", "info")

        except Exception as e:
            print(f"Stream end xətası: {e}")
            add_log(f"Stream end xətası: {e}", "error")

    # Event handler-i əlavə et (PyTgCalls 1.0.0 üçün)
    try:
        @pytg.on_stream_end()
        async def on_stream_end(client, update):
            await stream_end_handler(client, update)
    except AttributeError:
        try:
            # PyTgCalls 1.0.0 üçün alternatif yol
            pytg.add_handler(stream_end_handler, filters.stream_end)
        except:
            # Əgər heç biri işləməzsə, event handling-i deaktiv edirik
            print("⚠️ PyTgCalls stream end event dəstəklənmir - avtomatik növbə keçidi söndürüldü")
            add_log("PyTgCalls stream end event dəstəklənmir", "warning")

    return pytg

async def start_pytgcalls(pytg_instance):
    """PyTgCalls-ı başladır"""
    try:
        await pytg_instance.start()
        add_log("PyTgCalls uğurla başladıldı", "success")
        return True
    except Exception as e:
        print(f"PyTgCalls başlatma xətası: {e}")
        add_log(f"PyTgCalls xətası: {e}", "error")
        return False