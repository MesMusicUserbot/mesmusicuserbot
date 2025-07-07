
import os
import datetime

def create_py_file(file_name, content="", description=""):
    """
    Yeni Python faylını Menim_PY_modullarim qovluğunda yaradır
    
    Args:
        file_name (str): Fayl adı (.py uzantısı avtomatik əlavə edilir)
        content (str): Faylın məzmunu (isteğe bağlı)
        description (str): Faylın təsviri (isteğe bağlı)
    
    Returns:
        str: Yaradılan faylın tam yolu
    """
    # .py uzantısını yoxla və əlavə et
    if not file_name.endswith('.py'):
        file_name += '.py'
    
    # Tam fayl yolunu təyin et
    file_path = os.path.join("Menim_PY_modullarim", file_name)
    
    # Əgər fayl artıq mövcuddursa, xəbərdarlıq ver
    if os.path.exists(file_path):
        print(f"⚠️ {file_name} artıq mövcuddur!")
        return file_path
    
    # Standart Python faylı başlığı
    if not content:
        content = f'''"""
{description if description else f"{file_name} - Avtomatik yaradılmış modul"}

Yaradılma tarixi: {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}
"""

# Lazımi kitabxanaları import edin
from telethon import events
from telethon.tl.types import *

# Əsas funksiyalarınızı burada yazın

def register_handlers(client):
    """Bu modulun handler-lərini qeydiyyata alır"""
    pass

# Əgər lazımdırsa, əlavə funksiyalar əlavə edin
'''
    
    try:
        # Qovluğun mövcudluğunu təmin et
        os.makedirs("Menim_PY_modullarim", exist_ok=True)
        
        # Faylı yarat
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ {file_name} uğurla yaradıldı: {file_path}")
        return file_path
        
    except Exception as e:
        print(f"❌ Fayl yaradılarkən xəta: {e}")
        return None

def list_py_modules():
    """Menim_PY_modullarim qovluğundakı bütün Python fayllarını siyahıya alır"""
    module_dir = "Menim_PY_modullarim"
    
    if not os.path.exists(module_dir):
        print("❌ Menim_PY_modullarim qovluğu mövcud deyil!")
        return []
    
    py_files = []
    for file in os.listdir(module_dir):
        if file.endswith('.py') and file != '__init__.py':
            py_files.append(file)
    
    return sorted(py_files)

def show_module_info(module_name):
    """Modulun ətraflı məlumatlarını göstərir"""
    if not module_name.endswith('.py'):
        module_name += '.py'
    
    file_path = os.path.join("Menim_PY_modullarim", module_name)
    
    if not os.path.exists(file_path):
        print(f"❌ {module_name} mövcud deyil!")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fayl haqqında məlumat
        print(f"📄 Modul: {module_name}")
        print(f"📍 Yol: {file_path}")
        print(f"📊 Həcm: {len(content)} simvol")
        print(f"📝 Sətir sayı: {len(content.splitlines())}")
        
        # Docstring tap
        if '"""' in content:
            start = content.find('"""') + 3
            end = content.find('"""', start)
            if end != -1:
                docstring = content[start:end].strip()
                print(f"📋 Təsvir: {docstring}")
        
    except Exception as e:
        print(f"❌ Fayl oxunarkən xəta: {e}")

# Köhnə versiyalarla uyğunluq üçün
def create_module_file(name, content=""):
    """Köhnə versiya uyğunluğu üçün"""
    return create_py_file(name, content)
