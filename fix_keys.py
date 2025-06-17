import os
import re

# === Ayarlar ===
kaynak_klasor = r"C:\Program Files (x86)\Steam\steamapps\common\Crusader Kings III\game\localization\english"
hedef_klasor = r"ÇEVİRİLERİN BULUNDUĞU DİZİN PATHI BURAYA YAZILIR"

# === Key doğrulama ve düzeltme işlevi ===
def keyleri_dogrula_ve_duzelt(kaynak_dosya, hedef_dosya):
    with open(kaynak_dosya, "r", encoding="utf-8") as f_kaynak:
        kaynak_satirlar = f_kaynak.readlines()

    with open(hedef_dosya, "r", encoding="utf-8") as f_hedef:
        hedef_satirlar = f_hedef.readlines()

    duzeltilmis_satirlar = []
    degisiklik_yapildi = False

    for i, satir in enumerate(hedef_satirlar):
        if i < len(kaynak_satirlar):
            kaynak_satir = kaynak_satirlar[i].strip()
            hedef_satir = satir.strip()

            # Yorum satırı, boş satır, veya dil etiketi ise aynen bırak
            if kaynak_satir.startswith("#") or kaynak_satir == "" or kaynak_satir.startswith("l_"):
                duzeltilmis_satirlar.append(satir)
                continue

            # Key yapısını yakala
            kaynak_key_match = re.match(r'^([^:]+:\d*)\s+"', kaynak_satir)
            hedef_key_match = re.match(r'^([^:]+:\d*)\s+"', hedef_satir)

            if kaynak_key_match and hedef_key_match:
                kaynak_key = kaynak_key_match.group(1)
                hedef_key = hedef_key_match.group(1)

                if kaynak_key != hedef_key:
                    # Key bozulmuş, düzelt
                    yeni_satir = re.sub(r'^([^:]+:\d*)', kaynak_key, hedef_satir)
                    duzeltilmis_satirlar.append(yeni_satir + "\n")
                    degisiklik_yapildi = True
                    continue

        # Değişiklik gerekmediyse satırı aynen ekle
        duzeltilmis_satirlar.append(satir)

    # Değişiklik yapıldıysa dosyayı yeniden yaz
    if degisiklik_yapildi:
        with open(hedef_dosya, "w", encoding="utf-8") as f:
            f.writelines(duzeltilmis_satirlar)
        print(f"✔️ Düzeltildi: {hedef_dosya}")
    else:
        print(f"✅ Keyler doğru: {hedef_dosya}")

# === Tüm dosyaları kontrol et ===
def klasordeki_keyleri_dogrula(kaynak_root, hedef_root):
    for root, _, files in os.walk(kaynak_root):
        for file in files:
            if file.endswith(".yml"):
                kaynak_yol = os.path.join(root, file)
                hedef_yol = os.path.join(hedef_root, os.path.relpath(kaynak_yol, kaynak_root))

                if not os.path.exists(hedef_yol):
                    print(f"⚠️ Hedef dosya eksik, atlanıyor: {hedef_yol}")
                    continue

                keyleri_dogrula_ve_duzelt(kaynak_yol, hedef_yol)

# === Ana çalıştırıcı ===
if __name__ == "__main__":
    print("🔍 Key doğrulama ve düzeltme başlatılıyor...")
    klasordeki_keyleri_dogrula(kaynak_klasor, hedef_klasor)
    print("🏁 Tüm dosyalar kontrol edildi.")
