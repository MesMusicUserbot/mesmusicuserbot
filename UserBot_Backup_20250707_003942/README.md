
# MəşBot - Azərbaycan Telegram Userbot

## 📋 Təsvir

MəşBot - Telegram üçün güclü və çoxfunksiyalı userbot sistemidir. Qrup idarəetməsi, əyləncə, təhlükəsizlik və avtomatik funksiyalar təklif edir.

## 🚀 Quraşdırma

### 1. Environment Variables
`.env` faylı yaradın və aşağıdakı məlumatları daxil edin:

```env
API_ID=sizin_api_id
API_HASH=sizin_api_hash
PHONE=sizin_telefon_nomresi
PASSWORD=sizin_2fa_parolu
LOG_PORT=5000
MESHEDI_ID=sizin_telegram_id
MESHBOT_USERBOT_ID=hedef_userbot_id
```

### 2. Asılılıqları yükləyin
```bash
pip install telethon python-dotenv flask psutil
```

### 3. Botu işə salın
```bash
python main.py
```

## 📚 Modullar

### 🏷️ TAĞ ƏMRLƏRİ (tag_commands.py)
- Qrup üzvlərini tağlamaq
- Admin və istifadəçi seçimi
- Sürətli tağlama funksiyaları

### 🔮 ƏYLƏNCƏ ƏMRLƏRİ (entertainment_commands.py)
- Oyunlar və əyləncə komandaları
- İnteraktiv funksiyalar

### 🚀 KOSMIK ƏMRLƏRİ (cosmic_commands.py)
- Animasiya və effektlər
- Vizual komandalar

### 👤 PROFİL ƏMRLƏRİ (profile_commands.py)
- Profil idarəetməsi
- Şəkil və məlumat dəyişdirmə

### 🛡️ SÖYÜŞ FİLTRİ (profanity_filter.py)
- Avtomatik söyüş aşkarlanması
- Qrup təmizləmə sistemi
- Azərbaycan dili dəstəyi

### 🔒 STİKER BLOKLAMA (sticker_blocker.py)
- Müəyyən stikerləri bloklama
- İcazəli istifadəçi sistemi

### 🔗 LİNK FİLTRİ (link_filter.py)
- İcazəsiz link bloklama
- Global və qrup-spesifik icazələr

### 🤖 AI ƏMRLƏRİ (ai_commands.py)
- AI inteqrasiyası və cavablar

### 🎵 MUSİQİ ƏMRLƏRİ (music_player.py)
- Musiqi oxutma sistemi

### ℹ️ SİSTEM ƏMRLƏRİ (system_commands.py)
- Sistem monitorinqi
- Statistika və status

### 🔄 AVTOMATIK FUNKSIYALAR (automatic_functions.py)
- Avtomatik proseslər
- Planlı tapşırıqlar

### 🎯 QRUP AKTİVLƏŞDİRMƏ SİSTEMİ (group_activation.py)
- Qrupspesifik userbot aktivləşdirmə
- `.aktivol` - Userbotu qrupda aktivləşdir
- `.deaktivol` - Userbotu qrupda deaktivləşdir
- `.aktivstatus` - Aktivləşdirmə statusunu yoxla
- Avtomatik qrup filtrləməsi

## 🔐 Təhlükəsizlik

- API məlumatları environment variables vasitəsilə qorunur
- Istifadəçi icazələri səviyyələndirilmişdir
- Log sistemi bütün fəaliyyətləri izləyir

## 📊 Log Sistemi

Bot `http://localhost:5000` ünvanında web interfeysi təqdim edir:
- Real-time log izlənməsi
- Sistem statistikaları
- Modul statusları

## ⚙️ Konfiqurasiya

JSON faylları `Menim_JSON_fayillarim/` qovluğunda saxlanılır:
- `profanity_settings.json` - Söyüş filtri ayarları
- `link_filter_settings.json` - Link filtri ayarları
- `sticker_blocker_settings.json` - Stiker bloklama ayarları
- `group_activation_settings.json` - Qrup aktivləşdirmə ayarları
- `bot_logs.json` - Bot logları

## 🛠️ Texniki Tələblər

- Python 3.8+
- Telegram API hesabı
- Internet bağlantısı

## 📝 Lisenziya

Bu layihə açıq mənbəlidir və təhsil məqsədləri üçün istifadə edilə bilər.

## 🤝 Dəstək

Problemlər və ya suallar üçün issue yaradın.
