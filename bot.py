# bot.py
import asyncio
import json
import logging
import os
import time
from pathlib import Path

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Токен бота и ID группы для заказов
API_TOKEN = "7957824215:AAFXeeA8H7ElTOEAW5NGilydtwQkPFcMBu8"
GROUP_ID = -1003062619878  # ID группы продавца
# Список ID администраторов (можно добавить несколько)
ADMIN_IDS = [5186803258, 467876266]  # !!! ВАЖНО: Добавьте ID администраторов (узнать можно у @userinfobot)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=storage)

# Путь к файлу с товарами
PRODUCTS_FILE = Path(__file__).parent / "products.json"
PROJECT_DIR = Path(__file__).parent.absolute()  # Полный путь к проекту
IMAGES_DIR = PROJECT_DIR / "images" / "products"  # Папка для фото товаров

# Создаем папку для изображений если её нет
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Функции для работы с файлом товаров
def load_products_from_file():
    """Загрузка товаров из JSON файла"""
    try:
        if PRODUCTS_FILE.exists():
            with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        logging.error(f"Ошибка загрузки товаров: {e}")
        return []

def save_products_to_file(products):
    """Сохранение товаров в JSON файл"""
    try:
        with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        # Автоматический пуш на GitHub
        try:
            import subprocess
            
            # Используем полный путь к проекту
            project_path = str(PROJECT_DIR)
            
            # Добавляем products.json и все изображения
            result = subprocess.run(['git', 'add', 'products.json', 'images/'], 
                          cwd=project_path, 
                          capture_output=True, text=True)
            
            result = subprocess.run(['git', 'commit', '-m', 'Автообновление товаров и изображений'], 
                          cwd=project_path,
                          capture_output=True, text=True)
            
            result = subprocess.run(['git', 'push'], 
                          cwd=project_path,
                          capture_output=True, text=True)
            
            if result.returncode == 0:
                logging.info("✅ Товары автоматически загружены на GitHub! Появятся на сайте через 2-3 минуты.")
            else:
                logging.warning(f"Ошибка git push: {result.stderr}")
        except Exception as e:
            logging.warning(f"Не удалось автоматически загрузить на GitHub: {e}")
        
        return True
    except Exception as e:
        logging.error(f"Ошибка сохранения товаров: {e}")
        return False

# Загружаем товары при запуске
products = load_products_from_file()

# Состояния для добавления товара
class AddProduct(StatesGroup):
    product_id = State()
    name = State()
    price = State()
    description = State()
    image = State()

# Состояния для редактирования товара
class EditProduct(StatesGroup):
    select_product = State()
    edit_field = State()
    new_value = State()

# Главное меню для обычных пользователей
def user_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text="👜 Открыть магазин",
                web_app=WebAppInfo(url="https://fine322223.github.io/bogato/")
            )],
            [KeyboardButton(text="📞 Техподдержка")]
        ],
        resize_keyboard=True
    )
    return keyboard

# Меню администратора с дополнительными кнопками управления
def admin_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить товар", callback_data="add_product")],
        [InlineKeyboardButton(text="✏️ Редактировать товар", callback_data="edit_product")],
        [InlineKeyboardButton(text="❌ Удалить товар", callback_data="delete_product")],
        [InlineKeyboardButton(text="📋 Список товаров", callback_data="list_products")],
        [InlineKeyboardButton(
            text="📞 Техподдержка",
            url="https://t.me/fine911"
        )]
    ])
    return keyboard

