// URL для загрузки данных о товарах
    const API_URL = "https://script.google.com/macros/s/AKfycbxmzenU7gOI0DOyUfuJ_gV-l4zwizB4rn8rh07EXeteKv-pcj-WDx62pxdtxrp3j-cskQ/exec";
    let products = [];
    let cart = [];

    // Загрузка товаров с сервера
    async function loadProducts() {
      const res = await fetch(API_URL);
      products = await res.json();
      renderProducts(products);
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
      let telegramInput = document.getElementById("telegram").value.trim();
      // Проверяем ник на наличие @
      if (telegramInput && !telegramInput.startsWith("@")) {
        telegramInput = "@" + telegramInput;
      }

      const order = {
        name: document.getElementById("name").value,
        phone: document.getElementById("phone").value,
        address: document.getElementById("address").value,
        telegram: telegramInput,
        cart: cart.map(c => ({
          id: c.ID,
          title: c.Name,
          price: c.Cost
        }))
      };


      // Отправка данных заказа в Telegram бота
      Telegram.WebApp.sendData(JSON.stringify(order));
      Telegram.WebApp.close();
    });

    // Загрузка товаров при запуске
    loadProducts();