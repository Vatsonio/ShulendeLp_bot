import datetime
import time
import telebot

TOKEN = '6810810967:AAGgW1F37wmpLSrd9b9spn8dQuWbrKzUdMw'
bot = telebot.TeleBot(TOKEN)

# Лічильник для функції update()
h=0

last_update = None

# Словник для зберігання message_id
messages_to_edit = {}

# Список дозволених id користувачів
allowed_users = [671904288]

# Початкова дата
current_time = datetime.datetime.now()

print("/// Бот запущений -->",current_time)

# Розклад для всіх днів, окрім середи
schedule = [
    {'start': '8:30', 'finish': '9:50'},
    {'start': '10:05', 'finish': '11:25'},
    {'start': '11:40', 'finish': '13:00'},
    {'start': '13:15', 'finish': '14:35'}
]

# Розклад для середи
wednesday_schedule = [
    {'start': '8:00', 'finish': '9:20'},
    {'start': '10:05', 'finish': '11:25'},
    {'start': '11:40', 'finish': '13:00'},
    {'start': '13:15', 'finish': '14:35'}
]

start_time = time.time()

def update():
    global h, last_update
    h=h+1
    current_time = datetime.datetime.now()
    last_update = current_time
    print("|",h,"| Запущена функція 'update' час: ",current_time.strftime('%Y-%m-%d %H:%M:%S'))
    current_minutes = current_time.hour * 60 + current_time.minute

    # Перевірка на вихідні
    if current_time.weekday() == 5 or current_time.weekday() == 6:
        return 'Вихідний'

    # Вибираємо розклад в залежності від дня тижня
    if current_time.weekday() == 2:  # 0 - понеділок, 1 - вівторок, 2 - середа, ...
        day_schedule = wednesday_schedule
    else:
        day_schedule = schedule

    for i, class_ in enumerate(day_schedule, start=1):
        start_time = [int(t) for t in class_['start'].split(':')]
        start_minutes = start_time[0] * 60 + start_time[1]

        finish_time = [int(t) for t in class_['finish'].split(':')]
        finish_minutes = finish_time[0] * 60 + finish_time[1]

        if current_minutes < start_minutes:
            return 'Пара ' + str(i) + ' - Час до початку пари: ' + format_duration(start_minutes - current_minutes)
        elif current_minutes < finish_minutes:
            return 'Пара ' + str(i) + ' - Час до кінця пари: ' + format_duration(finish_minutes - current_minutes)

    return 'На данний момент пар немає (:'

# Ваш код ...


def format_duration(minutes):
    hours = minutes // 60
    minutes = minutes % 60
    return f'{hours:01d}:{minutes:02d}'


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id not in allowed_users:
        print("! У доступі відмовлену користувачу: ", message.from_user.id)
        return  # Якщо користувач не є в списку дозволених, не робимо нічого
    update_current_time = datetime.datetime.now()
    print("\nЗвернення || User ID:", message.from_user.id, " | Час -",update_current_time.strftime('%Y-%m-%d %H:%M:%S'),"\n")  # Виводимо id користувача
    msg = bot.send_message(message.chat.id, update())
    message_id = msg.message_id
    last_text = msg.text
    # Зберігаємо message_id в словнику
    messages_to_edit[message.chat.id] = message_id
    print("|| Message id: ",message_id)
    while True:
        update_current_time = datetime.datetime.now()  # Оновлюємо час
        #print(update_current_time.strftime('%S'))
        while update_current_time.strftime('%S') != "00":
            time.sleep(0.3)
            update_current_time = datetime.datetime.now()  # Оновлюємо час
        new_text = update()
        if new_text != last_text:
            # Замість редагування повідомлення за message_id, шукайте його в словнику
            bot.edit_message_text(chat_id=message.chat.id, message_id=messages_to_edit[message.chat.id], text=new_text)
            last_text = new_text
        time.sleep(20)


@bot.message_handler(commands=['status'])
def send_status(message):
    global last_update
    update_current_time = datetime.datetime.now()

    if message.from_user.id not in allowed_users:
        print("! У доступі відмовлену користувачу: ", message.from_user.id)
        return  # Якщо користувач не є в списку дозволених, не робимо нічого
    
    print("\nЗвернення || User ID:", message.from_user.id, " | Час -",update_current_time.strftime('%Y-%m-%d %H:%M:%S'),"\n")  # Виводимо id користувача
    uptime = time.time() - start_time
    hours, rem = divmod(uptime, 3600)
    minutes, seconds = divmod(rem, 60)
    last_update_output = "пустота" if last_update == None else str(last_update.strftime("%Y-%m-%d %H:%M:%S"))
    bot.send_message(message.chat.id, "_Статус бота:_ *активний* \n" + str(update_current_time.strftime("%Y-%m-%d %H:%M:%S")) + "\n\n_Останнє оновлення:_ \n" + last_update_output + "\n\n_Uptime:_ \n*{:0>2}:{:0>2}:{:05.2f}*".format(int(hours),int(minutes),seconds), parse_mode='Markdown')

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"|\n|!Виникла помилка: {e}\n|")
        time.sleep(15)
