from telethon import events
import asyncio
import random
from .log_server import add_log
from .group_activation import is_userbot_active_in_group

def register_cosmic_handlers(client):
    @client.on(events.NewMessage(pattern='\.kosmos'))
    async def mesh_kosmos_handler(event):
        # Qrup aktivləşdirmə yoxlaması
        if event.is_group and not await is_userbot_active_in_group(event.chat_id):
            return
            
        await event.delete()
        msg = await event.reply("🪐 Mərkəz yönləndirildi...")

        frames = [
            """
                 🛰️

             🌍      🪐

                 ☀️
            """,
            """
             🪐      🌑


                 ☀️    🛰️
            """,
            """
                 🌍     🛰️

             🌑     ☀️

                     🪐
            """,
            """
            🛰️

                ☀️  🌍     🌑

            🪐
            """,
            """
                🌍     🪐

                    ☀️     🛰️

                          🌑
            """,
            """
              🌑

                  🛰️   ☀️

             🪐      🌍
            """,
            """
                🌍
            🪐       ☀️     🌑


                  🛰️
            """,
            """
              🪐    🛰️
                 ☀️
             🌍        🌑
            """,
            """
             🌍     ☀️     🛰️

             🌑            🪐
            """,
            """
             🌍     ☀️     🛰️

             🌑     🕳️    🪐
            """,
            """
             🌍     ☀️     🛰️

             🪐     🕳️    🌑
            """,
            """
             🪐     🛰️     🌑

             🕳️     ☀️    🌍
            """,
            """
             🪐     🛰️     🕳️

             🌑     ☀️    🌍
            """,
            """
             🛰️     🕳️

             ☀️     🌍    🪐 🌑
            """,
            """
             🕳️

             ☀️     🪐🌍🛰️🌑
            """,
            """
             🕳️ ☀️

             (Orbit dağıldı...)
            """,
            """
             🕳️

             (Bütün sistem uduldu)
            """
        ]

        for frame in frames:
            await asyncio.sleep(0.6)
            await msg.edit(f"```{frame}```", parse_mode="markdown")

        await asyncio.sleep(1)
        await msg.edit("""
```markdown
☀️ = Məşədi (Günəş)
🪐 = Admin (Böyük planet)
🌍 = User (Yer)
🛰️ = Bot (peyklər)
🌑 = Ghost reader (oxuyub susanlar)
🕳️ = Qara dəlik (mübahisəli istifadəçilər 😈)

⚠️ Diqqət: Qara dəlik orbitə daxil olduqda, hamını udur...""")