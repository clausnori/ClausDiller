# ClausDiller
Бот для создания экономики в Telegram 
## Установка зависимостей
``
## Установка
Указать токен в main.py
```(python)
updater = Updater("TOKEN", use_context=True)
    
```
## Запуск 
```(python)
python3 main.py
```
Указать данные в файле handlers.py:
ID для администратора чтобы использовать команды админа
```(python)
ADMIN_ID = "123"
```


## Магазин
Обычный масив Python

```(python)
# Список доступных товаров в магазине с их ценами
shop_items = {
    "Knife": 20,
    "Protection": 20,
    "Detective": 30,
    "Code":1000,
    "VIP":1000
}
```
## Размер инвентаря
```(python)
MAX_INVENTORY_SIZE = 5
```