def admin_keyboard():
    """Обычная клавиатура для админа с WebApp"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text="👜 Открыть магазин",
                web_app=WebAppInfo(url="https://fine322223.github.io/bogato/")
            )],
            [KeyboardButton(text="⚙️ Управление")]
        ],
        resize_keyboard=True
    )
    return keyboard


# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    
    # Проверяем, является ли пользователь администратором
    if user_id in ADMIN_IDS:
        await message.answer(
            "👋 Привет, Администратор!\n\n"
            "Добро пожаловать в панель управления магазином Bogato Boutique.\n"
            "Используйте кнопки ниже для управления товарами.",
            reply_markup=admin_keyboard()
        )
    else:
        await message.answer(
            "👋 Здравствуйте!\n\n"
            "Добро пожаловать в Bogato Boutique - магазин премиальных товаров.",
            reply_markup=user_menu()
        )

# Обработчик кнопки "Управление" для админа
@dp.message(F.text == "⚙️ Управление")
async def show_admin_menu(message: types.Message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        return
    
    await message.answer(
        "⚙️ Панель управления:",
        reply_markup=admin_menu()
    )

# Обработчик кнопки "Техподдержка" для обычных пользователей
@dp.message(F.text == "📞 Техподдержка")
async def show_support(message: types.Message):
    support_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💬 Написать в поддержку",
            url="https://t.me/fine911"
        )]
    ])
    
    await message.answer(
        "📞 <b>Техподдержка</b>\n\n"
        "По всем вопросам обращайтесь к нашему менеджеру.\n"
        "Мы ответим вам в ближайшее время!",
        parse_mode="HTML",
        reply_markup=support_keyboard
    )


# Обработка заказов из WebApp
@dp.message(F.content_type == types.ContentType.WEB_APP_DATA)
async def handle_webapp_data(message: types.Message):
    import time
    import base64
    import urllib.parse
    
    start_time = time.time()
    logging.info(f"🔔 Получены данные из WebApp от пользователя {message.from_user.id}")
    try:
        # Парсим данные из веб-приложения
        raw_data = message.web_app_data.data
        
        # Пробуем декодировать base64 (для iOS)
        try:
            decoded = base64.b64decode(raw_data).decode('utf-8')
            decoded = urllib.parse.unquote(decoded)
            data = json.loads(decoded)
            logging.info(f"📦 Данные заказа (base64): {data}")
        except:
            # Если не base64, то обычный JSON
            data = json.loads(raw_data)
            logging.info(f"📦 Данные заказа (JSON): {data}")
        
        parse_time = time.time()
        logging.info(f"⏱ Парсинг занял: {(parse_time - start_time)*1000:.0f}ms")
        
        name = data.get("name")
        phone = data.get("phone")
        address = data.get("address")
        # Автоматически получаем username из Telegram
        telegram = f"@{message.from_user.username}" if message.from_user.username else data.get("telegram", "Не указан")
        cart = data.get("cart", [])

        # Формируем текст заказа
        order_text = (
            f"📦 <b>Новый заказ</b>\n\n"
            f"👤 <b>Имя:</b> {name}\n"
            f"📞 <b>Телефон:</b> {phone}\n"
            f"📍 <b>Адрес:</b> {address}\n"
            f"💬 <b>Telegram:</b> {telegram}\n\n"
            f"🛒 <b>Товары:</b>\n"
        )
        
        total = 0
        for item in cart:
            order_text += f"• {item['title']} - {item['price']} ₽\n"
            total += item['price']
        
        order_text += f"\n💰 <b>Итого:</b> {total} ₽"
        format_time = time.time()
        logging.info(f"⏱ Форматирование: {(format_time - parse_time)*1000:.0f}ms")

        # Подтверждение покупателю (СРАЗУ!)
        user_id = message.from_user.id
        if user_id in ADMIN_IDS:
            await message.answer(
                "✅ Заказ успешно оформлен!",
                reply_markup=admin_menu()
            )
        else:
            await message.answer(
                "✅ Ваш заказ успешно оформлен!\n"
                "Менеджер свяжется с вами в ближайшее время.",
                reply_markup=user_menu()
            )
        answer_time = time.time()
        logging.info(f"⏱ Ответ пользователю: {(answer_time - format_time)*1000:.0f}ms")
        
        # Отправляем заказ в группу продавца (в фоне)
        try:
            await bot.send_message(GROUP_ID, order_text, parse_mode="HTML")
            group_time = time.time()
            logging.info(f"✅ Заказ отправлен в группу за {(group_time - answer_time)*1000:.0f}ms")
            logging.info(f"⏱ ОБЩЕЕ ВРЕМЯ: {(group_time - start_time)*1000:.0f}ms")
        except Exception as group_error:
            logging.error(f"❌ Ошибка отправки в группу: {group_error}")

    except Exception as e:
        logging.error(f"Ошибка обработки заказа: {e}")
        user_id = message.from_user.id
        menu = admin_menu() if user_id in ADMIN_IDS else user_menu()
        await message.answer(
            "❌ Произошла ошибка при оформлении заказа. Попробуйте еще раз.",
            reply_markup=menu
        )


# ============= АДМИНИСТРАТИВНЫЕ ФУНКЦИИ =============

# Добавление товара - шаг 1: запрос ID
@dp.callback_query(F.data == "add_product")
async def add_product_start(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    # Показываем список существующих ID
    existing_ids = [p['id'] for p in products]
    id_list = ", ".join(existing_ids) if existing_ids else "нет товаров"
    
    await callback.message.answer(
        f"📝 Введите ID для нового товара\n\n"
        f"Существующие ID: {id_list}\n\n"
        f"💡 ID должен быть уникальным (например: 1, 2, 3 или custom_id)"
    )
    await state.set_state(AddProduct.product_id)
    await callback.answer()

# Добавление товара - шаг 2: получение ID, запрос названия
@dp.message(AddProduct.product_id)
async def add_product_id(message: types.Message, state: FSMContext):
    product_id = message.text.strip()
    
    # Проверяем уникальность ID
    if any(p['id'] == product_id for p in products):
        await message.answer(f"❌ ID '{product_id}' уже существует. Введите другой ID:")
        return
    
    await state.update_data(product_id=product_id)
    await message.answer("Введите название товара:")
    await state.set_state(AddProduct.name)

# Добавление товара - шаг 3: получение названия, запрос цены
@dp.message(AddProduct.name)
async def add_product_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите цену товара (только число):")
    await state.set_state(AddProduct.price)

# Добавление товара - шаг 4: получение цены, запрос описания
@dp.message(AddProduct.price)
async def add_product_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price=price)
        await message.answer(
            "📝 Введите описание товара (1-2 строки)\n\n"
            "Например: Размер М, новое\n"
            "Или напишите 'пропустить' чтобы добавить без описания"
        )
        await state.set_state(AddProduct.description)
    except ValueError:
        await message.answer("❌ Неверный формат цены. Введите число:")

# Добавление товара - шаг 5: получение описания, запрос изображения
@dp.message(AddProduct.description)
async def add_product_description(message: types.Message, state: FSMContext):
    description = message.text if message.text.lower() != 'пропустить' else ''
    await state.update_data(description=description)
    await message.answer(
        "📸 Отправьте фото товара или URL изображения\n\n"
        "Вы можете:\n"
        "• Отправить фото (рекомендуется)\n"
        "• Отправить URL изображения\n"
        "• Написать 'пропустить' чтобы добавить без фото"
    )
    await state.set_state(AddProduct.image)

# Добавление товара - шаг 6: получение изображения и сохранение
@dp.message(AddProduct.image)
async def add_product_image(message: types.Message, state: FSMContext):
    # Получаем все данные
    data = await state.get_data()
    product_id = data['product_id']
    
    image_url = ''
    
    # Проверяем, отправил ли пользователь фото
    if message.photo:
        try:
            # Получаем самое большое фото
            photo = message.photo[-1]
            
            # Генерируем уникальное имя файла
            timestamp = int(time.time())
            file_name = f"product_{product_id}_{timestamp}.jpg"
            file_path = IMAGES_DIR / file_name
            
            # Скачиваем фото
            await bot.download(photo, destination=file_path)
            
            # Формируем URL для веб-приложения
            image_url = f"https://fine322223.github.io/bogato/images/products/{file_name}"
            
            logging.info(f"✅ Фото сохранено: {file_path}")
            
        except Exception as e:
            logging.error(f"Ошибка сохранения фото: {e}")
            await message.answer(f"❌ Ошибка сохранения фото: {e}")
            return
    
    elif message.text and message.text.lower() != 'пропустить':
        # Если отправлен текст (URL), используем его
        image_url = message.text
    
    # Создаем новый товар
    new_product = {
        'id': product_id,
        'name': data['name'],
        'price': data['price'],
        'description': data.get('description', ''),
        'image': image_url
    }
    
    products.append(new_product)
    
    # Сохраняем в файл
    if save_products_to_file(products):
        await message.answer(
            f"✅ Товар добавлен и сохранен:\n\n"
            f"Название: {new_product['name']}\n"
            f"Цена: {new_product['price']} ₽\n"
            f"Описание: {new_product['description'] if new_product['description'] else '❌ Нет'}\n"
            f"Изображение: {'📸 Фото загружено' if message.photo else ('🔗 URL' if image_url else '❌ Нет')}\n\n"
            f"Товар автоматически появится в магазине через 2-3 минуты!",
            reply_markup=admin_menu()
        )
    else:
        await message.answer(
            "❌ Ошибка сохранения товара",
            reply_markup=admin_menu()
        )
    
    await state.clear()

# Список товаров
@dp.callback_query(F.data == "list_products")
async def list_products(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    if not products:
        await callback.message.answer("📋 Список товаров пуст", reply_markup=admin_menu())
        await callback.answer()
        return
    
    text = "📋 <b>Список товаров:</b>\n\n"
    for p in products:
        text += f"ID: {p['id']}\n"
        text += f"• {p['name']} - {p['price']} ₽\n\n"
    
    await callback.message.answer(text, parse_mode="HTML", reply_markup=admin_menu())
    await callback.answer()

# Редактирование товара - шаг 1: выбор товара
@dp.callback_query(F.data == "edit_product")
async def edit_product_start(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    if not products:
        await callback.message.answer("❌ Нет товаров для редактирования", reply_markup=admin_menu())
        await callback.answer()
        return
    
    text = "📋 Выберите товар для редактирования (введите ID):\n\n"
    for p in products:
        text += f"ID: {p['id']} - {p['name']}\n"
    
    await callback.message.answer(text)
    await state.set_state(EditProduct.select_product)
    await callback.answer()

# Редактирование товара - шаг 2: получение ID
@dp.message(EditProduct.select_product)
async def edit_product_select(message: types.Message, state: FSMContext):
    product_id = message.text
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        await message.answer("❌ Товар не найден. Попробуйте еще раз:")
        return
    
    await state.update_data(product_id=product_id)
    await message.answer(
        f"Редактирование товара: {product['name']}\n\n"
        f"Что хотите изменить?\n"
        f"1 - Название\n"
        f"2 - Цена\n"
        f"3 - Описание\n"
        f"4 - Изображение"
    )
    await state.set_state(EditProduct.edit_field)

# Редактирование товара - шаг 3: выбор поля
@dp.message(EditProduct.edit_field)
async def edit_product_field(message: types.Message, state: FSMContext):
    field = message.text
    
    if field not in ['1', '2', '3', '4']:
        await message.answer("❌ Неверный выбор. Введите 1, 2, 3 или 4:")
        return
    
    field_name = {'1': 'name', '2': 'price', '3': 'description', '4': 'image'}[field]
    await state.update_data(field=field_name)
    
    prompt = "Введите новое значение:"
    if field == '3':
        prompt = "Введите новое описание (или 'пропустить' чтобы удалить):"
    elif field == '4':
        prompt = "Отправьте новое фото или URL:"
    
    await message.answer(prompt)
    await state.set_state(EditProduct.new_value)

# Редактирование товара - шаг 4: получение нового значения
@dp.message(EditProduct.new_value)
async def edit_product_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    product_id = data['product_id']
    field = data['field']
    
    product = next((p for p in products if p['id'] == product_id), None)
    
    # Обработка разных типов полей
    if field == 'price':
        try:
            new_value = float(message.text)
        except ValueError:
            await message.answer("❌ Неверный формат цены. Попробуйте еще раз:")
            return
        product[field] = new_value
    
    elif field == 'description':
        # Если редактируем описание
        if message.text.lower() == 'пропустить':
            product[field] = ''
        else:
            product[field] = message.text
    
    elif field == 'image':
        # Если изменяем изображение
        if message.photo:
            try:
                # Получаем самое большое фото
                photo = message.photo[-1]
                
                # Генерируем уникальное имя файла
                timestamp = int(time.time())
                file_name = f"product_{product_id}_{timestamp}.jpg"
                file_path = IMAGES_DIR / file_name
                
                # Скачиваем фото
                await bot.download(photo, destination=file_path)
                
                # Формируем URL
                new_value = f"https://fine322223.github.io/bogato/images/products/{file_name}"
                product[field] = new_value
                
                logging.info(f"✅ Фото обновлено: {file_path}")
                
            except Exception as e:
                logging.error(f"Ошибка сохранения фото: {e}")
                await message.answer(f"❌ Ошибка сохранения фото: {e}")
                return
        else:
            # Если отправлен текст (URL)
            product[field] = message.text
    
    else:
        # Для остальных полей (name)
        product[field] = message.text
    
    # Сохраняем изменения в файл
    if save_products_to_file(products):
        await message.answer(
            f"✅ Товар обновлен и сохранен:\n\n"
            f"ID: {product['id']}\n"
            f"Название: {product['name']}\n"
            f"Цена: {product['price']} ₽\n"
            f"Изображение: {'Да' if product['image'] else 'Нет'}",
            reply_markup=admin_menu()
        )
    else:
        await message.answer(
            "❌ Ошибка сохранения изменений",
            reply_markup=admin_menu()
        )
    
    await state.clear()

# Удаление товара - шаг 1: выбор товара
@dp.callback_query(F.data == "delete_product")
async def delete_product_start(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    if not products:
        await callback.message.answer("❌ Нет товаров для удаления", reply_markup=admin_menu())
        await callback.answer()
        return
    
    text = "🗑 <b>Удаление товаров</b>\n\n"
    text += "Список товаров:\n\n"
    for p in products:
        text += f"ID: {p['id']} - {p['name']}\n"
    
    text += "\n<b>Введите ID товаров для удаления</b>\n"
    text += "Можно удалить один товар: <code>5</code>\n"
    text += "Или несколько через запятую: <code>1,3,5</code> или <code>1, 2, 3</code>"
    
    await callback.message.answer(text, parse_mode="HTML")
    await state.set_state("delete_product_id")
    await callback.answer()

# Удаление товара - шаг 2: подтверждение и удаление
@dp.message(F.text, StateFilter("delete_product_id"))
async def delete_product_confirm(message: types.Message, state: FSMContext):
    try:
        # Парсим ID из сообщения (поддержка одного или нескольких ID)
        ids_text = message.text.strip()
        ids = [id.strip() for id in ids_text.split(',')]
        
        deleted_count = 0
        deleted_names = []
        deleted_images = []
        not_found = []
        
        for product_id in ids:
            product = next((p for p in products if p['id'] == product_id), None)
            
            if product:
                # Удаляем изображение товара, если оно есть
                if product.get('image'):
                    image_path = product['image']
                    # Извлекаем имя файла из пути
                    if image_path.startswith('images/products/'):
                        file_name = image_path.replace('images/products/', '')
                        full_image_path = IMAGES_DIR / file_name
                        
                        # Удаляем файл, если он существует
                        if full_image_path.exists():
                            try:
                                full_image_path.unlink()
                                deleted_images.append(file_name)
                                logging.info(f"🗑 Удалено изображение: {file_name}")
                            except Exception as e:
                                logging.error(f"❌ Ошибка удаления изображения {file_name}: {e}")
                
                products.remove(product)
                deleted_names.append(product['name'])
                deleted_count += 1
            else:
                not_found.append(product_id)
        
        # Сохраняем изменения
        if deleted_count > 0:
            if save_products_to_file(products):
                if deleted_count == 1:
                    result_text = f"✅ Товар удален: {deleted_names[0]}"
                else:
                    result_text = f"✅ Удалено товаров: {deleted_count}\n\n"
                    result_text += "Удаленные товары:\n" + "\n".join(f"• {name}" for name in deleted_names)
                
                if deleted_images:
                    result_text += f"\n\n🗑 Удалено изображений: {len(deleted_images)}"
                
                if not_found:
                    result_text += f"\n\n⚠️ Не найдены ID: {', '.join(not_found)}"
                
                await message.answer(result_text, reply_markup=admin_menu())
            else:
                await message.answer("❌ Ошибка сохранения", reply_markup=admin_menu())
        else:
            await message.answer(
                f"❌ Ни один товар не найден. Проверьте ID: {', '.join(not_found)}",
                reply_markup=admin_menu()
            )
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}", reply_markup=admin_menu())
    
    await state.clear()


# Отладочный обработчик для всех сообщений
@dp.message()
async def debug_all_messages(message: types.Message):
    logging.info(f"📨 Получено сообщение: type={message.content_type}, from={message.from_user.id}")
    if message.web_app_data:
        logging.info(f"🌐 WebApp данные присутствуют!")


# Запуск бота
if __name__ == "__main__":
    print("Бот запущен!")
    asyncio.run(dp.start_polling(bot, skip_updates=True))
