
"""
Mərkəzi Səhv İdarəetmə Sistemi
Bu modul bütün modullar üçün vahid exception handling təmin edir.
"""

import logging
import traceback
from functools import wraps
from .log_server import add_log

# Logging konfiqurasiyası
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Menim_JSON_fayillarim/error_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def safe_execute(operation_name: str = "Bilinməyən əməliyyat"):
    """
    Decorator - funksiyaları təhlükəsiz şəkildə icra edir
    
    Args:
        operation_name (str): Əməliyyatın adı
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except PermissionError as e:
                error_msg = f"❌ İcazə xətası - {operation_name}: {str(e)}"
                logger.error(error_msg)
                add_log(error_msg, "error")
                print(error_msg)
            except FileNotFoundError as e:
                error_msg = f"❌ Fayl tapılmadı - {operation_name}: {str(e)}"
                logger.error(error_msg)
                add_log(error_msg, "error")
                print(error_msg)
            except ConnectionError as e:
                error_msg = f"❌ Bağlantı xətası - {operation_name}: {str(e)}"
                logger.error(error_msg)
                add_log(error_msg, "error")
                print(error_msg)
            except Exception as e:
                error_msg = f"❌ Ümumi xəta - {operation_name}: {str(e)}"
                full_traceback = traceback.format_exc()
                logger.error(f"{error_msg}\n{full_traceback}")
                add_log(error_msg, "error")
                print(error_msg)
                print(f"📋 Ətraflı xəta: {full_traceback}")
                
        return wrapper
    return decorator

def log_function_call(func_name: str, args: tuple = (), kwargs: dict = {}):
    """
    Funksiya çağırışını loglayır
    
    Args:
        func_name (str): Funksiya adı
        args (tuple): Arqumentlər
        kwargs (dict): Açar-dəyər arqumentləri
    """
    try:
        add_log(f"🔧 Funksiya çağırışı: {func_name}", "info")
        logger.info(f"Function called: {func_name} with args: {args}, kwargs: {kwargs}")
    except Exception as e:
        print(f"Log yazarkən xəta: {e}")

class ErrorHandler:
    """Səhv idarəetmə sinifi"""
    
    @staticmethod
    def handle_telegram_error(error, context: str = ""):
        """Telegram API xətalarını idarə edir"""
        error_msg = f"📱 Telegram xətası {context}: {str(error)}"
        logger.error(error_msg)
        add_log(error_msg, "error")
        print(error_msg)
        
    @staticmethod
    def handle_file_error(error, file_path: str = ""):
        """Fayl əməliyyatı xətalarını idarə edir"""
        error_msg = f"📁 Fayl xətası {file_path}: {str(error)}"
        logger.error(error_msg)
        add_log(error_msg, "error")
        print(error_msg)
        
    @staticmethod
    def handle_json_error(error, operation: str = ""):
        """JSON xətalarını idarə edir"""
        error_msg = f"📄 JSON xətası {operation}: {str(error)}"
        logger.error(error_msg)
        add_log(error_msg, "error")
        print(error_msg)

# Xəta növləri
class BotError(Exception):
    """Bot xətaları üçün əsas sinif"""
    pass

class ConfigurationError(BotError):
    """Konfiqurasiya xətaları"""
    pass

class AuthenticationError(BotError):
    """Autentifikasiya xətaları"""
    pass

class PermissionDeniedError(BotError):
    """İcazə rədd edilmə xətaları"""
    pass
