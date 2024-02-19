import telebot
from telebot import types
from PIL import Image
from io import BytesIO
import io
from moviepy.editor import *
import os
import re

bot = telebot.TeleBot('6943064156:AAGPblILUoJKauMxbhfAmqqzkPBMZRaBuPs')


# Обработчик команды /newpack
@bot.message_handler(commands=['newpack'])
def new_pack(message):
    # Запрашиваем имя стикерпака
    bot.send_message(message.chat.id, 'Введите имя стикерпака')
    bot.register_next_step_handler(message, get_pack_name)


# Обработчик получения имени стикерпака
def get_pack_name(message):
    pack_name = message.text
    # Запрашиваем эмодзи для стикерпака
    bot.send_message(message.chat.id, 'Введите эмодзи для стикерпака (от 3 до 5)')
    bot.register_next_step_handler(message, get_pack_emojis, pack_name=pack_name)


# Обработчик получения эмодзи для стикерпака
def get_pack_emojis(message, pack_name):
    # Используем регулярное выражение для извлечения эмодзи из сообщения
    emojis = re.findall(r'(\U00010000-\U0010FFFF)', message.text)

    if len(emojis) >= 3 and len(emojis) <= 5:
        # Создаем новый стикерпак
        pack = bot.create_new_sticker_set(
            user_id=message.from_user.id,
            name=pack_name,
            title=pack_name,
            emojis=emojis
        )

        # Отправляем инструкцию
        bot.send_message(message.chat.id, 'Отправьте фото для добавления в стикерпак')

        # Устанавливаем состояние для ожидания фото
        bot.register_next_step_handler(message, add_sticker, pack=pack)
    else:
        # Если количество эмодзи неверное, запрашиваем повторно
        bot.send_message(message.chat.id, 'Количество эмодзи должно быть от 3 до 5. Пожалуйста, введите эмодзи заново.')
        bot.register_next_step_handler(message, get_pack_emojis, pack_name=pack_name)


# Обработчик получения фото
def add_sticker(message, pack):
    if message.content_type == 'photo':
        # Получаем данные о фото
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        # Скачиваем фото
        downloaded_photo = bot.download_file(file_info.file_path)
        # Открываем фото с помощью PIL
        image = Image.open(io.BytesIO(downloaded_photo))
        # Изменяем размер фото до 512x512
        resized_image = image.resize((512, 512))
        # Создаем буфер для сохранения изображения
        output = io.BytesIO()
        # Сохраняем измененное фото в буфере
        resized_image.save(output, format='PNG')
        # Переводим буфер в байты
        sticker_bytes = output.getvalue()
        # Добавляем стикер в стикерпак
        bot.add_sticker_to_set(
            user_id=message.from_user.id,
            name=pack.name,
            png_sticker=sticker_bytes,
            emojis=pack.emojis
        )
        # Отправляем сообщение о успешном добавлении стикера
        bot.send_message(message.chat.id, 'Стикер успешно добавлен в стикерпак!')
    else:
        # Если тип контента не является фото, запрашиваем повторно
        bot.send_message(message.chat.id, 'Пожалуйста, отправьте фото для добавления в стикерпак')
        bot.register_next_step_handler(message, add_sticker, pack=pack)


@bot.message_handler(commands=['start'])
def start(message):
    butn = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('/newpack')
    butn.row(btn1)
    bot.send_message(message.chat.id, 'Привет', reply_markup=butn)
    # bot.register_next_step_handler(message, on_click)


# Функция, которая обрабатывает нажатие кнопок
# @bot.message_handler(func=lambda message: True)
# def handle_buttons(message):
#     if message.text == 'Создать стикер пак':
#         bot.send_message(message.chat.id, 'Вы нажали кнопку 1!')
#     elif message.text == 'Преобразовать фото':
#         bot.send_message(message.chat.id, 'Вы нажали кнопку 2!')
#     elif message.text == 'Преобразовать видео':
#         bot.send_message(message.chat.id, 'Вы нажали кнопку 3!')

# Обработчик получения фотографий
#     @bot.message_handler(content_types=['photo'])
#     def process_photo(message):
#         # Получаем данные о фотографии
#         photo = message.photo[-1]  # Берем только последнюю отправленную фотографию
#         photo_data = bot.get_file(photo.file_id)  # Получаем ссылку на файл фотографии
#         # Скачиваем фотографию
#         downloaded_photo = bot.download_file(photo_data.file_path)
#         # Открываем фотографию с помощью библиотеки PIL
#         image = Image.open(BytesIO(downloaded_photo))
#         # Преобразуем фотографию в формат PNG с прозрачным слоем
#         image = image.convert("RGBA")
#         # Создаем квадратное изображение размером 512x512
#         if image.width > image.height:
#             square_size = image.width
#             padding = (square_size - image.height) // 2
#         else:
#             square_size = image.height
#             padding = (square_size - image.width) // 2
#         square_image = Image.new("RGBA", (square_size, square_size), (0, 0, 0, 0))
#         square_image.paste(image, (padding, padding))
#         # Изменяем размер изображения до 512x512
#         square_image = square_image.resize((512, 512))
#         # Сохраняем изображение в формате WebP
#         square_image.save("processed_image.webp", format="WebP")
#         # Отправляем обработанное изображение пользователю
#         with open("processed_image.webp", "rb") as image_file:
#             bot.send_photo(message.chat.id, image_file)
#
#     @bot.message_handler(commands=['gif'])
#     def convert_to_gif(message):
#         # Получаем информацию о видео
#         video = message.reply_to_message.video
#         file_info = bot.get_file(video.file_id)
#         downloaded_file = bot.download_file(file_info.file_path)
#         video_filename = f'{message.chat.id}_{video.file_unique_id}.mp4'
#         gif_filename = f'{message.chat.id}_{video.file_unique_id}.gif'
#
#         # Сохраняем видео на диск
#         with open(video_filename, 'wb') as file:
#             file.write(downloaded_file)
#
#         # Конвертируем видео в GIF
#         video_clip = VideoFileClip(video_filename)
#         gif_clip = video_clip.subclip(0, 3).resize((512, 512)).set_duration(3)
#         gif_clip.write_gif(gif_filename, fps=10)
#
#         # Отправляем GIF пользователю
#         with open(gif_filename, 'rb') as file:
#             bot.send_document(message.chat.id, file)
#
#         # Удаляем временные файлы
#         os.remove(video_filename)
#         os.remove(gif_filename)

# @bot.message_handler(content_types=['photo'])
# def convert_to_png(message):
#     try:
#         photo = bot.get_file(message.photo[-1].file_id)
#         file_path = bot.download_file(photo)
#         # Convert jpg to png using PIL
#         original_img = Image.open(file_path)
#         png_img = original_img.convert("RGBA")
#         png_img.save("path/to/your/png/file.png", format="PNG")
#         # Send png to chat
#         bot.send_document(message.chat.id, open("path/to/your/png/file.png", "rb"))
#     except requests.exceptions.ConnectionError as e:
#         print(f"ConnectionError: {e}")
#         # Retry with exponential backoff
#         delay = 2 ** random.randint(1, 5)
#         print(f"Retrying in {delay} seconds...")
#         time.sleep(delay)
#         convert_to_png(message)
#     except Exception as e:
#         print(f"Error: {e}")

bot.polling()  # Запускаем бота

