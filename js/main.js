// Инициализация Telegram WebApp
if (window.Telegram?.WebApp) {
    console.log("🚀 Telegram WebApp инициализация");
    console.log("Версия WebApp:", Telegram.WebApp.version);
    console.log("Платформа:", Telegram.WebApp.platform);
    console.log("InitData:", Telegram.WebApp.initData);
    console.log("IsInline:", Telegram.WebApp.isInline);
    
    Telegram.WebApp.ready();
    Telegram.WebApp.expand();
    
    console.log("✅ WebApp готов к работе");
} else {
    console.error("❌ Telegram WebApp недоступен!");
}

let products = [];
let cart = [];

// URL к файлу с товарами на GitHub
const PRODUCTS_URL = 'https://raw.githubusercontent.com/fine322223/bogato/main/products.json';

// Функция отправки заказа
function submitOrder() {
    console.log("submitOrder вызвана");
    
    // Проверка заполненности полей
    const name = document.getElementById("name").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const address = document.getElementById("address").value.trim();
    const telegram = document.getElementById("telegram").value.trim();

    if (!name || !phone || !address || !telegram) {
        alert("Пожалуйста, заполните все поля");
        return;
    }

    if (cart.length === 0) {
        alert("Корзина пуста");
        return;
    }

    let telegramInput = telegram;
    // Проверяем ник на наличие @
    if (telegramInput && !telegramInput.startsWith("@")) {
        telegramInput = "@" + telegramInput;
    }

    // Формируем данные заказа
    const order = {
        name: name,
        phone: phone,
        address: address,
        telegram: telegramInput,
        cart: cart.map(c => ({
            id: c.id,
            title: c.name,
            price: c.price
        }))
    };

    console.log("Отправка заказа:", order);

    // Отправка данных заказа через WebApp
    if (window.Telegram?.WebApp) {
        try {
            console.log("Отправка через Telegram WebApp");
            const jsonData = JSON.stringify(order);
            console.log("JSON данные:", jsonData);
            
            // Для iOS: кодируем в base64 и отправляем
            const base64Data = btoa(unescape(encodeURIComponent(jsonData)));
            console.log("Base64 данные:", base64Data);
            
            // Отправляем данные
            Telegram.WebApp.sendData(base64Data);
            console.log("✅ Данные отправлены!");
            
        } catch (error) {
            console.error("❌ Ошибка отправки:", error);
            alert("Ошибка: " + error.message);
        }
    } else {
        console.error("Telegram WebApp недоступен");
        alert("Telegram WebApp недоступен");
    }
}

// Загрузка товаров из JSON файла на GitHub
async function loadProducts() {
    try {
        const response = await fetch(PRODUCTS_URL + '?t=' + Date.now()); // Добавляем timestamp для обхода кэша
        
        if (response.ok) {
            products = await response.json();
        } else {
            console.warn("Файл с товарами не найден, используем пустой массив");
            products = [];
        }
        
        renderProducts(products);
    } catch (error) {
        console.error("Ошибка загрузки товаров:", error);
        products = [];
        renderProducts(products);
    }
}

    // Отображение товаров на странице
    function renderProducts(list) {
      const container = document.getElementById("product-list");
      container.innerHTML = "";
  
      if (list.length === 0) {
        container.innerHTML = "<p style='text-align:center;width:100%;padding:20px;'>Товары не найдены</p>";
        return;
      }
  
      list.forEach(item => {
        const div = document.createElement("div");
        div.className = "product";
        div.innerHTML = `
          <div class="product-image">
            <img src="${item.image}" alt="${item.name}" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjJmMmYyIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM5OTkiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIwLjM1ZW0iPk5vIGltYWdlPC90ZXh0Pjwvc3ZnPg=='">
          </div>
          <div class="product-info">
            <div class="product-details">
              <h3 class="product-name">${item.name}</h3>
              <p class="product-price">${item.price} ₽</p>
            </div>
            <button class="add-to-cart" onclick="addToCart('${item.id}')">+</button>
          </div>
        `;
        container.appendChild(div);
      });
    }

    // Добавление товара в корзину
    function addToCart(id) {
      const item = products.find(p => p.id == id);
      cart.push(item);
      document.getElementById("cart-count").innerText = cart.length;
    }

    // Удаление товара из корзины
    function removeFromCart(index) {
      cart.splice(index, 1);
      document.getElementById("cart-count").innerText = cart.length;
      const list = document.getElementById("cart-items");
      list.innerHTML = cart.map((c, i) => `
        <div class="cart-item">
          <span>${c.name} - ${c.price} ₽</span>
          <button class="remove-btn" onclick="removeFromCart(${i})">❌</button>
        </div>
      `).join("");
    }

    // Поиск товаров
    document.getElementById("search").addEventListener("input", e => {
      const q = e.target.value.toLowerCase();
      const filtered = products.filter(p => p.name.toLowerCase().includes(q));
      renderProducts(filtered);
    });

    // Открытие/закрытие сортировки
    document.getElementById("sort-btn").addEventListener("click", () => {
      document.getElementById("sort-modal").classList.remove("hidden");
    });
    function closeSort() {
      document.getElementById("sort-modal").classList.add("hidden");
    }

    // Применение сортировки
    function applySort(order) {
      let sorted = [...products];
      if (order === "asc") {
        sorted.sort((a, b) => a.price - b.price);
      } else if (order === "desc") {
        sorted.sort((a, b) => b.price - a.price);
      }
      renderProducts(sorted);
      closeSort();
    }

    // Открытие/закрытие фильтра
    document.getElementById("filter-btn").addEventListener("click", () => {
      document.getElementById("filter-modal").classList.remove("hidden");
    });
    function closeFilter() {
      document.getElementById("filter-modal").classList.add("hidden");
    }

    // Применение фильтра
    function applyFilter() {
      const min = parseFloat(document.getElementById("min-price").value) || 0;
      const max = parseFloat(document.getElementById("max-price").value) || Infinity;

      const filtered = products.filter(p => p.price >= min && p.price <= max);
      renderProducts(filtered);
      closeFilter();
    }

    // Открытие корзины
    document.getElementById("cart-btn").addEventListener("click", () => {
      const list = document.getElementById("cart-items");
      list.innerHTML = cart.map((c, index) => `
        <div class="cart-item">
          <span>${c.name} - ${c.price} ₽</span>
          <button class="remove-btn" onclick="removeFromCart(${index})">❌</button>
        </div>
      `).join("");
      document.getElementById("cart-modal").classList.remove("hidden");
    });

    // Закрытие корзины
    function closeCart() {
      document.getElementById("cart-modal").classList.add("hidden");
    }

    // Переход к оформлению заказа
    document.getElementById("checkout-btn").addEventListener("click", () => {
      console.log("Переход к оформлению заказа");
      document.getElementById("cart-modal").classList.add("hidden");
      document.getElementById("checkout-modal").classList.remove("hidden");
      
      // Устанавливаем обработчик на кнопку оформления
      const submitBtn = document.getElementById("submit-order-btn");
      console.log("Кнопка найдена:", submitBtn);
      if (submitBtn) {
          submitBtn.onclick = function() {
              console.log("🔔 Кнопка нажата!");
              submitOrder();
          };
          console.log("Обработчик установлен на кнопку");
      } else {
          console.error("❌ Кнопка submit-order-btn не найдена!");
      }
    });

    // Закрытие окна оформления заказа
    function closeCheckout() {
      document.getElementById("checkout-modal").classList.add("hidden");
    }

    // Загрузка товаров при запуске
    loadProducts();