# Discord AIGENCY Bot

Bu proje, AIGENCY API'si ile etkileşimde bulunarak Discord'da kullanıcıların yapay zeka modelleriyle sohbet etmelerini sağlayan bir bottur.

## Özellikler

- Kullanıcılar e-posta ve şifreleriyle giriş yapabilirler.
- Mevcut yapay zeka modellerinin listesini görebilirler. (Komut: !ai)
- Seçilen bir yapay zeka modeliyle sohbet başlatabilirler.
- Sohbeti sıfırlayabilir veya kapatabilirler. (Komut: !reset)
- Oturum durumu kontrol edebilirler. (Komut: !durum)
- Yardım komutları için !yardim komutunu kullanabilirsiniz.

## Kurulum

1. Bu projeyi bilgisayarınıza klonlayın.
2. https://discord.com/developers/ adresinden uygulamanızı oluşturup Token bilginizi main.py içinde 5. satırdaki ilgili yere yapıştırın.
3. AI ile sohbet edebilmek için <bold>https://aigency.dev</bold> adresinde hesabınızın olması gerekmektedir.

   ```bash
   git clone https://github.com/ecloud-bh/discord-aigency-bot.git
   cd discord-aigency-bot
   python main.py
