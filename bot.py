# bot.py
import asyncio
import json
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Токен бота и ID группы для заказов
API_TOKEN = "7957824215:AAFXeeA8H7ElTOEAW5NGilydtwQkPFcMBu8"
GROUP_ID = -1003062619878  # ID группы продавца
ADMIN_ID = 5186803258  # !!! ВАЖНО: Замените на ваш Telegram ID (узнать можно у @userinfobot)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=storage)

# Путь к файлу с товарами
PRODUCTS_FILE = Path(__file__).parent / "products.json"
PROJECT_DIR = Path(__file__).parent.absolute()  # Полный путь к проекту

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
            
            result = subprocess.run(['git', 'add', 'products.json'], 
                          cwd=project_path, 
                          capture_output=True, text=True)
            
            result = subprocess.run(['git', 'commit', '-m', 'Автообновление товаров'], 
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
    name = State()
    price = State()
    image = State()

# Состояния для редактирования товара
class EditProduct(StatesGroup):
    select_product = State()
    edit_field = State()
    new_value = State()

# Главное меню для обычных пользователей
def user_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="👜 Открыть магазин",
            web_app=WebAppInfo(url="https://fine322223.github.io/bogato/")
        )],
        [InlineKeyboardButton(
            text="📞 Техподдержка",
            url="https://t.me/fine911"
        )]
    ])
    return keyboard

# Меню администратора с дополнительными кнопками управления
def admin_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="👜 Открыть магазин",
            web_app=WebAppInfo(url="https://fine322223.github.io/bogato/")
        )],
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


# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    
    # Проверяем, является ли пользователь администратором
    if user_id == ADMIN_ID:
        await message.answer(
            "👋 Привет, Администратор!\n\n"
            "Добро пожаловать в панель управления магазином Bogato Boutique.\n"
            "Используйте кнопки ниже для управления товарами.",
            reply_markup=admin_menu()
        )
    else:
        await message.answer(
            "👋 Здравствуйте!\n\n"
            "Добро пожаловать в Bogato Boutique - магазин премиальных товаров.",
            reply_markup=user_menu()
        )


# Обработка заказов из WebApp
@dp.message(F.content_type == types.ContentType.WEB_APP_DATA)
async def handle_webapp_data(message: types.Message):
    import time
    start_time = time.time()
    logging.info(f"🔔 Получены данные из WebApp от пользователя {message.from_user.id}")
    try:
        # Парсим данные из веб-приложения
        data = json.loads(message.web_app_data.data)
        logging.info(f"📦 Данные заказа: {data}")
        parse_time = time.time()
        logging.info(f"⏱ Парсинг занял: {(parse_time - start_time)*1000:.0f}ms")
        
        name = data.get("name")
        phone = data.get("phone")
        address = data.get("address")
        telegram = data.get("telegram")
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
        logging.info(f"⏱ Форматирование текста: {(format_time - parse_time)*1000:.0f}ms")

        # Подтверждение покупателю (СРАЗУ!)
        user_id = message.from_user.id
        if user_id == ADMIN_ID:
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
        menu = admin_menu() if user_id == ADMIN_ID else user_menu()
        await message.answer(
            "❌ Произошла ошибка при оформлении заказа. Попробуйте еще раз.",
            reply_markup=menu
        )


# ============= АДМИНИСТРАТИВНЫЕ ФУНКЦИИ =============

# Добавление товара - шаг 1: запрос названия
@dp.callback_query(F.data == "add_product")
async def add_product_start(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if user_id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    await callback.message.answer("Введите название товара:")
    await state.set_state(AddProduct.name)
    await callback.answer()

# Добавление товара - шаг 2: получение названия, запрос цены
@dp.message(AddProduct.name)
async def add_product_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите цену товара (только число):")
    await state.set_state(AddProduct.price)

# Добавление товара - шаг 3: получение цены, запрос изображения
@dp.message(AddProduct.price)
async def add_product_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price=price)
        await message.answer("Отправьте URL изображения товара (или введите 'пропустить'):")
        await state.set_state(AddProduct.image)
    except ValueError:
        await message.answer("❌ Неверный формат цены. Введите число:")

# Добавление товара - шаг 4: получение изображения и сохранение
@dp.message(AddProduct.image)
async def add_product_image(message: types.Message, state: FSMContext):
    image_url = message.text if message.text.lower() != 'пропустить' else ''
    await state.update_data(image=image_url)
    
    # Получаем все данные
    data = await state.get_data()
    
    # Создаем новый товар
    new_product = {
        'id': str(len(products) + 1),
        'name': data['name'],
        'price': data['price'],
        'image': data['image']
    }
    
    products.append(new_product)
    
    # Сохраняем в файл
    if save_products_to_file(products):
        await message.answer(
            f"✅ Товар добавлен и сохранен:\n\n"
            f"Название: {new_product['name']}\n"
            f"Цена: {new_product['price']} ₽\n"
            f"Изображение: {'Да' if new_product['image'] else 'Нет'}\n\n"
            f"Товар автоматически появится в магазине!",
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
    if user_id != ADMIN_ID:
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
    if user_id != ADMIN_ID:
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
        f"3 - Изображение"
    )
    await state.set_state(EditProduct.edit_field)

# Редактирование товара - шаг 3: выбор поля
@dp.message(EditProduct.edit_field)
async def edit_product_field(message: types.Message, state: FSMContext):
    field = message.text
    
    if field not in ['1', '2', '3']:
        await message.answer("❌ Неверный выбор. Введите 1, 2 или 3:")
        return
    
    field_name = {'1': 'name', '2': 'price', '3': 'image'}[field]
    await state.update_data(field=field_name)
    
    await message.answer(f"Введите новое значение:")
    await state.set_state(EditProduct.new_value)

# Редактирование товара - шаг 4: получение нового значения
@dp.message(EditProduct.new_value)
async def edit_product_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    product_id = data['product_id']
    field = data['field']
    new_value = message.text
    
    product = next((p for p in products if p['id'] == product_id), None)
    
    if field == 'price':
        try:
            new_value = float(new_value)
        except ValueError:
            await message.answer("❌ Неверный формат цены. Попробуйте еще раз:")
            return
    
    product[field] = new_value
    
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
    if user_id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    if not products:
        await callback.message.answer("❌ Нет товаров для удаления", reply_markup=admin_menu())
        await callback.answer()
        return
    
    text = "🗑 Введите ID товара для удаления:\n\n"
    for p in products:
        text += f"ID: {p['id']} - {p['name']}\n"
    
    await callback.message.answer(text)
    await state.set_state("delete_product_id")
    await callback.answer()

# Удаление товара - шаг 2: подтверждение и удаление
@dp.message(F.text, lambda msg: msg.text.isdigit())
async def delete_product_confirm(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state != "delete_product_id":
        return
    
    product_id = message.text
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        await message.answer("❌ Товар не найден. Попробуйте еще раз:")
        return
    
    products.remove(product)
    
    # Сохраняем изменения в файл
    if save_products_to_file(products):
        await message.answer(
            f"✅ Товар удален и изменения сохранены:\n{product['name']}",
            reply_markup=admin_menu()
        )
    else:
        await message.answer(
            "❌ Ошибка сохранения изменений",
            reply_markup=admin_menu()
        )
    
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
