import logging
import discord
from discord.ext import commands
import httpx
from io import BytesIO

from config import DISCORD_TOKEN, AGENCY_API_URL

# Logger ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

user_sessions = {}  # Kullanıcı oturumlarını izlemek için bir sözlük

# HTTP isteklerinde yeniden deneme işlemlerini yönetmek için bir yardımcı fonksiyon
async def http_request_with_retries(method, url, **kwargs):
    max_retries = 5
    retries = 0
    while retries < max_retries:
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                if method == 'GET':
                    response = await client.get(url, **kwargs)
                elif method == 'POST':
                    response = await client.post(url, **kwargs)
                else:
                    raise ValueError("Unsupported HTTP method")
            return response
        except httpx.ReadTimeout:
            retries += 1
            logger.warning(f"Zaman aşımı, yeniden deneme {retries}/{max_retries}")
            if retries >= max_retries:
                logger.error("Maksimum yeniden deneme sayısına ulaşıldı.")
                return None
        except httpx.RequestError as exc:
            logger.error(f"HTTP isteği başarısız oldu: {exc}")
            return None

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # GUILD_MEMBERS niyetini etkinleştiriyoruz

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f'Bot {bot.user.name} olarak giriş yaptı')

@bot.command(name='baslat')
async def baslat(ctx):
    logger.info("!baslat komutu alındı.")
    user_id = str(ctx.author.id)
    user_sessions[user_id] = {'stage': 'email'}
    await yardim(ctx)
    await ctx.send('Lütfen e-posta adresinizi girin:')

@bot.command(name='yardim')
async def yardim(ctx):
    logger.info("!yardim komutu alındı.")
    help_message = (
        "Mevcut komutlar:\n"
        "!baslat: Oturumu başlatın.\n"
        "!sifirla: Sohbeti sıfırlayın.\n"
        "!ai: AI listesini görüntüleyin.\n"
        "!kapat: Sohbeti kapatın.\n"
        "!durum: Mevcut oturum durumunuzu kontrol edin.\n"
        "/img: AIGENCY Image Model v1 ile resim oluşturun.\n"
        "\n"
        "Kodlarınızı göndereceğiniz zaman dosya olarak gönderebilirsiniz.\n"
        "Resim gönderirken herhangi bir komut girmeyin, sadece resmi yükleyin.\n\n"
        "eCloud Tech.\n"
    )
    await ctx.send(help_message)

async def login(email, password):
    logger.info(f"Login: {email}")
    url = AGENCY_API_URL + 'login/'
    data = {'email': email, 'password': password}
    response = await http_request_with_retries('POST', url, data=data)
    if response:
        return response.json()
    else:
        return {"error": "Giriş işlemi başarısız oldu"}

async def ai_team_list(access_token):
    logger.info("AI takım listesi alınıyor...")
    url = AGENCY_API_URL + 'ai-team-list/?access_token=' + access_token
    response = await http_request_with_retries('GET', url)
    if response and response.status_code == 200:
        return response.json()
    else:
        return {"error": "AI takım listesi alınamadı"}

async def new_chat(access_token, ai_id):
    logger.info(f"Yeni sohbet başlatılıyor... AI ID: {ai_id}")
    url = AGENCY_API_URL + 'newChat'
    data = {'access_token': access_token, 'ai_id': ai_id}
    response = await http_request_with_retries('POST', url, data=data)
    if response:
        return response.json()
    else:
        return {"error": "Yeni sohbet başlatılamadı"}

async def send_message(access_token, chat_id, message):
    logger.info(f"Mesaj gönderiliyor... Chat ID: {chat_id}, Mesaj: {message}")
    url = AGENCY_API_URL + 'sendMessage'
    data = {'access_token': access_token, 'chat_id': chat_id, 'message': message}
    response = await http_request_with_retries('POST', url, data=data)
    if response:
        return response.json()
    else:
        return {"error": "Mesaj gönderme işlemi başarısız oldu"}

