# ClausDiller
Бот для создания экономики в Telegram 
## Установка зависимостей
```
pip install -r requirements.txt
```
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
# Админ команды
```
/send - Отправить сообщение всем участникам

/delete_item <item> <nickname> - Удалить предмет у человека
/send_all <number> - Отправить всем некоторое количество монет
```
