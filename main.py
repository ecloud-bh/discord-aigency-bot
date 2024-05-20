import discord
import requests
import asyncio

TOKEN = 'DC APP KODUNUZ'  # Discord bot ve/veya bot token
AGENCY_API_URL = 'https://aigency.dev/api/v1/'

client = discord.Client(intents=discord.Intents.default())
user_sessions = {}  # Kullanıcı oturumlarını izlemek için bir sözlük

# Oturum zaman aşımı kontrolü için arka plan görevi
async def session_timeout_check():
    while True:
        await asyncio.sleep(300)  # Her 5 dakikada bir kontrol et
        for user_id, session in list(user_sessions.items()):
            if 'last_active' in session and (discord.utils.utcnow() - session['last_active']).total_seconds() > 1800:  # 30 dakika
                del user_sessions[user_id]
                user = await client.fetch_user(user_id)
                await user.send("Oturumunuz zaman aşımına uğradı. Tekrar başlatmak için `!baslat` yazın.")

def login(email, password):
    url = AGENCY_API_URL + 'login/'
    data = {'email': email, 'password': password}
    response = requests.post(url, data=data)
    return response.json()

def ai_team_list(access_token):
    url = AGENCY_API_URL + 'ai-team-list/?access_token=' + access_token
    response = requests.get(url)
    print(f"AI Team List Response: {response.text}")  # Yanıtı terminale yazdır
    if response.status_code != 200:
        return {"error": f"Failed to fetch AI team list: {response.status_code} {response.reason}"}
    return response.json()

def new_chat(access_token, ai_id):
    url = AGENCY_API_URL + 'newChat'
    data = {'access_token': access_token, 'ai_id': ai_id}
    response = requests.post(url, data=data)
    return response.json()

def send_message(access_token, chat_id, message):
    url = AGENCY_API_URL + 'sendMessage'
    data = {'access_token': access_token, 'chat_id': chat_id, 'message': message}
    response = requests.post(url, data=data)
    return response.json()

def reset_chat(access_token, chat_id):
    url = AGENCY_API_URL + 'resetChat'
    data = {'access_token': access_token, 'chat_id': chat_id}
    response = requests.post(url, data=data)
    return response.json()

