// Инициализация Telegram WebApp
if (window.Telegram?.WebApp) {
    Telegram.WebApp.ready();
    Telegram.WebApp.expand();
}
        // === ЛОГГИРОВАНИЕ ДАННЫХ (для отладки) ===
    function debugLogData(orderData) {
        console.log("📦 Данные для отправки:", orderData);
        
        // Создаем скрытый элемент для копирования
        const debugDiv = document.createElement('div');
        debugDiv.style.position = 'fixed';
        debugDiv.style.top = '10px';
        debugDiv.style.left = '10px';
        debugDiv.style.background = 'rgba(0,0,0,0.8)';
        debugDiv.style.color = 'white';
        debugDiv.style.padding = '10px';
        debugDiv.style.borderRadius = '5px';
        debugDiv.style.zIndex = '9999';
        debugDiv.style.fontSize = '12px';
        debugDiv.style.maxWidth = '300px';
        debugDiv.style.wordBreak = 'break-all';
        debugDiv.innerHTML = `
            <strong>Данные для отправки:</strong><br>
            ${JSON.stringify(orderData, null, 2).replace(/\n/g, '<br>').replace(/ /g, '&nbsp;')}
            <br><br>
            <button onclick="copyDebugData()" style="background: #007bff; color: white; border: none; padding: 5px; border-radius: 3px; cursor: pointer;">
                Копировать данные
            </button>
            <button onclick="this.parentElement.remove()" style="background: #dc3545; color: white; border: none; padding: 5px; border-radius: 3px; cursor: pointer;">
                Закрыть
            </button>
        `;
        
        document.body.appendChild(debugDiv);
    }

    function copyDebugData() {
        const orderData = {
            name: document.getElementById("name")?.value || "Test Name",
            phone: document.getElementById("phone")?.value || "+79990001122",
            address: document.getElementById("address")?.value || "Test Address",
            telegram: document.getElementById("telegram")?.value || "@testuser",
            cart: cart.map(c => ({ id: c.ID, title: c.Name, price: c.Cost }))
        };
        
        navigator.clipboard.writeText(JSON.stringify(orderData, null, 2));
        alert('Данные скопированы в буфер обмена!');
    }

    // Добавляем кнопку отладки в интерфейс
    function addDebugButton() {
        const debugBtn = document.createElement('button');
        debugBtn.innerHTML = '🐛 Debug';
        debugBtn.style.position = 'fixed';
        debugBtn.style.bottom = '70px';
        debugBtn.style.right = '10px';
        debugBtn.style.zIndex = '9998';
        debugBtn.style.background = '#ffc107';
        debugBtn.style.color = 'black';
        debugBtn.style.border = 'none';
        debugBtn.style.padding = '8px';
        debugBtn.style.borderRadius = '5px';
        debugBtn.style.cursor = 'pointer';
        debugBtn.onclick = () => {
            const testData = {
                name: "Test User",
                phone: "+79990001122", 
                address: "Moscow, Test Street 1",
                telegram: "@testuser",
                cart: [{id: "test1", title: "Test Product", price: 1000}]
            };
            debugLogData(testData);
        };
        
        document.body.appendChild(debugBtn);
    }

    // Инициализация отладки после загрузки
    setTimeout(addDebugButton, 2000);

      //==============================================

    // URL для загрузки данных о товарах
    const API_URL = "https://script.google.com/macros/s/AKfycbxmzenU7gOI0DOyUfuJ_gV-l4zwizB4rn8rh07EXeteKv-pcj-WDx62pxdtxrp3j-cskQ/exec";
    let products = [];
    let cart = [];

    // Загрузка товаров с сервера
    async function loadProducts() {
        try {
            const res = await fetch(API_URL);
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            products = await res.json();
            renderProducts(products);
        } catch (error) {
            console.error("Ошибка загрузки товаров:", error);
            document.getElementById("product-list").innerHTML = 
                "<p style='text-align:center;width:100%;padding:20px;'>Ошибка загрузки товаров</p>";
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
            <img src="${item.Picture}" alt="${item.Name}" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjJmMmYyIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtc2l6ZT0iMTQiIGZpbGw9IiM5OTkiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIwLjM1ZW0iPk5vIGltYWdlPC90ZXh0Pjwvc3ZnPg=='">
          </div>
          <div class="product-info">
            <div class="product-details">
              <h3 class="product-name">${item.Name}</h3>
              <p class="product-price">${item.Cost} ₽</p>
            </div>
            <button class="add-to-cart" onclick="addToCart('${item.ID}')">+</button>
          </div>
        `;
        container.appendChild(div);
      });
    }

    // Добавление товара в корзину
    function addToCart(id) {
      const item = products.find(p => p.ID == id);
      cart.push(item);
      document.getElementById("cart-count").innerText = cart.length;
    }

    // Удаление товара из корзины
    function removeFromCart(index) {
      cart.splice(index, 1); // удаляем товар по индексу
      document.getElementById("cart-count").innerText = cart.length; // обновляем счётчик
      const list = document.getElementById("cart-items");
      list.innerHTML = cart.map((c, i) => `
        <div class="cart-item">
          <span>${c.Name} - ${c.Cost} ₽</span>
          <button class="remove-btn" onclick="removeFromCart(${i})">❌</button>
        </div>
      `).join("");
    }

    // Поиск товаров
    document.getElementById("search").addEventListener("input", e => {
      const q = e.target.value.toLowerCase();
      const filtered = products.filter(p => p.Name.toLowerCase().includes(q));
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
        sorted.sort((a, b) => a.Cost - b.Cost);
      } else if (order === "desc") {
        sorted.sort((a, b) => b.Cost - a.Cost);
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

      const filtered = products.filter(p => p.Cost >= min && p.Cost <= max);
      renderProducts(filtered);
      closeFilter();
    }

    // Открытие корзины
    document.getElementById("cart-btn").addEventListener("click", () => {
      const list = document.getElementById("cart-items");
      list.innerHTML = cart.map((c, index) => `
        <div class="cart-item">
          <span>${c.Name} - ${c.Cost} ₽</span>
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
      document.getElementById("cart-modal").classList.add("hidden");
      document.getElementById("checkout-modal").classList.remove("hidden");
    });

    // Закрытие окна оформления заказа
    function closeCheckout() {
      document.getElementById("checkout-modal").classList.add("hidden");
    }

    // Подтверждение заказа
    document.getElementById("confirm-order").addEventListener("click", () => {
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

    const order = {
        name: name,
        phone: phone,
        address: address,
        telegram: telegramInput,
        cart: cart.map(c => ({
            id: c.ID,
            title: c.Name,
            price: c.Cost
        }))
    };

        // === ОТЛАДОЧНЫЙ ВЫВОД ===
    debugLogData(order);
    console.log("Отправляемые данные:", order);
    
    if (window.Telegram?.WebApp) {
        Telegram.WebApp.sendData(JSON.stringify(order));
        Telegram.WebApp.close();
    } else {
        alert("Telegram WebApp не доступен");
        console.log("Данные (имитация отправки):", JSON.stringify(order));
    }
    //=================================================================

    console.log("Sending order:", order); // Для отладки

    // Отправка данных заказа в Telegram бота
    if (window.Telegram?.WebApp) {
        Telegram.WebApp.sendData(JSON.stringify(order));
        //Telegram.WebApp.close();
    } else {
        alert("Telegram WebApp не доступен");
    }
    });

    // Загрузка товаров при запуске
    loadProducts();