import asyncio
from mysql.connector import Error
import aiomysql
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN, admin_id, hostname, hostuser, hostpassword, datab
from urllib.request import urlopen
import xml.etree.ElementTree as ET

loop = asyncio.get_event_loop()
bot = Bot(TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, loop=loop)
URLBANK = 'https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5'
URLCARD = 'https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=11'
i = 0


async def insert_select_delete_db(user_id, user_name, key):
    connection = None
    try:
        connection = await aiomysql.connect(
            host=hostname,
            user=hostuser,
            password=hostpassword,
            db=datab,
            loop=loop
        )
    except Error as e:
        print(f"Error while connecting to MySQL {e}")  # треба забрати
    cursor = await connection.cursor()
    if key == 'insert':
        await cursor.execute(
            f"INSERT INTO users (id, name) SELECT * FROM (SELECT {user_id}, '{user_name}') AS tmp WHERE NOT EXISTS ("
            f"SELECT id FROM users WHERE id = {user_id});")
    elif key == 'select':
        await cursor.execute("SELECT id FROM users;")
        all_users_id = await cursor.fetchall()
        await connection.commit()
        await cursor.close()
        connection.close()
        return all_users_id
    elif key == 'delete':
        await cursor.execute(f"DELETE FROM users WHERE id = {user_id};")
    await connection.commit()
    await cursor.close()
    connection.close()


@dp.message_handler(commands=['start', 'help'])
async def send_message(message: types.Message):
    #sti = open('sticker/BatmanComics_023.webp', 'rb')
    #await bot.send_sticker(message.chat.id, sti)
    await bot.send_message(admin_id, f"start -- {message.from_user.id} -- {message.from_user.first_name}")
    await bot.send_message(message.chat.id, f'Привіт {message.from_user.first_name}! \nЯ відправлятиму Тобі '
                                            f'повідомлення про курс валют від ПриватБанк.\nДля того щоб отримувати '
                                            f'сповіщення о 9:00, 12:00, 15:00 та 18:00 щодня про курс валют потрібно '
                                            f'зареєструватись в мене. \nІнструкції-команди:\nЗареєструватись - '
                                            f'/register\nВидалитись - /delete\nПобачити ще раз це меню - /start або '
                                            f'/help\nПри друку любого сполучення симолів буде відправлятись курс валют.')


@dp.message_handler(commands=['register'])
async def send_to_register(message: types.Message):
    key = 'insert'
    await bot.send_message(admin_id, f"{key} -- {message.from_user.id} -- {message.from_user.first_name}")
    await insert_select_delete_db(message.from_user.id, message.from_user.first_name, key)
    await bot.send_message(message.chat.id, f'{message.from_user.first_name} ви добавлені в систему для розсилки '
                                            f'курсу валют')


@dp.message_handler(commands=['delete'])
async def delete_fom_register(message: types.Message):
    key = 'delete'
    await bot.send_message(admin_id, f"{key} -- {message.from_user.id} -- {message.from_user.first_name}")
    await insert_select_delete_db(message.from_user.id, message.from_user.first_name, key)
    await bot.send_message(message.chat.id, f'{message.from_user.first_name} ви видалені із системи розсилки')


@dp.message_handler(commands=['start_program'])
async def timer(message: types.Message):
    global i
    time_to_call = 0
    m = datetime.now().timetuple()
    time_now = timedelta(hours=m[3] + 2, minutes=m[4], seconds=m[5])
    if i == 0:
        time_left = timedelta(hours=24) - time_now
        time_to_call = time_left + timedelta(hours=9)
        i = 1
    elif i == 1:
        time_to_call = timedelta(hours=3)
        i = 2
    elif i == 2:
        time_to_call = timedelta(hours=3)
        i = 3
    elif i == 3:
        time_to_call = timedelta(hours=3)
        i = 0
    await bot.send_message(admin_id, f"{i} -- {time_to_call}")
    all_users_id = insert_select_delete_db(user_id=None, user_name=None, key='select')
    for users in await all_users_id:
        await sender(await parser_xml(URLBANK), 'Банк:', int(users[0]))
        await sender(await parser_xml(URLCARD), 'Картка:', int(users[0]))
    await asyncio.sleep(time_to_call.total_seconds())
    await timer(message)


@dp.message_handler(content_types=['text'])
async def echo(message: types.Message):
    await bot.send_message(admin_id, f"text -- {message.from_user.id} -- {message.from_user.first_name}")
    await sender(await parser_xml(URLBANK), 'Банк:', message.chat.id)
    await sender(await parser_xml(URLCARD), 'Картка:', message.chat.id)


async def parser_xml(url):
    xml = urlopen(url)
    tree = ET.parse(xml)
    root = tree.getroot()
    return root


async def sender(root, text, users):
    print(users)
    await bot.send_message(users, f"{text}\n"
                                  f"{root[0][0].attrib['ccy']} : {root[0][0].attrib['buy']} - {root[0][0].attrib['sale']}\n"
                                  f"{root[1][0].attrib['ccy']} : {root[1][0].attrib['buy']} - {root[1][0].attrib['sale']}\n"
                                  f"{root[3][0].attrib['ccy']} : {root[3][0].attrib['buy']} - {root[3][0].attrib['sale']}")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
