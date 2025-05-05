import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, ApplicationBuilder
from ultralytics import YOLO
from deep_translator import GoogleTranslator

load_dotenv()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)


def run_inference(image_path, img_size=1024, conf_threshold=0.1):
    results = model.predict(image_path, imgsz=img_size, conf=conf_threshold)
    for result in results:
        idx = result.probs.top1
        predicted = result.names[idx]
        return predicted
    return None

## TODO Сделать меню для кнопок
start_markup = ReplyKeyboardMarkup(
    [
        [KeyboardButton("/start")],
        [KeyboardButton("/contacts")]
    ],
    resize_keyboard=True
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    text = (
        "👋 Привет! Я бот для распознавания блюд на фото.\n\n"
        "• Отправить изображение блюда, чтобы я смог распознать его.\n"
        "• Нажмите «/contacts», чтобы узнать, кто меня сделал."
    )
    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=start_markup
    )


async def contacts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    creators = (
        "👨‍💻 Авторы проекта:\n"
        "— Абзалов Эдуард Русланович\n"
        "— Власов Леонид Дмитриевич\n"
        "— Дмитриенко Константин\n"
        "— Ладыгин Никита Сергеевич"
    )
    await context.bot.send_message(chat_id=chat_id, text=creators)


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message.photo:
        await update.message.reply_text("❗ Это не изображение. Пожалуйста, отправьте фото блюда.")
        return

    photo = update.message.photo[-1]
    file = await photo.get_file()
    path = f"./downloads/{file.file_id}.jpg"
    os.makedirs(os.path.dirname(path), exist_ok=True)

    try:
        await file.download_to_drive(path)
    except Exception as e:
        logger.error(f"Ошибка при скачивании изображения: {e}")
        await update.message.reply_text("❗ Ошибка при скачивании изображения.")
        return

    result = run_inference(path)
    if result:
        if result == "none":
            await update.message.reply_text("❌ Ничего не найдено на изображении.")
        translated = GoogleTranslator(source='auto', target='ru').translate(result)
        translated = translated.capitalize()
        await update.message.reply_text(f"✅ Распознанное блюдо: *{translated}*", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Ничего не найдено на изображении.")

    try:
        os.remove(path)
    except Exception as e:
        logger.error(f"Ошибка при удалении файла: {e}")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Неизвестная команда. Воспользуйтесь клавиатурой ниже.",
        reply_markup=start_markup
    )


if __name__ == "__main__":
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    MODEL_PATH = os.getenv("MODEL_PATH")
    if not TOKEN:
        raise ValueError("Токен Telegram не найден.")
    if not MODEL_PATH:
        raise ValueError("Путь для запуска модели YOLO не найден.")

    logger.info("Запуск бота...")

    model = YOLO(MODEL_PATH)
    app = ApplicationBuilder().token(TOKEN).read_timeout(9999).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("contacts", contacts))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    try:
        app.run_polling()
        logger.info("Бот успешно запущен и работает.")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
