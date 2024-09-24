# Discord AIGENCY Bot v2

## Kurulum ve Çalıştırma

Botu çalıştırmak için aşağıdaki adımları takip edebilirsiniz:

1. **Depoyu Kopyalayın:**
    ```bash
    git clone https://github.com/ecloud-bh/discord-aigency-bot.git
    cd discord-aigency-bot
    ```

2. **Gereksinimleri Yükleyin:**
    Python ve pip yüklü olduğundan emin olun ve ardından aşağıdaki komutu çalıştırarak gereksinimleri yükleyin:
    ```bash
    pip install -r requirements.txt
    ```

3. **Yapılandırma Dosyasını Ayarlayın:**
    `config.py` dosyasını oluşturun ve aşağıdaki değişkenleri tanımlayın:
    ```python
    DISCORD_TOKEN = 'Your-Discord-Token-Here'
    AGENCY_API_URL = 'https://aigency.dev/'
    ```

4. **Botu Başlatın:**
    ```bash
    python main.py
    ```

## Kullanım

Bot aşağıdaki komutları destekler:

- **!baslat:** Oturumu başlatır ve kullanıcıdan e-posta adresi ve şifresini ister.
- **!yardim:** Mevcut komutların listesini gösterir.
- **!sifirla:** Sohbeti sıfırlar.
- **!ai:** AI listesini görüntüler.
- **!kapat:** Mevcut sohbeti kapatır.
- **!durum:** Mevcut oturum durumunu kontrol eder.
- **/img:** AIGENCY Image Model v1 ile resim oluşturur.

Dosya gönderdiğinizde, dosya içeriği analiz edilir ve ilgili AI modeli ile işlenir. Resim gönderdiğinizde, resim analizi yapılır.

## Güncellemeler

- **HTTP İstekleri için Yeniden Deneme:** HTTP istekleri için yeniden deneme mantığı eklendi, böylece zaman aşımı hataları durumunda istekler otomatik olarak yeniden denenir.
- **Komut İşleme İyileştirmeleri:** Komut işleme ve kullanıcı oturumu yönetimi iyileştirildi.
- **AI Sohbet Yönetimi:** Giriş yapma, AI listesi alma, sohbet başlatma, mesaj gönderme ve sohbet kapatma gibi işlemler için fonksiyonlar eklendi.
- **Dosya ve Resim İşleme:** Dosya ve resim yükleme ve analiz yetenekleri geliştirildi.
- **Geliştirilmiş Loglama:** Bot operasyonları boyunca ayrıntılı loglama eklendi.

Güncellenmiş botu kullanarak daha güvenilir ve kullanıcı dostu bir deneyim elde edebilirsiniz.
