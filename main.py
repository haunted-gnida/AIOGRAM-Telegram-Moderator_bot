import asyncio
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.enums.parse_mode import ParseMode

API_TOKEN = 'TOKEN' #Токен бота.
GROUP_ID = -1002415267780  # Айди чата (работает только на одну группу, ага ну. Айди чата начинается с -100. Я с этим все мозги выебал))
BAD_WORDS = ['работа', 'заработок', '18 лет', 'легальная', 'в лс']  # Бан ворды, за которые может забанить!

bot = Bot(token=API_TOKEN)
router = Router()
router.message.filter(F.chat.type != "private")
dp = Dispatcher()

blocked_users = {}

@dp.message(Command("unmute"))
async def send_help(message: types.Message, command: CommandObject, bot: Bot):
    reply_message = message.reply_to_message 
    if message.chat.id == GROUP_ID:
        if not reply_message or not await is_admin(message, bot):
            await message.reply("<b>❌  Произошла ошибка!</b>", parse_mode=ParseMode.HTML)

        elif reply_message and is_admin(message,bot):
            await bot.restrict_chat_member(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id, permissions=types.ChatPermissions(can_send_messages=True, can_send_other_messages=True))
            await message.answer(f"🎉 Все ограничения с пользователя <b>{message.reply_to_message.from_user.first_name}</b> были сняты!", parse_mode=ParseMode.HTML)
    
@dp.message(F.chat.type == "private")
async def private(message: types.Message):
    await message.reply("😔 <b>Бот работает только в группах</b>")


async def is_admin(message, bot):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    bot = await bot.get_chat_member(message.chat.id, bot.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR] or bot.status != ChatMemberStatus.ADMINISTRATOR:
        return False
    return True

@dp.message(F.text)
async def check_bad_words(message: Message):
    if message.chat.id == GROUP_ID:
        for bad_word in BAD_WORDS: #поиск бан ворда
            if bad_word in message.text.lower():
                reply_message = message.reply_to_message
                await message.reply(f"Отправка сообщений была ограничена для пользователя <b>[{message.from_user.first_name}]</b>, из-за подозрения в рекламе. \nЕсли вас замутили по ошибке обратитесь в администрацию!", parse_mode=ParseMode.HTML)
                await bot.restrict_chat_member(chat_id=message.chat.id, user_id=message.from_user.id, permissions=types.ChatPermissions(can_send_messages=False)) #мут пользователя
                await asyncio.sleep(3) #удалить сообщение
                await message.delete()
                return

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())