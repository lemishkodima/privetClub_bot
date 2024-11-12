import contextlib
import asyncio
from aiogram.types import CallbackQuery, ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, FSInputFile
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command
import logging
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import csv


BOT_TOKEN = '6180592335:AAFLKZ60x7efxzPgmo70DIqkB7HrifkXgrs' 
CHANNEL_ID =  -1001485074571
ADMIN_ID = 505658283

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class Form(StatesGroup):
    Broadcast = State()  # Состояние для рассылки

async def approve_request(chat_join: ChatJoinRequest, bot: Bot):
    start_msg = "Ваша заявка одобрена, для получения ссылки нажмите Start⬇️"
    start_button = KeyboardButton(text='Start')
    markup = ReplyKeyboardMarkup(keyboard=[[start_button]], resize_keyboard=True, one_time_keyboard=True)
    await bot.send_message(chat_id=chat_join.from_user.id, text=start_msg, reply_markup=markup)

@dp.message(F.text.lower() == "start")
async def send_channel_link(message: types.Message):
        msg = "Ваша заявка одобрена!\n\nВступить в канал: https://t.me/+f4ClsdHxOVNlNGUy"
        button = InlineKeyboardButton(text='ВСТУПИТЬ', url='https://t.me/+f4ClsdHxOVNlNGUy')
        markup = InlineKeyboardMarkup(inline_keyboard=[[button]])
        # msg2 = "В качестве подарка дарим Вам подписку на наш закрытый канал с сигналами и разборами акций РФ в 🇷🇺 - https://t.me/+__lAiNBlmP02ZGUy"

        user_data = [message.from_user.id, message.from_user.username, message.from_user.first_name]
        append_data_to_sheet(user_data, "1nCSQBIwryKNs13N_9MH8C6OMMjHBCXiMhRs5Q6TkxtA", "A:C")

        await message.answer(text=msg, disable_web_page_preview=True)
        # await message.answer(text=msg2, disable_web_page_preview=True)
   
# async def approve_request (chat_join: ChatJoinRequest, bot: Bot):
#    msg= f"Ваша заявка одобрена!\n\nВступить в канал: https://t.me/+f4ClsdHxOVNlNGUy"
#    button = InlineKeyboardButton(text='ВСТУПИТЬ', url='https://t.me/+f4ClsdHxOVNlNGUy', disable_web_page_preview=True)   
#    markup = InlineKeyboardMarkup(inline_keyboard=[[button]])

#    user_data = [chat_join.from_user.id, chat_join.from_user.username, chat_join.from_user.first_name]
#    append_data_to_sheet(user_data, "1nCSQBIwryKNs13N_9MH8C6OMMjHBCXiMhRs5Q6TkxtA", "A:C")
#    await bot.send_message(chat_id=chat_join.from_user.id, text=msg, reply_markup=markup, disable_web_page_preview=True)


def append_data_to_sheet(user_data, spreadsheet_id, range_name):
    """Добавляет данные пользователя в Google таблицу."""
    creds = Credentials.from_service_account_file("maxim.json")
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    request = sheet.values().append(spreadsheetId=spreadsheet_id, 
                                    range=range_name, 
                                    valueInputOption="USER_ENTERED", 
                                    body={"values": [user_data]})
    response = request.execute()
    return response
 

@dp.message(Form.Broadcast)
async def process_broadcast(message: types.Message, state: FSMContext):
    # Зчитування тексту розсилки
    broadcast_text = message.text
    await state.clear()  # Вихід зі стану розсилки

    # Зчитування всіх користувачів з Google Sheets
    creds = Credentials.from_service_account_file("maxim.json")
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId="1M0WEMEVhVn-cdu47fSTnwMAHeTnK5TGaSKKTP1rB2Es", range="steelrain_bot!A:C").execute()
    users = result.get('values', [])

    results = []

    for index, user in enumerate(users, start=2):
        try:
            user_id = user[0]
            await bot.send_message(chat_id=user_id, text=broadcast_text, disable_web_page_preview=True)
            results.append({'Index': index, 'User ID': user_id, 'Status': 'True'})
        except Exception as e:
            results.append({'Index': index, 'User ID': user_id, 'Status': 'False'})
            logging.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

    # Збереження результатів у файл
    file_path = 'broadcast_results.csv'
    await save_results_to_csv(results, file_path)
    
    # Відправка файлу з результатами адміністратору
    document = FSInputFile(file_path)
    await message.answer_document(document, caption="Рассылка завершена. Результаты сохранены в broadcast_results.csv")

async def save_results_to_csv(results, file_path):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Index', 'User ID', 'Status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

async def start():
    logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - [%(levelname)s] - %(name)s -"
                           "(%(filename)s.%(funcName)s(%(lineno)d) - %(message)s"
                    )
    dp.chat_join_request.register (approve_request, F.chat.id ==CHANNEL_ID)

    try:
     await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as ex:
     logging.error( exc_info=True)
    finally:
     await bot.session.close()


if __name__ == '__main__':
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(start())