async def close_chat(access_token, chat_id):
    logger.info(f"Sohbet kapatılıyor... Chat ID: {chat_id}")
    url = AGENCY_API_URL + 'closeChat'
    data = {'access_token': access_token, 'chat_id': chat_id}
    response = await http_request_with_retries('POST', url, data=data)
    if response:
        return response.json()
    else:
        return {"error": "Sohbet kapatılamadı"}

async def reset_chat(access_token, chat_id):
    logger.info(f"Sohbet sıfırlanıyor... Chat ID: {chat_id}")
    url = AGENCY_API_URL + 'resetChat'
    data = {'access_token': access_token, 'chat_id': chat_id}
    response = await http_request_with_retries('POST', url, data=data)
    if response:
        return response.json()
    else:
        return {"error": "Sohbet sıfırlanamadı"}

async def send_file(access_token, chat_id, file_content, filename, prompt="Kodlarımı analiz eder misin?"):
    logger.info("Dosya gönderiliyor...")
    url = AGENCY_API_URL + 'sendFile'
    files = {'file': (filename, file_content)}
    data = {'access_token': access_token, 'chat_id': chat_id, 'prompt': prompt}
    response = await http_request_with_retries('POST', url, files=files, data=data)
    if response:
        try:
            return response.json()
        except ValueError:
            logger.error("API'den geçersiz JSON yanıtı alındı")
            return {"error": "API'den geçersiz JSON yanıtı alındı"}
    else:
        return {"error": "Dosya gönderme işlemi başarısız oldu"}

async def send_image(access_token, chat_id, image_content, prompt="Analiz eder misin?"):
    logger.info("Resim gönderiliyor...")
    url = AGENCY_API_URL + 'sendImage'
    files = {'image': ('image.png', image_content, 'image/png')}
    data = {'access_token': access_token, 'chat_id': chat_id, 'prompt': prompt}
    response = await http_request_with_retries('POST', url, files=files, data=data)
    if response:
        try:
            response_json = response.json()
            logger.info(f"Resim gönderme yanıtı: {response_json}")
            return response_json
        except ValueError:
            logger.error("API'den geçersiz JSON yanıtı alındı")
            return {"error": "API'den geçersiz JSON yanıtı alındı"}
    else:
        return {"error": "Resim gönderme işlemi başarısız oldu"}

async def send_aigency_image(access_token, chat_id, prompt):
    logger.info("AIGENCY Image Model v1 istek gönderiliyor...")
    url = AGENCY_API_URL + 'DalleCreate'
    data = {
        'access_token': access_token,
        'chat_id': chat_id,
        'prompt': prompt
    }
    response = await http_request_with_retries('POST', url, data=data)
    if response:
        try:
            response_json = response.json()
            logger.info(f"AIGENCY Image Model yanıtı: {response_json}")
            return response_json
        except ValueError:
            logger.error("API'den geçersiz JSON yanıtı alındı")
            return {"error": "API'den geçersiz JSON yanıtı alındı"}
    else:
        return {"error": "AIGENCY Image Model v1 istek gönderme işlemi başarısız oldu"}

