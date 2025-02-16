import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, ApplicationBuilder
from ultralytics import YOLO

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("telegram").setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

load_dotenv()

class_translation = {
    'drink': 'Напиток',
    'dessert': 'Десерт',
    'meal': 'Блюдо'
}


# Функция для инференса
def run_inference(model_path, image_path, img_size=1024, conf_threshold=0.1):
    model = YOLO(model_path)
    results = model.predict(image_path, imgsz=img_size, conf=conf_threshold)

    # Извлекаем класс с наибольшей вероятностью
    for result in results:
        id = result.probs.top1
        predicted_class = result.names[id]

        # Переводим класс, если перевод существует
        translated_class = class_translation.get(predicted_class, predicted_class)
        return translated_class


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Пользователь {update.effective_user.id} вызвал команду /start")
    await update.message.reply_text("Привет! Отправь изображение, чтобы я выполнил определил блюдо.")


# Обработка изображений
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message.photo:
        await update.message.reply_text("Это не изображение. Пожалуйста, отправьте изображение.")
        return

    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_path = f"./downloads/{file.file_id}.jpg"

    os.makedirs(os.path.dirname(image_path), exist_ok=True)

    try:
        # Скачиваем изображение на диск
        await file.download_to_drive(image_path)
    except Exception as e:
        logger.error(f"Ошибка при скачивании файла: {e}")
        await update.message.reply_text("Произошла ошибка при скачивании изображения.")
        return

    # Выполняем инференс
    model_path = "runs/train/yolo_classification6/weights/best.pt"
    predicted_class = run_inference(model_path, image_path)

    if predicted_class:
        response = f"Предсказанный класс: {predicted_class}"
    else:
        response = "Ничего не найдено на изображении."

    try:
        # Отправка ответа пользователю
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")

    # Удаляем изображение после обработки
    try:
        os.remove(image_path)
        logger.info(f"Файл {image_path} успешно удалён.")
    except Exception as e:
        logger.error(f"Ошибка при удалении файла {image_path}: {e}")


# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message.photo:
        await update.message.reply_text("Это не изображение. Пожалуйста, отправьте изображение.")
        return


if __name__ == "__main__":
    # Получение токена
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        logger.critical("Токен Telegram не найден. Завершение работы.")
        raise ValueError("Токен Telegram не найден.")

    app = ApplicationBuilder().token(TOKEN).read_timeout(9999).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))

    logger.info("Бот запущен!")
    app.run_polling()