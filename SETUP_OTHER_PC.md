# 🚀 Инструкция для запуска бота на другом компьютере

## 📥 Шаг 1: Скачайте проект

На другом компьютере выполните:

```bash
cd ~
git clone https://github.com/fine322223/bogato.git
cd bogato
```

## 🔧 Шаг 2: Установите зависимости

```bash
pip3 install aiogram
```

Или через requirements.txt:
```bash
pip3 install -r requirements.txt
```

## ⚙️ Шаг 3: Настройте git для автопуша

**ВАЖНО:** Выполните эти команды в папке проекта:

```bash
git config user.name "fine322223"
git config user.email "fine.oo.oo@yandex.ru"
git remote set-url origin https://fine322223:ВАШ_ТОКЕН@github.com/fine322223/bogato.git
```

**Замените `ВАШ_ТОКЕН` на ваш Personal Access Token от GitHub!**

Где взять токен:
1. https://github.com/settings/tokens
2. Generate new token (classic)
3. Поставьте галочку `repo`
4. Скопируйте токен

## 📝 Шаг 4: Проверьте bot.py

Убедитесь, что в `bot.py` указаны правильные данные:

```python
API_TOKEN = "7957824215:AAFXeeA8H7ElTOEAW5NGilydtwQkPFcMBu8"
GROUP_ID = -1003062619878
ADMIN_ID = 5186803258
```

## 🚀 Шаг 5: Запустите бота

### Вариант 1: В терминале
```bash
python3 bot.py
```

### Вариант 2: В VSCode
1. Откройте папку проекта: `code ~/bogato`
2. Откройте Terminal (Ctrl+`)
3. Запустите: `python3 bot.py`

### Вариант 3: В PyCharm
1. File → Open → выберите папку `bogato`
2. Откройте `bot.py`
3. Нажмите ▶️ (Run)

## ✅ Проверка работы

1. **Бот запустился:**
   ```
   Бот запущен!
   INFO:aiogram.dispatcher:Start polling
   ```

2. **Добавьте товар через Telegram:**
   - Откройте бота
   - /start
   - ➕ Добавить товар
   - Введите данные

3. **Проверьте логи:**
   ```
   INFO:root:✅ Товары автоматически загружены на GitHub!
   ```

4. **Проверьте на GitHub:**
   - Откройте: https://github.com/fine322223/bogato/blob/main/products.json
   - Товар должен быть там!

5. **Проверьте на сайте:**
   - Откройте магазин через бота
   - Через 2-3 минуты товар появится

## 🔄 Обновление проекта

Если внесли изменения на первом компьютере:

```bash
cd ~/bogato
git pull
```

## 📁 Структура проекта

```
bogato/
├── bot.py              ← Telegram бот
├── products.json       ← Файл с товарами
├── index.html          ← Главная страница магазина
├── css/styles.css      ← Стили
├── js/main.js          ← Логика магазина
├── requirements.txt    ← Зависимости Python
└── push.sh            ← Скрипт для ручного пуша (если нужно)
```

## 🐛 Проблемы?

### Ошибка: "fatal: not a git repository"
→ Убедитесь, что запускаете бота из папки проекта

### Ошибка: "No module named 'aiogram'"
→ Установите: `pip3 install aiogram`

### Автопуш не работает
→ Проверьте настройки git (Шаг 3)

### Товары не появляются на сайте
→ Подождите 2-3 минуты после добавления
→ Откройте в режиме инкогнито

---

**Готово! Можете запускать бота на любом компьютере! 🎉**