async def send_long_message(channel, message):
    while message:
        chunk = message[:2000]
        message = message[2000:]
        await channel.send(chunk)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_id = str(message.author.id)
    content = message.content

    if not content and message.attachments:
        await handle_image(message)
        return

    if not content:
        return

    command = content.split()[0]

    logger.info(f"Komut: {command}")

    if command == '!baslat':
        await baslat_command(message)
    elif command == '!yardim':
        await yardim_command(message)
    else:
        if user_id in user_sessions:
            session = user_sessions[user_id]
            stage = session.get('stage')

            if stage == 'email':
                session['email'] = content
                session['stage'] = 'password'
                await message.channel.send("Lütfen parolanızı girin:")

            elif stage == 'password':
                session['password'] = content
                email = session['email']
                password = session['password']
                response = await login(email, password)
                if 'access_token' not in response:
                    await message.channel.send(f"Giriş başarısız: {response.get('error', 'Bilinmeyen bir hata oluştu.')}\nÜye değilseniz, aşağıdaki bağlantıya tıklayarak kayıt olun.\nhttps://aigency.dev/sign-up")
                    del user_sessions[user_id]
                else:
                    session['access_token'] = response['access_token']
                    session['stage'] = 'logged_in'
                    await message.channel.send("Başarıyla giriş yapıldı! AI listesini getiriyorum...")
                    access_token = response['access_token']
                    ai_response = await ai_team_list(access_token)
                    if 'error' in ai_response:
                        await message.channel.send(ai_response['error'])
                        del user_sessions[user_id]
                    else:
                        ai_list = ai_response
                        session['ai_list'] = ai_list
                        ai_list_message = "AI Listesi:\n\n"
                        for i, ai in enumerate(ai_list):
                            ai_list_message += f"{i+1}. {ai['ai_name']} - (ID: {ai['ai_id']})\n{ai['ai_desc']}\n\n"
                        await send_long_message(message.channel, ai_list_message)
                        await message.channel.send("Bir AI seçmek için numarasını yazın.")
                        session['stage'] = 'select_ai'

            elif stage == 'select_ai':
                try:
                    selection = int(content) - 1
                    ai_list = session['ai_list']
                    if 0 <= selection < len(ai_list):
                        ai_id = ai_list[selection]['ai_id']
                        access_token = session['access_token']
                        response = await new_chat(access_token, ai_id)
                        if 'error' in response:
                            await message.channel.send(response['error'])
                        else:
                            session['chat_id'] = response['chat_id']
                            session['ai_id'] = ai_id  # AI ID'yi oturum bilgisine ekleyin
                            session['stage'] = 'chatting'
                            await message.channel.send(f"{ai_list[selection]['ai_name']} ile sohbet başlatıldı! (Chat ID: {response['chat_id']})")
                    else:
                        await message.channel.send("Geçersiz seçim. Lütfen listedeki numaralardan birini seçin.")
                except ValueError:
                    await message.channel.send("Lütfen geçerli bir numara girin.")

            elif stage == 'chatting':
                if command == '!sifirla':
                    chat_id = session['chat_id']
                    access_token = session['access_token']
                    response = await reset_chat(access_token, chat_id)
                    if 'error' in response:
                        await message.channel.send(response['error'])
                    else:
                        session['stage'] = 'select_ai'
                        del session['chat_id']
                        await message.channel.send("Sohbet sıfırlandı. Lütfen yeniden bir AI seçin.")
                        ai_list_message = "AI Listesi:\n\n"
                        for i, ai in enumerate(session['ai_list']):
                            ai_list_message += f"{i+1}. {ai['ai_name']} - (ID: {ai['ai_id']})\n{ai['ai_desc']}\n\n"
                        await send_long_message(message.channel, ai_list_message)

                elif command == '!ai':
                    access_token = session['access_token']
                    ai_response = await ai_team_list(access_token)
                    if 'error' in ai_response:
                        await message.channel.send(ai_response['error'])
                    else:
                        ai_list = ai_response
                        session['ai_list'] = ai_list
                        ai_list_message = "AI Listesi:\n\n"
                        for i, ai in enumerate(ai_list):
                            ai_list_message += f"{i+1}. {ai['ai_name']} - (ID: {ai['ai_id']})\n{ai['ai_desc']}\n\n"
                        await send_long_message(message.channel, ai_list_message)

                elif command == '!kapat':
                    chat_id = session['chat_id']
                    access_token = session['access_token']
                    response = await close_chat(access_token, chat_id)
                    if 'error' in response:
                        await message.channel.send(response['error'])
                    else:
                        await message.channel.send("Sohbet kapatıldı.")
                        del user_sessions[user_id]

                elif command == '!durum':
                    stage_message = f"Mevcut durum: {session['stage']}"
                    await message.channel.send(stage_message)

                elif command.startswith('!img'):
                    access_token = session['access_token']
                    chat_id = session['chat_id']
                    prompt = content[len('!img '):]

                    if not prompt:
                        await message.channel.send("Lütfen bir prompt girin. Örneğin: /img Kafası karışmış bir yazılımcı oluştur.")
                        return

                    response = await send_aigency_image(access_token, chat_id, prompt)

                    if response is None:
                        await message.channel.send("API'den yanıt alınamadı.")
                    elif 'error' in response:
                        await message.channel.send(response['error'])
                    else:
                        logger.info(f"Yanıt: {response}")  # Yanıtı logla
                        if response.get('status') == 1 and 'message' in response:
                            message_content = response['message']
                            if 'data' in message_content and len(message_content['data']) > 0:
                                image_url = message_content['data'][0]['url']
                                await message.channel.send(f"Görsel başarıyla oluşturuldu: {image_url}")
                            else:
                                await message.channel.send("Yanıt alınamadı. Gelen yanıt: " + str(response))
                        else:
                            await message.channel.send("Yanıt alınamadı. Gelen yanıt: " + str(response))

                else:
                    if 'chat_id' not in session:
                        await message.channel.send("Geçerli bir AI seçimi yapmalısınız.")
                        return

                    chat_id = session['chat_id']
                    access_token = session['access_token']
                    msg = content
                    response = await send_message(access_token, chat_id, msg)
                    if 'error' in response:
                        await message.channel.send(response['error'])
                    else:
                        if 'answer' in response and 'message' in response['answer']:
                            await message.channel.send(response['answer']['message'])
                        else:
                            await message.channel.send("Yanıt alınamadı. Gelen yanıt: " + str(response))

