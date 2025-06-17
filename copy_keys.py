import os
import re

# === Dizini Tanımla ===
a_dizin = r"C:\ESKİ ÇEVİRİ PATH"
b_dizin = r"C:\YENİ ÇEVİRİ PATH"

def parse_yml_to_dict(path):
    """YML dosyasındaki key-value çiftlerini sözlük olarak döndürür."""
    key_value = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line and '"' in line and not line.strip().startswith("#"):
                match = re.match(r'^([^\s#][^:]*):0\s+"(.*)"$', line.strip())
                if match:
                    key = match.group(1).strip()
                    value = match.group(2).strip()
                    key_value[key] = value
    return key_value

def replace_values_in_file(b_path, updated_dict):
    """B dosyasındaki satırları, updated_dict'e göre değiştirip tekrar yazar."""
    with open(b_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        match = re.match(r'^([^\s#][^:]*):0\s+"(.*)"$', line.strip())
        if match:
            key = match.group(1).strip()
            if key in updated_dict:
                new_line = f'{key}:0 "{updated_dict[key]}"\n'
                new_lines.append(new_line)
                continue
        new_lines.append(line)

    with open(b_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

def update_matching_files():
    print("🔄 Güncelleme başlatılıyor...\n")

    for root, _, files in os.walk(a_dizin):
        for file in files:
            if not file.endswith(".yml"):
                continue

            a_path = os.path.join(root, file)
            relative_path = os.path.relpath(a_path, a_dizin)
            b_path = os.path.join(b_dizin, relative_path)

            if not os.path.exists(b_path):
                print(f"❌ Eşleşen dosya yok, atlandı: {relative_path}")
                continue

            print(f"✅ Eşleşti: {relative_path} -> Güncelleniyor...")

            try:
                a_dict = parse_yml_to_dict(a_path)
                replace_values_in_file(b_path, a_dict)
            except Exception as e:
                print(f"⚠️ Hata oluştu: {file} -> {e}")

    print("\n🎉 Tüm dosyalar başarıyla güncellendi.")

# === Ana çalıştırıcı ===
if __name__ == "__main__":
    update_matching_files()
