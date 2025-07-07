
#!/usr/bin/env python3
"""
Yeni Python modulunu yaratmaq üçün terminal əmri

İstifadə:
    python create_module.py <modul_adi> [təsvir]

Nümunə:
    python create_module.py yeni_sistem "Yeni sistem modulü"
"""

import sys
import os

# Menim_PY_modullarim qovluğunu Python path-a əlavə et
sys.path.insert(0, 'Menim_PY_modullarim')

from file_manager import create_py_file, list_py_modules

def main():
    if len(sys.argv) < 2:
        print("❌ İstifadə: python create_module.py <modul_adi> [təsvir]")
        print("\n📋 Mövcud modullar:")
        modules = list_py_modules()
        for i, module in enumerate(modules, 1):
            print(f"   {i}. {module}")
        return
    
    module_name = sys.argv[1]
    description = sys.argv[2] if len(sys.argv) > 2 else f"{module_name} modulü"
    
    print(f"🔨 {module_name} modulunu yaradılır...")
    
    # Modulu yarat
    file_path = create_py_file(module_name, description=description)
    
    if file_path:
        print(f"🎉 Modul uğurla yaradıldı!")
        print(f"📂 Fayl yolu: {file_path}")
        print(f"\n💡 İsteğe bağlı: main.py faylına əlavə etməyi unutmayın:")
        module_import = module_name.replace('.py', '')
        print(f"    from Menim_PY_modullarim.{module_import} import register_handlers")
        print(f"    register_handlers(client)")

if __name__ == "__main__":
    main()
