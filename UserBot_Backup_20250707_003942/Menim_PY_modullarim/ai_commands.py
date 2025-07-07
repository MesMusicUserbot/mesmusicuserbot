
from telethon import events
from openai import OpenAI
import json
import os
from .log_server import add_log

MESHEDI_ID = 5257767076
MEMORY_FILE = "Menim_JSON_fayillarim/memory.json"

def load_memory():
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(data):
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

client_openai = OpenAI(
    api_key=""
)

def register_ai_handlers(client):
    @client.on(events.NewMessage(pattern=r'(?i)(.ai|#ai)\s+(.*)'))
    async def ai_answer(event):
        user_id = event.sender_id
        
        if user_id != MESHEDI_ID:
            sender = await event.get_sender()
            mention = f"[{sender.first_name}](tg://user?id={sender.id})"
            await event.reply(f"{mention} ❌ Bu komandanı yalnız Məşədi istifadə edə bilər.", parse_mode='markdown')
            add_log(f"AI əmri: İcazəsiz istifadə cəhdi", "warning")
            return
        
        query = event.pattern_match.group(2).strip()
        add_log(f"AI sorğusu: {query[:50]}...", "info")

        memory = load_memory()
        user_history = memory.get(str(user_id), [])
        
        conversation_context = []
        if user_history:
            conversation_context = user_history[-20:]

        conversation_context.append({"role": "user", "content": query})

        try:
            system_prompt = (
                "Sən Azərbaycan dilinə mükəmməl bələd olan universal AI köməkçisən. "
                "İstifadəçilərin hər növ sualını cavablandıra bilirsən və əvvəlki söhbəti yadda saxlayırsan.\n\n"
                "📚 **Elm və Texnologiya:**\n"
                "- Programlaşdırma və kod yazma (Python, JavaScript, Java, C++, və s.)\n"
                "- Riyaziyyat və fizika problemləri\n"
                "- Kompüter elmləri və IT\n"
                "- İnженерлик və texniki məsələlər\n\n"
                "🌍 **Dil və Mədəniyyət:**\n"
                "- Dil öyrətmə və tərcümə (ingilis, türk, rus, ərəb, fars və s.)\n"
                "- Ədəbiyyat və şeir yazma\n"
                "- Tarixi məlumatlar və mədəniyyət\n"
                "- Coğrafiya və ölkələr haqqında\n\n"
                "🎨 **Yaradıcılıq və Əyləncə:**\n"
                "- Yaradıcı yazı və hekayələr\n"
                "- Zarafatlar və yumor\n"
                "- Şeir və mahnı sözləri\n"
                "- Oyun və əyləncə ideyaları\n\n"
                "🍳 **Həyat və Praktika:**\n"
                "- Yemək reseptləri və aşpazlıq\n"
                "- Səhiyyə və sağlamlıq məsləhətləri\n"
                "- Biznes və maliyyə\n"
                "- Hüquqi məlumatlar\n"
                "- Psixologiya və şəxsi inkişaf\n\n"
                "💡 **Xüsusiyyətlərin:**\n"
                "- Həmişə dəqiq və ətraflı cavab ver\n"
                "- Əvvəlki söhbəti yadda saxla və kontekstdən istifadə et\n"
                "- Əgər istifadəçi 'onu', 'bunu', 'həmin şeyi' kimi istinadlar işlədirsə, əvvəlki söhbətdən anlayırsan ki nədən danışır\n"
                "- Mümkün olduqda nümunələr və praktik məsləhətlər ver\n"
                "- Əgər sual aydın deyilsə, dəqiqləşdirici suallar ver\n"
                "- Zarafat və yumor istəyəndə məzəli və yaradıcı ol\n"
                "- Həmişə Azərbaycan dilində cavab ver\n"
                "- Məlumatları strukturlaşdırılmış şəkildə təqdim et\n"
                "- Əgər söhbət müəyyən mövzudan gedərsə və sonra həmin mövzu ilə bağlı sual gələrsə, əvvəlki konteksti xatırla"
            )

            response = client_openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    *conversation_context
                ],
                temperature=0.7,
                max_tokens=1800,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )

            answer = response.choices[0].message.content.strip()

            if len(answer) > 4000:
                parts = [answer[i:i+3800] for i in range(0, len(answer), 3800)]
                for i, part in enumerate(parts):
                    if i == 0:
                        await event.reply(f"🤖 **{i+1}/{len(parts)}**\n\n{part}")
                    else:
                        await event.respond(f"🤖 **{i+1}/{len(parts)}**\n\n{part}")
            else:
                await event.reply(f"🤖 {answer}")

            user_history.append({"role": "user", "content": query})
            user_history.append({"role": "assistant", "content": answer})
            
            if len(user_history) > 30:
                user_history = user_history[-30:]
            
            memory[str(user_id)] = user_history
            save_memory(memory)

        except Exception as e:
            await event.reply(f"⚠️ AI cavab verə bilmədi: {str(e)[:100]}")