def close_chat(access_token, chat_id):
    url = AGENCY_API_URL + 'closeChat'
    data = {'access_token': access_token, 'chat_id': chat_id}
    response = requests.post(url, data=data)
    return response.json()

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user_id = message.author.id
    content = message.content.split()
    command = content[0]

    if command == '!baslat':
        user_sessions[user_id] = {'stage': 'email', 'last_active': discord.utils.utcnow()}
        await message.channel.send("Lütfen e-posta adresinizi girin:")

    elif command == '!yardim':
        help_message = (
            "Mevcut komutlar:\n"
            "`!baslat`: Oturumu başlatın.\n"
            "`!reset`: Sohbeti sıfırlayın.\n"
            "`!ai`: AI listesini görüntüleyin.\n"
            "`!kapat`: Sohbeti kapatın.\n"
            "`!durum`: Mevcut oturum durumunuzu kontrol edin.\n"
        )
        await message.channel.send(help_message)

    elif user_id in user_sessions:
        session = user_sessions[user_id]
        session['last_active'] = discord.utils.utcnow()
        stage = session.get('stage')

        if stage == 'email':
            session['email'] = message.content
            session['stage'] = 'password'
            await message.channel.send("Lütfen şifrenizi girin:")

        elif stage == 'password':
            session['password'] = message.content
            email = session['email']
            password = session['password']
            response = login(email, password)
            if 'error' in response:
                await message.channel.send(response['error'])
                del user_sessions[user_id]
            else:
                session['access_token'] = response['access_token']
                session['stage'] = 'logged_in'
                await message.channel.send("Başarıyla giriş yapıldı! AI listesini getiriyorum...")
                access_token = response['access_token']
                ai_response = ai_team_list(access_token)
                print(f"AI Team List API Response: {ai_response}")  # Yanıtı terminale yazdır
                if 'error' in ai_response:
                    await message.channel.send(ai_response['error'])
                    del user_sessions[user_id]
                else:
                    ai_list = ai_response
                    session['ai_list'] = ai_list
                    ai_list_message = "AI Listesi:\n"
                    for i, ai in enumerate(ai_list):
                        ai_list_message += f"{i+1}. {ai['ai_name']} (ID: {ai['ai_id']})\n"
                    await message.channel.send(ai_list_message)
                    await message.channel.send("Bir AI seçmek için numarasını yazın.")
                    session['stage'] = 'select_ai'

        elif stage == 'select_ai':
            try:
                selection = int(message.content) - 1
                ai_list = session['ai_list']
                if 0 <= selection < len(ai_list):
                    ai_id = ai_list[selection]['ai_id']
                    access_token = session['access_token']
                    response = new_chat(access_token, ai_id)
                    if 'error' in response:
                        await message.channel.send(response['error'])
                    else:
                        session['chat_id'] = response['chat_id']
                        session['stage'] = 'chatting'
                        await message.channel.send(f"{ai_list[selection]['ai_name']} ile sohbet başlatıldı! (Chat ID: {response['chat_id']})")
                else:
                    await message.channel.send("Geçersiz seçim. Lütfen listedeki numaralardan birini seçin.")
            except ValueError:
                await message.channel.send("Lütfen geçerli bir numara girin.")

        elif stage == 'chatting':
            if command == '!reset':
                chat_id = session['chat_id']
                access_token = session['access_token']
                response = reset_chat(access_token, chat_id)
                if 'error' in response:
                    await message.channel.send(response['error'])
                else:
                    session['stage'] = 'select_ai'  # Kullanıcıya tekrar AI seçtirmek için stage değiştiriliyor
                    del session['chat_id']
                    await message.channel.send("Sohbet sıfırlandı. Lütfen yeniden bir AI seçin.")
                    ai_list_message = "AI Listesi:\n"
                    for i, ai in enumerate(session['ai_list']):
                        ai_list_message += f"{i+1}. {ai['ai_name']} (ID: {ai['ai_id']})\n"
                    await message.channel.send(ai_list_message)

            elif command == '!ai':
                access_token = session['access_token']
                ai_response = ai_team_list(access_token)
                if 'error' in ai_response:
                    await message.channel.send(ai_response['error'])
                else:
                    ai_list = ai_response
                    session['ai_list'] = ai_list
                    ai_list_message = "AI Listesi:\n"
                    for i, ai in enumerate(ai_list):
                        ai_list_message += f"{i+1}. {ai['ai_name']} (ID: {ai['ai_id']})\n"
                    await message.channel.send(ai_list_message)

            elif command == '!kapat':
                chat_id = session['chat_id']
                access_token = session['access_token']
                response = close_chat(access_token, chat_id)
                if 'error' in response:
                    await message.channel.send(response['error'])
                else:
                    await message.channel.send("Sohbet kapatıldı.")
                    del user_sessions[user_id]

            elif command == '!durum':
                stage_message = f"Mevcut durum: {session['stage']}"
                await message.channel.send(stage_message)

            else:
                if 'chat_id' not in session:
                    await message.channel.send("Geçerli bir AI seçimi yapmalısınız.")
                    return

                chat_id = session['chat_id']
                access_token = session['access_token']
                msg = message.content
                response = send_message(access_token, chat_id, msg)
                print(f"Send Message Response: {response}")  # Yanıtı terminale yazdır
                if 'error' in response:
                    await message.channel.send(response['error'])
                else:
                    if 'answer' in response and 'message' in response['answer']:
                        await message.channel.send(response['answer']['message'])
                    else:
                        await message.channel.send("Yanıt alınamadı. Gelen yanıt: " + str(response))

async def main():
    await client.start(TOKEN)
    await session_timeout_check()

asyncio.run(main())
