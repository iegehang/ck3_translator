
# Crusader Kings III Türkçe Çeviri Scripti (Microsoft Translator Text API (Azure))

Oyunun localization dizininde yer alan .yml dosyalarını Microsoft Translator Text API (Azure) kullanarak otomatik olarak çevirir. Bunu yaparken değişkenleri bozmaz. 

## Çalıştırma
Scriptleri çalıştırmak son derece basittir. Scriptlerin bulunduğu dizinde sırayla şu komutları çalıştırın;

1. `pip install googletrans==4.0.0-rc1` #Azure'un kullanılamadığı yerlerde Google Translate kullanabilmek için. Scripte kolayca entegre edebilirsiniz. Ancak verimlilik olarak çok fark ettiğini belirtmeliyim. 
2. `python translate.py` veya diğerlerini...

### Gereksinimler
- Öncelikle hizmeti kullanabilmek için bir Azure hesabına ve kullanım anahtarlarına ihtiyacınız var. Ücretsiz kredi limit hediyeli bir hesap açabilir veya öğrenciyseniz .edu uzantılı öğrenci e-posta adresinizle Azure Students programına kayıt olabilir ve Microsoft Translator Text API'yı kullanabilirsiniz. 

### Sınırlamalar
İstek başına maksimum karakter sayısı: 5.000'dir. Toplamda da 2 milyon karakter limiti vardır. Ve API'de 429 kısıtlamaları da mevcut. Scriptler içerisinde bu durumlara karşı interval ve timeout önlemleri var. Çevirilerin tamamı için ortalama 7-8m istek kotası harcanıyor. Her API key'inin kullanım istatistiklerinin ay başında sıfırlandığını düşünürsek böyle bir çalışmaya ay sonu başlamakta fayda var. 

### Microsoft Translator Text API nasıl oluşturulur?
https://learn.microsoft.com/en-us/azure/ai-services/translator/how-to/create-translator-resource adresindeki yönergeleri takip edin. Burada önemli olan detay API için kullanılacak bölgenin `global` olması. Eğer ilk kez Kaynak Grubu oluştururken Global seçmenize izin vermiyorsa; kaynak grubunu önce kendi menüsünden oluşturup sonra o grubun içerisinde Translator API'yi Create ederek global seçimini yapabilirsiniz. Ardından key bölümünden API anahtarlarınızı alabilirsiniz.

## translate.py
.yml dosyalarını oyunun ihtiyaç duyduğu değişkenleri bozmadan çevirir.

## fix_keys.py
Çeviri sonrası oluşan "key" bozulmalarını düzeltir. "value" değerlerine dokunmaz.

## copy_keys.py
Daha önce yapmış olduğunuz çevirileri .yml dosyaların içindeki key'lere göre (eşleştiğinde) hedef dizinindeki dosyalara aktarır. Örneğin; daha önce çevirisi yapılan "vassal": "vasal" ifadesini hedef .yml'lar içerisinde bulduğunda karşılık gelen ifadenin üzerine yazar.
