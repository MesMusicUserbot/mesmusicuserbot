
"""
Qrup Aktivləşdirmə Middleware
Bu modul bütün modulların qrup aktivləşdirmə yoxlamasını avtomatik edir.
"""

from .group_activation import is_userbot_active_in_group

def apply_activation_check(original_handler):
    """
    Decorator function - hər hansı command handler-ə qrup aktivləşdirmə yoxlaması əlavə edir
    """
    async def wrapper(event):
        # PM-lərdə həmişə işləsin
        if event.is_private:
            return await original_handler(event)
        
        # Qruplarda aktivlik yoxlanılır
        if event.is_group:
            if not is_userbot_active_in_group(event.chat_id):
                # Userbot bu qrupda aktiv deyil - heç bir cavab vermə
                return
        
        # Channels-də də yoxla
        if event.is_channel and not event.is_group:
            if not is_userbot_active_in_group(event.chat_id):
                return
        
        # Aktivdirsə normal şəkildə işlə
        return await original_handler(event)
    
    return wrapper

def register_with_activation_check(client, pattern, original_func):
    """
    Client-ə handler qeydiyyatı aparır və avtomatik aktivləşdirmə yoxlaması əlavə edir
    """
    @client.on(events.NewMessage(pattern=pattern))
    @apply_activation_check
    async def wrapped_handler(event):
        return await original_func(event)
    
    return wrapped_handler
