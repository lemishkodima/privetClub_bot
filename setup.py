import contextlib
import asyncio 
from aiogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, Dispatcher, F
import logging
import contextlib
import asyncio
from aiogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, Dispatcher, F
import logging
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials


BOT_TOKEN = '6180592335:AAFLKZ60x7efxzPgmo70DIqkB7HrifkXgrs' 
CHANNEL_ID =  -1001485074571
ADMIN_ID = 505658283
async def approve_request (chat_join: ChatJoinRequest, bot: Bot):
   msg= f"Ваша заявка одобрена!\n\nВступить в канал: https://t.me/+TwT2yXl8sPs2NjQy"
   button = InlineKeyboardButton(text='ВСТУПИТЬ', url='https://t.me/+TwT2yXl8sPs2NjQy', disable_web_page_preview=True)   
   markup = InlineKeyboardMarkup(inline_keyboard=[[button]])

   user_data = [chat_join.from_user.id, chat_join.from_user.username, chat_join.from_user.first_name]
   append_data_to_sheet(user_data, "1nCSQBIwryKNs13N_9MH8C6OMMjHBCXiMhRs5Q6TkxtA", "A:C")
   await bot.send_message(chat_id=chat_join.from_user.id, text=msg, reply_markup=markup, disable_web_page_preview=True)


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
 

async def start():
    logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - [%(levelname)s] - %(name)s -"
                           "(%(filename)s.%(funcName)s(%(lineno)d) - %(message)s"
                    )
    bot: Bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher ()
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
