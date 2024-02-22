import telebot
from telebot import types
from PIL import Image
from io import BytesIO
import io
from moviepy.editor import *
import os
import re

bot = telebot.TeleBot('6943064156:AAGPblILUoJKauMxbhfAmqqzkPBMZRaBuPs')


@bot.message_handler(commands=['start'])
def start(message):
    butn = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('/newpack')
    btn2 = types.KeyboardButton('/publ')
    butn.row(btn1, btn2)
    # bot.register_next_step_handler(message, on_click)

import os
import telebot
from PIL import Image
from io import BytesIO

# Создаем экземпляр бота с указанием токена, полученного от BotFather в Telegram
bot = telebot.TeleBot('YOUR_TELEGRAM_BOT_TOKEN')

# Словарь для хранения информации о созданных стикерпаках
sticker_packs = {}

# Обработчик команды /newpack
@bot.message_handler(commands=['newpack'])
def handle_newpack_command(message):
    # Отправляем сообщение с запросом имени для нового стикерпака
    bot.send_message(message.chat.id, "Введите имя для нового стикерпака:")
    # Устанавливаем состояние ожидания имени пака для данного пользователя
    bot.register_next_step_handler(message, ask_pack_name)

# Функция для запроса имени стикерпака и сохранения его
def ask_pack_name(message):
    pack_name = message.text
    # Инициализируем список для хранения эмодзи и фото стикеров в паке
    sticker_packs[pack_name] = []
    # Отправляем сообщение с запросом эмодзи и фото для первого стикера в паке
    bot.send_message(message.chat.id, "Отправьте эмодзи и фото для первого стикера в формате эмодзи, а затем фото.")
    # Устанавливаем состояние ожидания эмодзи для данного пользователя
    bot.register_next_step_handler(message, ask_sticker_info, pack_name)

# Функция для запроса эмодзи и фото для стикера
def ask_sticker_info(message, pack_name):
    emoji = message.text
    # Отправленное сообщение является эмодзи
    if emoji:
        # Устанавливаем состояние ожидания фото для данного пользователя
        bot.send_message(message.chat.id, "Теперь отправьте фото для этого стикера.")
        # Добавляем эмодзи в список стикерпака
        sticker_packs[pack_name].append({'emoji': emoji})
        # Устанавливаем состояние ожидания фото для данного пользователя
        bot.register_next_step_handler(message, save_sticker_photo, pack_name, len(sticker_packs[pack_name]) - 1)
    else:
        # Если не было отправлено эмодзи, сообщаем об ошибке
        bot.send_message(message.chat.id, "Вы не отправили эмодзи. Пожалуйста, отправьте эмодзи.")

# Функция для сохранения фото стикера и обработки следующего стикера
def save_sticker_photo(message, pack_name, sticker_index):
    # Получаем информацию о фотографии с самым большим разрешением
    file_info = bot.get_file(message.photo[-1].file_id)
    # Скачиваем фото
    downloaded_file = bot.download_file(file_info.file_path)
    # Открываем фото с помощью PIL
    image = Image.open(BytesIO(downloaded_file))
    # Ресайзим фото до 512x512
    image.thumbnail((512, 512))
    # Создаем белый квадратный фон размером 512x512
    square_image = Image.new('RGB', (512, 512), (255, 255, 255))
    # Вставляем ресайзнутое изображение по центру белого фона
    square_image.paste(image, ((512 - image.width) // 2, (512 - image.height) // 2))
    # Создаем временный файл для сохранения квадратного изображения
    temp_file_path = f'sticker_{pack_name}_{sticker_index}.webp'
    # Сохраняем квадратное изображение в формате WEBP
    square_image.save(temp_file_path, 'WEBP')
    # Добавляем фото стикера в список стикерпака
    sticker_packs[pack_name][sticker_index]['file_path'] = temp_file_path
    # Отправляем сообщение с запросом следующего стикера или команды для закрытия пака
    bot.send_message(message.chat.id, "Отправьте следующее эмодзи и фото для стикера в формате эмодзи, а затем фото. "
                                      "Для завершения пака введите команду /close.")

# Обработчик команды /close
@bot.message_handler(commands=['close'])
def handle_close_command(message):
    # Отправляем сообщение с завершением процесса создания пака
    bot.send_message(message.chat.id, "Процесс создания стикерпака завершен.")
    # Удаляем состояние ожидания для данного пользователя
    bot.clear_step_handler(message)

# Обработчик команды /publ
@bot.message_handler(commands=['publ'])
def handle_publish_command(message):
    # Проверяем, есть ли аргументы в команде
    if len(message.text.split(' ')) > 1:
        # Получаем имя пака, который нужно опубликовать
        pack_name = message.text.split(' ')[1]
        # Создаем список для хранения ссылок на стикерпаки
        sticker_links = []
        # Публикуем каждый стикерпак и сохраняем ссылки
        for sticker_pack_name, stickers in sticker_packs.items():
            if sticker_pack_name == pack_name:
                # Создаем стикеры в паке
                for sticker in stickers:
                    bot.add_sticker_to_set(message.chat.id, sticker_pack_name, open(sticker['file_path'], 'rb'), sticker['emoji'])
                # Получаем ссылку на стикерпак
                sticker_link = f"https://t.me/addstickers/{sticker_pack_name}"
                sticker_links.append(sticker_link)
        # Отправляем пользователю ссылки на опубликованные стикерпаки
        bot.send_message(message.chat.id, "Ваши стикерпаки опубликованы и доступны по следующим ссылкам:")
        for link in sticker_links:
            bot.send_message(message.chat.id, link)
    else:
        # Если отсутствуют аргументы в команде, сообщаем об ошибке
        bot.send_message(message.chat.id, "Пожалуйста, укажите имя пака для публикации.")

# Запускаем бота
bot.polling()