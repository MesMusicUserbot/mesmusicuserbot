import os

# Web messages JSON faylının yolunu Menim_JSON_fayillarim qovluğuna yönləndir
WEB_MESSAGES_FILE = "Menim_JSON_fayillarim/web_messages.json"

def ensure_json_directory():
    """JSON qovluğunun mövcudluğunu təmin edir"""
    os.makedirs("Menim_JSON_fayillarim", exist_ok=True)

# Web checker functionality removed
async def start_web_checker(client):
    """Web checker deactivated"""
    ensure_json_directory()
    print("🌐 Web checker functionality removed")