async def handle_image(message):
    user_id = str(message.author.id)
    if user_id not in user_sessions:
        await message.channel.send("Lütfen önce !baslat komutunu kullanarak oturum açın.")
        return

    session = user_sessions[user_id]
    if session.get('stage') != 'chatting':
        await message.channel.send("Geçerli bir AI seçimi yapmalısınız.")
        return

    access_token = session['access_token']
    chat_id = session['chat_id']

    for attachment in message.attachments:
        file_content = BytesIO()
        await attachment.save(file_content)
        file_content.seek(0)
        
        prompt = "Analiz eder misin?"
        if session.get('ai_id') == 53:  # Altay AI seçildiyse özel prompt kullan
            prompt = "Görüntüyü analiz eder misin?"

        response = await send_image(access_token, chat_id, file_content, prompt)
        
        if response is None:
            await message.channel.send("API'den yanıt alınamadı.")
        elif 'error' in response:
            await message.channel.send(response['error'])
        else:
            answer = response.get('answer')
            if answer is None:
                await message.channel.send("Yanıt alınamadı.")
            else:
                response_message = answer.get('message', 'Yanıt alınamadı.')
                await message.channel.send(f"Fotoğraf başarıyla gönderildi.\nYanıt: {response_message}")

@bot.event
async def on_message_edit(before, after):
    await on_message(after)

@bot.event
async def on_raw_reaction_add(payload):
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    await on_message(message)

@bot.event
async def on_message_delete(message):
    await on_message(message)

@bot.event
async def on_raw_message_delete(payload):
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    await on_message(message)

@bot.event
async def on_message_bulk_delete(messages):
    for message in messages:
        await on_message(message)

async def baslat_command(message):
    logger.info("!baslat komutu alındı.")
    user_id = str(message.author.id)
    user_sessions[user_id] = {'stage': 'email'}
    await yardim_command(message)
    await message.channel.send('Lütfen e-posta adresinizi girin:')

async def yardim_command(message):
    logger.info("!yardim komutu alındı.")
    help_message = (
        "Mevcut komutlar:\n"
        "!baslat: Oturumu başlatın.\n"
        "!sifirla: Sohbeti sıfırlayın.\n"
        "!ai: AI listesini görüntüleyin.\n"
        "!kapat: Sohbeti kapatın.\n"
        "!durum: Mevcut oturum durumunuzu kontrol edin.\n"
        "/img: AIGENCY Image Model v1 ile resim oluşturun.\n"
        "\n"
        "Kodlarınızı göndereceğiniz zaman dosya olarak gönderebilirsiniz.\n"
        "Resim gönderirken herhangi bir komut girmeyin, sadece resmi yükleyin.\n\n"
        "eCloud Tech.\n"
    )
    await message.channel.send(help_message)

bot.run(DISCORD_TOKEN)
