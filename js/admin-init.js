// admin-init.js
// Скрипт для быстрой инициализации магазина тестовыми товарами
// Использовать только для администраторов!

(function() {
    'use strict';
    
    // Тестовые товары
    const testProducts = [
        {
            ID: '1',
            Name: 'Сумка Louis Vuitton Premium',
            Cost: 45000,
            Picture: 'https://images.unsplash.com/photo-1591561954557-26941169b49e?w=400'
        },
        {
            ID: '2',
            Name: 'Кошелек Gucci Luxury',
            Cost: 25000,
            Picture: 'https://images.unsplash.com/photo-1627123424574-724758594e93?w=400'
        },
        {
            ID: '3',
            Name: 'Ремень Hermes Classic',
            Cost: 15000,
            Picture: 'https://images.unsplash.com/photo-1624222247344-550fb60583c0?w=400'
        },
        {
            ID: '4',
            Name: 'Рюкзак Prada Elite',
            Cost: 38000,
            Picture: 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400'
        },
        {
            ID: '5',
            Name: 'Клатч Versace Gold',
            Cost: 22000,
            Picture: 'https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=400'
        },
        {
            ID: '6',
            Name: 'Портфель Armani Business',
            Cost: 32000,
            Picture: 'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400'
        }
    ];
    
    // Функция инициализации
    function initTestProducts() {
        try {
            // Сохраняем в LocalStorage
            localStorage.setItem('bogato_products', JSON.stringify(testProducts));
            console.log('✅ Тестовые товары успешно добавлены!');
            console.log(`Добавлено товаров: ${testProducts.length}`);
            
            // Перезагружаем страницу для отображения
            if (confirm('Товары добавлены! Перезагрузить страницу?')) {
                location.reload();
            }
        } catch (error) {
            console.error('❌ Ошибка при добавлении товаров:', error);
        }
    }
    
    // Функция очистки
    function clearProducts() {
        try {
            localStorage.removeItem('bogato_products');
            console.log('✅ Все товары удалены!');
            
            if (confirm('Товары удалены! Перезагрузить страницу?')) {
                location.reload();
            }
        } catch (error) {
            console.error('❌ Ошибка при удалении товаров:', error);
        }
    }
    
    // Функция просмотра товаров
    function viewProducts() {
        try {
            const stored = localStorage.getItem('bogato_products');
            if (stored) {
                const products = JSON.parse(stored);
                console.log('📋 Текущие товары:');
                console.table(products);
                console.log(`Всего товаров: ${products.length}`);
            } else {
                console.log('📋 Товары отсутствуют');
            }
        } catch (error) {
            console.error('❌ Ошибка при просмотре товаров:', error);
        }
    }
    
    // Экспортируем функции в window для использования в консоли
    window.BogatoAdmin = {
        init: initTestProducts,
        clear: clearProducts,
        view: viewProducts,
        testProducts: testProducts
    };
    
    console.log('🔧 Bogato Admin Tools загружены!');
    console.log('Доступные команды:');
    console.log('  BogatoAdmin.init()  - Добавить тестовые товары');
    console.log('  BogatoAdmin.clear() - Удалить все товары');
    console.log('  BogatoAdmin.view()  - Просмотреть товары');
    
})();
