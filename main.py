import logging
import os
import csv
from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, ApplicationBuilder
from ultralytics import YOLO

load_dotenv()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

translation_path = os.getenv("TRANSLATION_CSV") or "translations.csv"
if not os.path.isfile(translation_path):
    raise FileNotFoundError(f"Файл переводов не найден: {translation_path}")
translations = {}
with open(translation_path, encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = row.get('English')
        val = row.get('Russian')
        if key and val:
            translations[key.strip()] = val.strip()

calories_path = os.getenv("CALORIES_CSV") or "calories.csv"
if not os.path.isfile(calories_path):
    raise FileNotFoundError(f"Файл калорий не найден: {calories_path}")
calories_data = {}
with open(calories_path, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row.get('name', '').strip()
        cal = row.get('calories, 100 gm', '').strip()
        if name and cal:
            calories_data[name] = cal

recipes_path = os.getenv("RECIPES_CSV") or "recipes.csv"
if not os.path.isfile(recipes_path):
    raise FileNotFoundError(f"Файл калорий не найден: {recipes_path}")
recipes_data = {}
with open(recipes_path, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row.get('name', '').strip()
        cal = row.get('recipes', '').strip()
        if name and cal:
            recipes_data[name] = cal

def run_inference(image_path: str, conf_threshold: float = 0.1):
    results = model.predict(image_path, conf=conf_threshold)
    for result in results:
        if result.probs is not None:
            probs_array = result.probs.data.cpu().numpy()
            idx = probs_array.argmax()
            label = result.names[idx]
            confidence = float(probs_array[idx])
            return label, confidence
    return None, 0.0


commands = [
    BotCommand("start", "🍔 Запустить бота"),
    BotCommand("creators", "📌 О создателях"),
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="🍔 *Привет, гурман! Я – FoodSherlock, твой личный детектив калорий!*\n\n🔍 Просто отправь фото блюда, и я:\n✅ Определю, что за еда перед тобой\n✅ Расскажу её калорийность\n\n*Хочешь узнать, сколько калорий в твоей тарелке? Просто сфоткай и жми \"Отправить\"!*\n\n📌 P.S. Нажми /creators, если хочешь познакомиться с создателями этого кулинарного волшебства ✨",
                                   parse_mode=ParseMode.MARKDOWN)


async def creators(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="🔍 *Кто стоит за FoodSherlock?*\n\nНаш кулинарный детектив создан талантливой командой:\n\n• *Эдуард Абзалов* – Мастер данных\n• *Леонид Власов* – Капитан команды & Дизайнер\n• *Константин Дмитриенко* – Аналитик\n• *Никита Ладыгин* – Волшебник бэкенда\n\n*Этот dream team соединил технологии и любовь к еде!* 🚀",
                                   parse_mode=ParseMode.MARKDOWN)


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message.photo:
        await update.message.reply_text("❗ Это не изображение. Пожалуйста, отправьте фото блюда.")
        return
    photo = update.message.photo[-1]
    file = await photo.get_file()
    path = f"./downloads/{file.file_id}.jpg"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    await file.download_to_drive(path)
    label, confidence = run_inference(path)
    if label:
        if label == "none":
            await update.message.reply_text("❌ Ничего не найдено на изображении.")
        else:
            russian = translations.get(label, label).capitalize()
            percent = round(confidence * 100, 2)
            cal = calories_data.get(label)
            recipe = recipes_data.get(label)
            text = f"✅ Распознанное блюдо: *{russian}* \n📝 Вероятность: *{percent}%*"
            if cal:
                text += f"\n🔥 Калорийность (100 г): *{cal}*"
            if recipe:
                text += f"\n📔 Ссылка на рецепт: *{recipe}*"
            os.remove(path)
            await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    else:
        os.remove(path)
        await update.message.reply_text("❌ Ничего не найдено на изображении.")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Неизвестная команда. Воспользуйтесь клавиатурой ниже.")


async def post_init(application: ApplicationBuilder) -> None:
    await application.bot.set_my_commands(commands)


if __name__ == "__main__":
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    MODEL_PATH = os.getenv("MODEL_PATH")
    if not TOKEN:
        raise ValueError("Токен Telegram не найден.")
    if not MODEL_PATH:
        raise ValueError("Путь для запуска модели YOLO не найден.")
    model = YOLO(MODEL_PATH)
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).read_timeout(9999).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("creators", creators))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))
    app.run_polling()
