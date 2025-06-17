import os
import re
import time
import requests

# === Ayarlar ===
kaynak_klasor = r"C:\Program Files (x86)\Steam\steamapps\common\Crusader Kings III\game\localization\english"
hedef_klasor = r"BELİRLEYECEĞİNİZ ÇIKTI KLASÖRÜ YOLU"


api_keys = [
    "AZURE_KEY_1_BURAYA_YAZILACAK",
    "AZURE_KEY_2_BURAYA_YAZILACAK"
]
region = "global"  # Azure panelinizdeki bölge ayarı buraya yazılır
endpoint = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&from=en&to=tr"

# === Özel yapıları koruma === Oyunun .yml dosyalarında bazı değişkenler var. Bunlara dikkat ediyoruz.
def tokenize(metin):
    pattern = re.compile(r'(\$[^$]+\$|\[[^\]]+\]|\{[^}]+\})')
    token_map = {}
    def replace(match):
        token = f"__TOKEN{len(token_map)}__"
        token_map[token] = match.group(0)
        return token
    return pattern.sub(replace, metin), token_map

def detokenize(metin, token_map):
    for token, orijinal in token_map.items():
        metin = metin.replace(token, orijinal)
    return metin
import random

# === Azure ile Çeviri İşlemi ===
def cevir_blok_azure(metin_listesi, max_retry=20):
    cevrilenler = []
    headers_base = {
        'Content-type': 'application/json'
    }

    tokenized_list = []
    token_maps = []

    for metin in metin_listesi:
        tokenized, token_map = tokenize(metin)
        tokenized_list.append(tokenized)
        token_maps.append(token_map)

    for deneme in range(1, max_retry + 1):
        try:
            body = [{"Text": t} for t in tokenized_list]

            headers = headers_base.copy()
            current_key = api_keys[(deneme - 1) % len(api_keys)]  # sırayla kullan
            headers['Ocp-Apim-Subscription-Key'] = current_key
            headers['Ocp-Apim-Subscription-Region'] = region

            response = requests.post(endpoint, headers=headers, json=body, timeout=20)
            
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 10))  # 10 varsayılan
                print(f"[Azure HATA] 429 Too Many Requests. Bekleniyor: {retry_after} saniye...")
                time.sleep(retry_after + 5)  # +5 buffer
                continue  # retry

            response.raise_for_status()

            translations = response.json()
            cevrilenler = [detokenize(item['translations'][0]['text'], token_maps[i]) for i, item in enumerate(translations)]

            delay = random.randint(15, 30)  # her istek arası gecikme (daha yavaş)
            print(f"🕒 Blok tamamlandı, bekleniyor: {delay} saniye...")
            time.sleep(delay)

            return cevrilenler

        except Exception as e:
            print(f"[Azure HATA] Deneme {deneme}: {e}")
            time.sleep(20 + deneme * 2)  # artan bekleme

    print("❌ HATA: Azure API ile çeviri başarısız oldu.")
    return metin_listesi

# === Blok oluşturucu ===
def bloklara_ayir_karaktere_gore(metin_listesi, max_char=4000):
    blok = []
    toplam = 0
    for metin in metin_listesi:
        if toplam + len(metin) > max_char:
            yield blok
            blok = []
            toplam = 0
        blok.append(metin)
        toplam += len(metin)
    if blok:
        yield blok

# === Dosya çevirici ===
def dosya_cevir(kaynak_dosya_yolu, hedef_dosya_yolu):
    with open(kaynak_dosya_yolu, "r", encoding="utf-8") as f:
        satirlar = f.readlines()

    yeni_satirlar = []
    cevrilecekler = []
    indeksler = []

    for i, satir in enumerate(satirlar):
        if satir.strip().startswith("l_english:"):
            yeni_satirlar.append("l_turkish:\n")
        elif satir.strip().startswith("#") or satir.strip() == "":
            yeni_satirlar.append(satir)
        elif ":" in satir and '"' in satir:
            try:
                cevrilcek_kisim = satir.split('"')[1]
                cevrilecekler.append(cevrilcek_kisim)
                indeksler.append(i)
                yeni_satirlar.append(None)
            except Exception as e:
                yeni_satirlar.append(satir)
                with open("ceviri_hatalari.log", "a", encoding="utf-8") as log:
                    log.write(f"HATA (split): {satir.strip()} -> {e}\n")
        else:
            yeni_satirlar.append(satir)

    cevrilenler = []
    for blok in bloklara_ayir_karaktere_gore(cevrilecekler):
        cevrilenler.extend(cevir_blok_azure(blok))

    for idx, ceviri in zip(indeksler, cevrilenler):
        orijinal_satir = satirlar[idx]
        eski = orijinal_satir.split('"')[1]
        yeni = orijinal_satir.replace(eski, ceviri)
        yeni_satirlar[idx] = yeni

    os.makedirs(os.path.dirname(hedef_dosya_yolu), exist_ok=True)
    with open(hedef_dosya_yolu, "w", encoding="utf-8") as f:
        f.writelines(yeni_satirlar)

    print(f"✅ Çevirildi: {kaynak_dosya_yolu}")

# === Klasör gezici ===
def klasor_gezin(kaynak, hedef):
    # İlk olarak .yml dosyaları listeleyelim
    yml_dosyalar = []
    for root, _, files in os.walk(kaynak):
        for file in files:
            if file.endswith(".yml"):
                yml_dosyalar.append(os.path.join(root, file))

    toplam_dosya = len(yml_dosyalar)
    print(f"📁 Toplam çevirilecek dosya sayısı: {toplam_dosya}\n")

    for index, kaynak_yol in enumerate(yml_dosyalar, start=1):
        hedef_yol = os.path.join(hedef, os.path.relpath(kaynak_yol, kaynak))

        if os.path.exists(hedef_yol):
            print(f"⏩ ({index}/{toplam_dosya}) Atlanıyor (var): {hedef_yol}")
            continue

        print(f"🔄 ({index}/{toplam_dosya}) Çeviriliyor: {kaynak_yol}")
        dosya_cevir(kaynak_yol, hedef_yol)
        time.sleep(2)  # isteğe bağlı: dosyalar arası bekleme


# === Ana Başlangıç ===
if __name__ == "__main__":
    print("⏳ Azure ile Crusader Kings III çevirisi başlatılıyor...")
    klasor_gezin(kaynak_klasor, hedef_klasor)
    print("🎉 Tüm çeviriler tamamlandı.")
