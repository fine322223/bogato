#!/bin/bash
# Быстрый скрипт для загрузки товаров на GitHub

cd /Users/fine/Documents/bogato
git add products.json
git commit -m "обновление товаров"
git push

echo "✅ Товары загружены на GitHub!"
echo "Они появятся на сайте через 2-3 минуты"
