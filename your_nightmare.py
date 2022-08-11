from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.dispatcher.filters import IsReplyFilter, IDFilter
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from random import choice
import sqlite3
import asyncio
import json
import requests
import logging
#import nest_asyncio
#nest_asyncio.apply()


V = 1
VK_ID = 215268409
TOKEN = "a469a4784e9eb78bd15479c964fba70a2220a377309763864a"
ADMIN = 5161665132
#ADMIN = 235519518

logging.basicConfig(level=logging.INFO)
bot = Bot(token='5379912413:AAHU1vDeTtZMBMU4-DUoK2elDDGR9_tilCs', parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

purch = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton('Купить', callback_data='buy'))

tariffs = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton('Тестовое видео', callback_data='simple'), InlineKeyboardButton('Премиум видео', callback_data='premium'))

buy = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton('Оплатить', url='https://vk.com/club215268409?w=app6887721_-215268409'), InlineKeyboardButton('Проверить', callback_data='check'), InlineKeyboardButton('Отмена', callback_data='cancel'))

class keksik:
    def __init__(self, group, token, v, headers = {'Content-type': 'application/json'}):
        self.group = group
        self.token = token
        self.v = v
        self.headers = headers
    def req(self, method, params = {}):
        r = requests.post("https://api.keksik.io/"+method, json=params, headers=self.headers)
        out = json.loads(r.text)
        return out
    def history(self, len = 20):
        r = requests.post("https://api.keksik.io/donates/get", json={'group': self.group, 'token': self.token, 'v': self.v}, headers=self.headers)
        out = json.loads(r.text)
        print(out)
        return out
    def find(self, msg, price):
        lst = self.history().get('list')
        print(lst)
        finded = False
        for i in lst:
            if i.get('msg') == msg and i.get('amount') == str(price):
                finded = True
                break
        return finded

keks = keksik(VK_ID, TOKEN, V)
#print(keks.find('g', 10))

def get_type(callback_query):
    entities = callback_query.message.entities or callback_query.message.caption_entities
    if not entities or entities[-1].type != "hashtag":
        return None, "No hashtags found"
    hashtag = entities[-1].get_text(callback_query.message.text or callback_query.message.caption)
    return hashtag[1:], None

def db():
    con = sqlite3.connect('ref.db')
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS db (user INTEGER, simple INTEGER DEFAULT 1, premium INTEGER DEFAULT 1, msg TEXT DEFAULT "No", msg_premium TEXT DEFAULT "No")')
    cur.execute('CREATE TABLE IF NOT EXISTS links (link TEXT, tariff TEXT)')
    con.commit()
    con.close()

def generate():
    digits = '0123456789'
    uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    lowercase = 'abcdefghijklmnopqrstuvwxyz' 
    #punctuation = '!#$%&*+-=?@^_' 
    ally = digits + uppercase + lowercase
    chars = ''
    for i in range(20):
        chars += choice(ally)
    return chars

async def wait(*args, **kwargs):
    call=args[0]
    await bot.send_message(call.from_user.id, "Не спамьте пожалуйста :(")


