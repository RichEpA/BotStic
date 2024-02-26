import os
import telebot
from PIL import Image
from io import BytesIO

bot = telebot.TeleBot('6943064156:AAF31l0eeaUUXWWGInzafZvwBTwbQAJErOU')


@bot.message_handler(commands=['start'])
def start(message):
    # Create a custom keyboard markup with buttons for each command
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    new_pack_button = telebot.types.KeyboardButton('/newpack')
    publ_button = telebot.types.KeyboardButton('/publ')
    markup.row(new_pack_button, publ_button)
    # Send a message with the custom keyboard markup
    bot.send_message(message.chat.id, "Welcome to the Sticker Pack Creator Bot!", reply_markup=markup)

import os
import telebot
from PIL import Image
from io import BytesIO

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
                                      "Для завершения пака введите команду /close или /publ для опубликования стикерпака.")

# Обработчик команды /close или /publ
@bot.message_handler(commands=['close', 'publ'])
def handle_close_publ_command(message):
    # Если пользователь выбирает команду /close
    if message.text.startswith('/close'):
        # Отправляем сообщение с завершением процесса создания пака
        bot.send_message(message.chat.id, "Процесс создания стикерпака завершен.")
        # Удаляем состояние ожидания для данного пользователя
        bot.clear_step_handler(message)
    # Если пользователь выбирает команду /publ
    elif message.text.startswith('/publ'):
        # Получаем состояние пользователя
        state = bot.get_state(message.chat.id)
        if state is not None and 'pack_name' in state:
            pack_name = state['pack_name']
            # Создаем список для хранения ссылок на стикерпаки
            sticker_links = []
            # Публикуем стикерпак на сервере Telegram
            for sticker_pack_name, stickers in sticker_packs.items():
                if sticker_pack_name == pack_name:
                    # Создаем стикерпак
                    result = bot.create_new_sticker_set(
                        user_id=message.chat.id,
                        name=sticker_pack_name,
                        title=sticker_pack_name,
                        emojis=' '.join([sticker['emoji'] for sticker in stickers]),
                        png_sticker=open(stickers[0]['file_path'], 'rb')
                    )
                    # Получаем ссылку на стикерпак
                    sticker_link = f"https://telegram.me/addstickers/{result.name}"
                    sticker_links.append(sticker_link)
            # Отправляем пользователю ссылки на опубликованные стикерпаки
            bot.send_message(message.chat.id, "Ваши стикерпаки опубликованы и доступны по следующим ссылкам:")
            for link in sticker_links:
                bot.send_message(message.chat.id, link)
        else:
            # Если состояние пользователя отсутствует или в нем нет ключа pack_name, отправляем сообщение об ошибке
            bot.send_message(message.chat.id, "Для публикации стикерпака необходимо сначала создать его с помощью команды /newpack.")

# Запускаем бота
bot.polling()