@dp.callback_query_handler(Text(equals='simple'))
async def simple(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    #await bot.answer_callback_query(call.id)
    con = sqlite3.connect('ref.db')
    cur = con.cursor()
    type = 'simple'
    tries =  cur.execute('SELECT simple FROM db WHERE user = ?', (call.from_user.id,)).fetchone()
    links = cur.execute('SELECT link FROM links WHERE tariff = ?', (type,)).fetchall()
    print(tries, links, type)
    if tries[0] > len(links):
        await bot.send_message(call.from_user.id, "Вы купили уже все ссылки из этого тарифа, совсем скоро мы добавим новые!")
        return
    available = len(links) - tries[0] +1
    data = cur.execute('SELECT simple FROM db WHERE user = ?', (call.from_user.id,)).fetchone()
    print(data)
    price = 10*data[0]
    msg = generate()
    cur.execute('UPDATE db SET msg = ? WHERE user = ?', (msg, call.from_user.id,))
    con.commit()
    con.close()
    await bot.send_message(call.from_user.id, f"⭐️Нажми на кнопку \"Оплатить\" и оплати {price} рублей через мини приложение ВК с таким комментарием: <code>{msg}</code>\n\n⚡️Тебе нужно оплатить ровно столько сколько сказано, не меньше и не больше! Если ты запустил другую оплату, то эта оплата считается устаревшей и ссылку ты не получишь!\n\n✨Осталось видео: {available}\n🕛Длительность до 1 минуты\n\n#simple", reply_markup=buy)

@dp.callback_query_handler(Text(equals='premium'))
async def premium(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    #await bot.answer_callback_query(call.id)
    con = sqlite3.connect('ref.db')
    cur = con.cursor()
    type = 'premium'
    tries =  cur.execute('SELECT premium FROM db WHERE user = ?', (call.from_user.id,)).fetchone()
    links = cur.execute('SELECT link FROM links WHERE tariff = ?', (type,)).fetchall()
    if tries[0] > len(links):
        await bot.send_message(call.from_user.id, "Вы купили уже все ссылки из этого тарифа, совсем скоро мы добавим новые!")
        return
    available = len(links) - tries[0] + 1
    data = cur.execute('SELECT premium FROM db WHERE user = ?', (call.from_user.id,)).fetchone()
    print(data)
    price = 50*data[0]
    msg = generate()
    cur.execute('UPDATE db SET msg_premium = ? WHERE user = ?', (msg, call.from_user.id,))
    con.commit()
    con.close()
    
    await bot.send_message(call.from_user.id, f"⭐️Нажми на кнопку \"Оплатить\" и оплати {price} рублей через мини приложение ВК с таким комментарием: <code>{msg}</code>\n\n⚡️Тебе нужно оплатить ровно столько сколько сказано, не меньше и не больше! Если ты запустил другую оплату, то эта оплата считается устаревшей и ссылку ты не получишь!\n\n✨Осталось видео: {available}\n🕛Длительность до 5 часов\n\n#premium", reply_markup=buy)

@dp.message_handler(IDFilter(chat_id=ADMIN), commands="add")
async def add(message: types.Message):
    try:
        message.text.split(' ')[2]
    except IndexError:
        await message.reply("Передавай аргументы: /add ССЫЛКА ТАРИФ")
        return
    link = message.text.split(' ')[1]
    tariff = message.text.split(' ')[2]
    tariffs = ['simple', 'premium']
    if tariff not in tariffs:
        await message.reply("Неверный тариф, указывай simple или premium")
        return
    con = sqlite3.connect('ref.db')
    cur = con.cursor()
    cur.execute('INSERT INTO links VALUES (?, ?)', (link, tariff))
    con.commit()
    con.close()
    await message.reply("Успешно добавлено!")

@dp.message_handler(IDFilter(chat_id=ADMIN), commands="del")
async def delete(message: types.Message):
    try:
        message.text.split(' ')[1]
    except IndexError:
        await message.reply("Передавай аргументы: /del ССЫЛКА")
        return
    link = message.text.split(' ')[1]
    con = sqlite3.connect('ref.db')
    cur = con.cursor()
    data = cur.execute('SELECT link FROM links').fetchall()
    print(data)
    there = False
    for i in data:
        if i[0] == link:
            there = True
    if not there:
        await message.reply("Нету такой ссылки")
        return
    cur.execute('DELETE FROM links WHERE link=?', (link,))
    con.commit()
    con.close()
    await message.reply('Успешно удадено!')

@dp.message_handler(IDFilter(chat_id=ADMIN), commands="show")
async def show(message: types.Message):
    con = sqlite3.connect('ref.db')
    cur = con.cursor()
    data = cur.execute('SELECT link, tariff FROM links').fetchall()
    text = 'Все ссылки:\n\n'
    print(data)
    for index, item in enumerate(data, 1):
        text += f'{index}. {item[0]} - {item[1]}\n'
    await message.reply(text)

@dp.message_handler(commands='start')
async def start(message: types.Message, state: FSMContext):
    async with state.proxy():
        data['clicked'] = 0
    con = sqlite3.connect('ref.db')
    cur = con.cursor()
    data = cur.execute('SELECT user FROM db WHERE user = ?', (message.from_user.id,)).fetchall()
    if not data:
        cur.execute('INSERT INTO db VALUES (?, ?, ?, ?, ?)', (message.from_user.id, 1, 1, "No", "No",))
        con.commit()
    con.close()
    pic = open('start.jpg', 'rb')
    #pic2 = open('menu.jpg', 'rb')
    await bot.send_photo(message.from_user.id, caption='Привет зайчик💋\n\nХочешь поглазеть на меня? 🙈\nТебе нужно просто купить тестовое видео (от 10р)🔥 или премиум (от 50р)👑', photo=pic, reply_markup=purch)
    #await bot.send_photo(message.from_user.id, caption='Выбери какое видео хочешь купить?', photo=pic2, reply_markup=tariffs)
    pic.close()
    #pic2.close()

@dp.callback_query_handler(Text(equals='buy'))
async def menu(call: types.CallbackQuery, state: FSMContext):
    #await bot.answer_callback_query(call.id)
    await bot.delete_message(call.from_user.id, call.message.message_id)
    pic = open('menu.jpg', 'rb')
    await bot.send_photo(call.from_user.id, caption='Выбери какое видео хочешь купить?', photo=pic, reply_markup=tariffs)
    pic.close()

@dp.callback_query_handler(Text(equals='cancel'))
async def cancel(call: types.CallbackQuery, state: FSMContext):
    #await bot.delete_message(call.from_user.id, call.message.message_id)
    #await bot.answer_callback_query(call.id)
    con = sqlite3.connect('ref.db')
    cur = con.cursor()
    type = get_type(call)[0]
    print(type)
    if type == 'premium':
        cur.execute('UPDATE db SET msg_premium = ? WHERE user = ?', ("No", call.from_user.id,))
        con.commit()
    elif type == 'simple':
        cur.execute('UPDATE db SET msg = ? WHERE user = ?', ("No", call.from_user.id,))
        con.commit()
    con.close()
    await menu(call, state)
    #await bot.send_message(call.from_user.id, "Отменено")


@dp.callback_query_handler(Text(equals='check'))
async def check(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['clicked'] += 1
        if data['clicked'] >2:
            data['clicked'] = 0
            await bot.send_message(call.from_user.id, "Антиспам: повторите попытку через 5 минут, я сам сообщу")
            await asyncio.sleep(300)
            await bot.send_message(call.from_user.id, "5 минут прошло, можете проверять оплату")
            return
    #await bot.delete_message(call.from_user.id, call.message.message_id)
    #await bot.answer_callback_query(call.id)
    con = sqlite3.connect('ref.db')
    cur = con.cursor()
    type = get_type(call)[0]
    msg = ''
    price = 0
    tries = 0
    if type == 'premium':
        data = cur.execute('SELECT premium, msg_premium FROM db WHERE user = ?', (call.from_user.id,)).fetchone()
        print(data)
        msg = data[1]
        price = 50*data[0]
        tries = data[0]
    elif type == 'simple':
        data = cur.execute('SELECT simple, msg FROM db WHERE user = ?', (call.from_user.id,)).fetchone()
        print(data)
        msg = data[1]
        price = 10*data[0]
        tries = data[0]
    con.commit()
    con.close()
    print(type, msg, price, tries)
    if msg == "No":
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await bot.send_message(call.from_user.id, "Эта оплата устарела или была удалена, причиной может стать то, что ты запустил другую оплату")
        return
    purchuased = keks.find(msg, price)
    if not purchuased:
        await bot.delete_message(call.from_user.id, call.message.message_id)
        if "😔Не нашел вашей оплаты!" not in call.message.text:
            await bot.send_message(call.from_user.id, "😔Не нашел вашей оплаты!\n\n"+call.message.text, reply_markup=buy)
        else:
            await bot.send_message(call.from_user.id, call.message.text, reply_markup=buy)
        return
    else:
        con = sqlite3.connect('ref.db')
        cur = con.cursor()
        data = cur.execute('SELECT link FROM links WHERE tariff = ?', (type,)).fetchall()
        print(data)
        try:
            #await bot.delete_message(call.from_user.id, call.message.message_id)
            await bot.send_message(call.from_user.id, "❤️Держи свою ссылочку — "+data[tries-1][0])
            if type == 'premium':
                cur.execute('UPDATE db SET premium = ?, msg_premium = "No" WHERE user = ?', (tries+1, call.from_user.id,))
            elif type == 'simple':
                cur.execute('UPDATE db SET simple = ?, msg = "No" WHERE user = ?', (tries+1, call.from_user.id,))
        except IndexError:
            #await bot.delete_message(call.from_user.id, call.message.message_id)
            await bot.send_message(call.from_user.id, "Ты купил все ссылки :/")
        con.commit()
        con.close()
        await menu(call, state)

if __name__ == "__main__":
    db()
    executor.start_polling(dp, skip_updates=True)