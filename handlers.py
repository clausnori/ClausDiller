import re
import random
from datetime import datetime, timedelta
from telegram.ext import Updater, CommandHandler

from utils import load_data, save_data

ADMIN_ID = "12345"  # Замените на реальный ID администратора
MAX_INVENTORY_SIZE = 5
# Список доступных товаров в магазине с их ценами
shop_items = {
    "Knife": 20,
    "Protection": 20,
    "Detective": 30,
    "Code":1000,
    "VIP":1000
}

#Охота
def hunt(update, context):
    user_id = str(update.message.from_user.id)
    data = load_data()

    # Проверка наличия ножа у пользователя
    if 'Knife' not in data[user_id].get('inventory', []):
        update.message.reply_text("Для охоты нужно иметь нож.")
        return

    # Удаление ножа из инвентаря пользователя
    data[user_id]['inventory'].remove('Knife')

    # Выполнение охоты
    loot = random.randint(10, 30)
    data[user_id]['coins'] += loot

    # Сообщение о результате охоты
    update.message.reply_text(f"Вы успешно охотились и получили {loot} монет.")

    # Сохранение обновленных данных
    save_data(data)

# Функция для проверки занятости ника
def is_nickname_taken(nickname):
    data = load_data()
    for user_data in data.values():
        if user_data['nickname'].lower() == nickname.lower():
            return True
    return False

def is_valid_nickname(nickname):
    # Проверка на наличие только английских букв, цифр и подчеркиваний в никнейме
    return re.match(r'^[a-zA-Z0-9_]+$', nickname) is not None

def register(update, context):
    try:
        nickname = context.args[0]
    except IndexError:
        update.message.reply_text("Используйте команду в формате: /reg <никнейм>")
        return

    # Проверка на корректность никнейма
    if not is_valid_nickname(nickname):
        update.message.reply_text("Никнейм должен содержать только английские буквы, цифры и подчеркивания.")
        return

    user_id = update.message.from_user.id
    if is_registered(user_id):
        update.message.reply_text("Вы уже зарегистрированы.")
        return
    if is_nickname_taken(nickname):
        update.message.reply_text("Этот никнейм уже занят. Пожалуйста, выберите другой.")
        return

    data = load_data()
    data[str(user_id)] = {"nickname": nickname, "coins": 0, "inventory": []}
    save_data(data)
    update.message.reply_text(f"Пользователь с никнеймом '{nickname}' успешно зарегистрирован.")
    
# Функция для проверки зарегистрирован ли пользователь
def is_registered(user_id):
    data = load_data()
    return str(user_id) in data
# Команда для майнинга
def mining(update, context):
    user_id = str(update.message.from_user.id)
    if not is_registered(user_id):
        update.message.reply_text("Для начала майнинга необходимо зарегистрироваться. Используйте команду /reg.")
        return

    data = load_data()
    user_data = data[user_id]

    coins_reward = 100
    
    if 'mining_end_time' not in user_data or user_data['mining_end_time'] is None or datetime.fromisoformat(user_data['mining_end_time']) < datetime.now():
        # Проверка на количество предметов в инвентаре
        if len(user_data.get('inventory', [])) >= MAX_INVENTORY_SIZE:
            update.message.reply_text("Ваш инвентарь переполнен. Продайте лишние предметы перед майнингом.")
            data[user_id] = {
                'nickname': user_data.get('nickname', ''),
                'coins': user_data.get('coins', 0) + coins_reward,
                'mining_end_time': (datetime.now() + timedelta(hours=1)).isoformat(),
                'inventory': user_data.get('inventory', [])
            }
            save_data(data)
            update.message.reply_text(f"Майнинг успешно запущен. Вы получили {coins_reward} монет.")
        else:
            data[user_id] = {
                'nickname': user_data.get('nickname', ''),
                'coins': user_data.get('coins', 0) + coins_reward,
                'mining_end_time': (datetime.now() + timedelta(hours=1)).isoformat(),
                'inventory': user_data.get('inventory', []) + ["Protection"]
            }
            save_data(data)
            update.message.reply_text(f"Майнинг успешно запущен. Вы получили {coins_reward} монет и предмет 'Protection'.")
    else:
        update.message.reply_text("Вы уже начали майнинг. Дождитесь окончания Кулдаун 1 час.")
#Гив
def send_coins_to_all_users(update, context):
    if str(update.message.from_user.id) != ADMIN_ID:
        update.message.reply_text("У вас нет прав на отправку монет всем пользователям.")
        return
    
    # Получаем количество монет для отправки из аргументов
    try:
        amount = int(context.args[0])
    except (IndexError, ValueError):
        update.message.reply_text("Используйте команду в формате: /send_all <количество монет>")
        return
    
    # Загружаем данные о пользователях
    data = load_data()
    
    # Отправляем указанное количество монет каждому пользователю
    for user_id in data:
        try:
            data[user_id]['coins'] += amount
        except KeyError:
            pass  # Если у пользователя нет монет, пропускаем его
    
    # Сохраняем обновленные данные
    save_data(data)
    
    # Уведомляем администратора об успешной отправке
    update.message.reply_text(f"Успешно отправлено {amount} монет всем пользователям.")

# Команда для передачи монет другому пользователю
def transfer_coins(update, context):
    try:
        amount, recipient_nickname = context.args
        amount = int(amount)
        sender_id = str(update.message.from_user.id)
        data = load_data()

        if amount <= 0:
            update.message.reply_text("Количество монет должно быть положительным числом.")
            return

        if sender_id not in data or data[sender_id]['coins'] < amount:
            update.message.reply_text("Недостаточно монет для передачи.")
            return

        # Поиск id получателя по его никнейму
        recipient_id = None
        for user_id, user_data in data.items():
            if user_data.get("nickname") == recipient_nickname:
                recipient_id = user_id
                break

        if not recipient_id:
            update.message.reply_text(f"Пользователь с никнеймом '{recipient_nickname}' не найден.")
            return

        data[sender_id]['coins'] -= amount

        # Обновление или создание записи о получателе
        recipient_data = data.get(recipient_id, {})
        recipient_data['coins'] = recipient_data.get('coins', 0) + amount
        recipient_data['mining_end_time'] = recipient_data.get('mining_end_time', None)
        data[recipient_id] = recipient_data

        save_data(data)
        update.message.reply_text(f"{amount} монет успешно переданы пользователю {recipient_nickname}.")
    except (ValueError, TypeError):
        update.message.reply_text("Некорректный формат команды. Используйте: /transfer <количество> <никнейм>")
        
# Команда для проверки баланса пользователя
def balance(update, context):
    user_id = str(update.message.from_user.id)
    data = load_data()
    if user_id in data:
        balance_message = f"Ваш текущий баланс: {data[user_id]['coins']} монет"
    else:
        balance_message = "У вас пока нет монет. Начните майнить!"
    update.message.reply_text(balance_message)

# Команда для отображения инвентаря пользователя
def inventory(update, context):
    user_id = str(update.message.from_user.id)
    data = load_data()

    if user_id in data and "inventory" in data[user_id] and data[user_id]["inventory"]:
        inventory_list = "\n".join(data[user_id]["inventory"])
        message = f"Ваш инвентарь:\n{inventory_list}"
    else:
        message = "Ваш инвентарь пуст."

    update.message.reply_text(message)
#Уведлмлене 
def send_message_to_all_users(update, context):
    # Проверяем, является ли пользователь администратором
    if str(update.message.from_user.id) != ADMIN_ID:
        update.message.reply_text("У вас нет прав на отправку сообщений всем пользователям.")
        return
    
    # Получаем текст сообщения из аргументов
    text = " ".join(context.args)
    
    # Загружаем данные о пользователях
    data = load_data()
    
    # Отправляем сообщение каждому пользователю
    for user_id in data:
        try:
            context.bot.send_message(chat_id=user_id, text=text)
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")
    
    # Уведомляем администратора об успешной отправке
    update.message.reply_text("Сообщение успешно отправлено всем пользователям.")

# Команда для отображения ре
def rating(update, context):
    data = load_data()
    sorted_users = sorted(data.items(), key=lambda x: x[1]['coins'], reverse=True)[:5]  # Получаем только первые 5 элементов
    rating_message = "Топ 5 пользователей по количеству монет:\n"
    for i, (user_id, user_data) in enumerate(sorted_users, start=1):
        nickname = user_data.get('nickname', f'User {i}')  # Получаем никнейм, если он есть, иначе используем заглушку
        rating_message += f"{i}. {nickname}: {user_data['coins']} монет\n"
    update.message.reply_text(rating_message)
    
# Команда для отображения списка товаров в магазине
def shop(update, context):
    items_list = "\n".join([f"{item}: {price} монет" for item, price in shop_items.items()])
    message = f"Доступные товары в магазине:\n{items_list}\nЧтобы купить товар, введите /buy <название товара>"
    update.message.reply_text(message)

# Функция для проверки наличия предмета в инвентаре пользователя
def has_item(user_id, item_name):
    data = load_data()
    if user_id in data:
        return item_name in data[user_id].get("inventory", [])
    return False

# Команда для покупки товара
def buy(update, context):
    user_id = str(update.message.from_user.id)
    data = load_data()
    args = context.args
    if len(args) == 0:
        update.message.reply_text("Используйте команду в формате: /buy <название товара>")
        return
    item_name = " ".join(args)
    if item_name not in shop_items:
        update.message.reply_text("Такого товара нет в магазине.")
        return
    item_price = shop_items[item_name]
    if user_id not in data:
        data[user_id] = {"coins": 0, "inventory": []}
    if "inventory" not in data[user_id]:
        data[user_id]["inventory"] = []  # Создаем список инвентаря, если его еще нет
    if data[user_id]["coins"] < item_price:
        update.message.reply_text("У вас недостаточно монет для покупки этого товара.")
        return
    
    # Проверка на максимальный размер инвентаря
    if len(data[user_id]["inventory"]) >= MAX_INVENTORY_SIZE:
        update.message.reply_text("Ваш инвентарь переполнен. Продайте лишние предметы перед покупкой новых.")
        return
    
    data[user_id]["coins"] -= item_price
    data[user_id]["inventory"].append(item_name)  # Добавляем купленный товар в инвентарь пользователя
    update.message.reply_text(f"Вы успешно купили {item_name} за {item_price} монет.")
    save_data(data)
    #продажа предметов 

# Функция для продажи товара
def sell_item(update, context):
    user_id = str(update.message.from_user.id)
    data = load_data()
    args = context.args

    if len(args) == 0:
        update.message.reply_text("Используйте команду в формате: /sell <название товара>")
        return

    item_name = " ".join(args)
    
    if not has_item(user_id, item_name):
        update.message.reply_text("У вас нет этого предмета в инвентаре.")
        return

    item_price = shop_items.get(item_name, 0)  # Получаем стоимость предмета из магазина
    if item_price == 0:
        update.message.reply_text("Этот предмет нельзя продать.")
        return

    sell_price = int(item_price * 0.9)  # Цена продажи = 90% от стоимости предмета

    data[user_id]["coins"] += sell_price  # Добавляем цену продажи предмета к монетам пользователя
    data[user_id]["inventory"].remove(item_name)  # Удаляем проданный товар из инвентаря

    update.message.reply_text(f"Вы успешно продали {item_name} за {sell_price} монет.")
    save_data(data)
    
#Всё пользователи
def all_users(update, context):
    if str(update.message.from_user.id) != ADMIN_ID:
        update.message.reply_text("Доступ запрещен. Эта команда предназначена только для администраторов.")
        return

    # Загрузка данных о пользователях
    data = load_data()

    # Формирование сообщения со всеми пользователями и их монетами
    all_users_message = "Список всех пользователей и их монет:\n"
    for user_id, user_data in data.items():
        nickname = user_data.get('nickname', f'User {user_id}')  # Получаем никнейм, если он есть, иначе используем заглушку
        coins = user_data.get('coins', 0)
        all_users_message += f"{nickname}: {coins} монет\n"

    # Отправка сообщения с информацией обо всех пользователях
    update.message.reply_text(all_users_message)

# Команда для ограбления другого пользователя
def rob(update, context):
    # Получение id грабителя
    robber_id = str(update.message.from_user.id)
    
    # Получение никнейма жертвы из аргументов команды
    try:
        victim_nickname = context.args[0]
    except IndexError:
        update.message.reply_text("Используйте команду в формате: /rob <никнейм>")
        return

    # Загрузка данных о пользователях
    data = load_data()

    # Получение id жертвы по никнейму
    victim_id = None
    for user_id, user_data in data.items():
        if user_data.get("nickname") == victim_nickname:
            victim_id = user_id
            break

    # Проверка наличия ограбляемого пользователя в данных
    if not victim_id:
        update.message.reply_text("Пользователь не найден.")
        return

    # Проверка наличия предмета "Knife" у грабителя
    if 'Knife' not in data[robber_id].get('inventory', []):
        update.message.reply_text("Для ограбления нужно иметь нож.")
        return

    # Удаление ножа из инвентаря грабителя
    data[robber_id].get('inventory', []).remove('Knife')

    # Проверка наличия предмета "Protection" у жертвы
    if 'Protection' in data[victim_id].get('inventory', []):
        # Удаление защиты из инвентаря жертвы
        data[victim_id].get('inventory', []).remove('Protection')
        update.message.reply_text("Ограбление не удалось из-за наличия защиты.")
    else:
        # Ограбление прошло успешно
        victim_coins = data[victim_id]['coins']
        max_stolen_coins = min(victim_coins // 5, 100)  # Выбираем минимум из 20% от количества монет жертвы и 100
        stolen_coins = random.randint(1, max_stolen_coins)
        data[robber_id]['coins'] += stolen_coins
        data[victim_id]['coins'] -= stolen_coins
        update.message.reply_text(f"Вы успешно ограбили пользователя @{victim_nickname} и украли {stolen_coins} монет.")

        # Уведомление жертвы об ограблении
        context.bot.send_message(victim_id, f"Вы были ограблены пользователем . Потеряно {stolen_coins} монет.")

    # Сохранение обновлённых данных
    save_data(data)
    
# Команда для передачи предмета другому пользователю
def give_item(update, context):
    giver_id = str(update.message.from_user.id)
    try:
        item, recipient_nickname = context.args
    except ValueError:
        update.message.reply_text("Используйте команду в формате: /give <предмет> <никнейм>")
        return

    # Загрузка данных о пользователях
    data = load_data()

    # Проверка наличия предмета у передающего
    if item not in data[giver_id].get('inventory', []):
        update.message.reply_text("У вас нет этого предмета в инвентаре.")
        return

    # Поиск id получателя по его никнейму
    recipient_id = None
    for user_id, user_data in data.items():
        if user_data.get("nickname") == recipient_nickname:
            recipient_id = user_id
            break

    if not recipient_id:
        update.message.reply_text(f"Пользователь с никнеймом '{recipient_nickname}' не найден.")
        return

    # Проверка количества предметов в инвентаре получателя
    if len(data[recipient_id].get('inventory', [])) >= 5:
        update.message.reply_text("Пользователь уже имеет максимальное количество предметов в инвентаре.")
        return

    # Передача предмета получателю
    data[giver_id]['inventory'].remove(item)
    data[recipient_id]['inventory'].append(item)

    # Сообщение об успешной передаче
    update.message.reply_text(f"Предмет '{item}' успешно передан пользователю '{recipient_nickname}'.")

    # Сохранение обновлённых данных
    save_data(data)
# Команда для просмотра инвентаря другого пользователя
def detective(update, context):
    detective_id = str(update.message.from_user.id)
    try:
        target_nickname = context.args[0]
    except IndexError:
        update.message.reply_text("Используйте команду в формате: /detective <никнейм>")
        return

    # Загрузка данных о пользователях
    data = load_data()

    # Проверка наличия предмета "Detective" у пользователя
    if 'Detective' not in data[detective_id].get('inventory', []):
        update.message.reply_text("У вас нет предмета 'Detective' в инвентаре.")
        return

    # Поиск ID цели по ее никнейму
    target_id = None
    for user_id, user_data in data.items():
        if user_data.get("nickname") == target_nickname:
            target_id = user_id
            break

    # Проверка наличия цели
    if not target_id:
        update.message.reply_text("Указанный пользователь не найден.")
        return

    # Просмотр инвентаря цели
    target_inventory = data[target_id].get('inventory', [])
    if not target_inventory:
        update.message.reply_text(f"Инвентарь пользователя @{target_nickname} пуст.")
    else:
        inventory_message = f"Инвентарь пользователя @{target_nickname}:\n"
        inventory_message += "\n".join(target_inventory)
        update.message.reply_text(inventory_message)

    # Удаление предмета "Detective" из инвентаря пользователя-детектива
    data[detective_id]['inventory'].remove('Detective')
    save_data(data)

# Функция для команды /банк
def bank(update, context):
    data = load_data()  # Предположим, что у вас есть функция load_data для загрузки данных о пользователях
    total_coins = sum(user_data['coins'] for user_data in data.values())
    update.message.reply_text(f"Общее количество монет в банке: {total_coins}")
    
#Хелп 
def help_command(update, context):
    help_text = """
    Доступные команды:
    /help - Показать список доступных команд
    /reg <никнейм> - Регистрация в игре
    /rating -Показать рейтинг по монетам.
    /mining- Получить 100 монет,Кулдаун 1час
    /hunt - Использовать нож и получить монеты с шансон 10-30 монет
    /shop - Показать магазин
    /inventory - Показать инвентарь
    
    /detective <никнейм> - Просмотр инвентаря другого пользователя
    /give <предмет> <никнейм> - Передача предмета другому пользователю
    /rob <никнейм> - Ограбление другого пользователя
    /give <Предмет> <никнейм>- Передать предмет другому
    /transfer <количество монет> <никнейм>-Передать монеты.
    /sell <Предмет> - Позволяет продать предмет (Комиссия 10%)
    """
    update.message.reply_text(help_text)

# Функция для команды /delete_item
def delete_item(update, context):
    # Получение id администратора
    admin_id = str(update.message.from_user.id)

    # Проверка, является ли пользователь администратором
    if admin_id != ADMIN_ID:
        update.message.reply_text("У вас нет прав на выполнение этой команды.")
        return

    try:
        # Извлечение аргументов команды
        target_nickname, item_to_delete = context.args
    except ValueError:
        update.message.reply_text("Используйте команду в формате: /delete_item <никнейм> <предмет>")
        return

    # Загрузка данных о пользователях
    data = load_data()

    # Поиск пользователя по никнейму
    target_id = None
    for user_id, user_data in data.items():
        if user_data.get("nickname") == target_nickname:
            target_id = user_id
            break

    # Проверка, найден ли пользователь
    if not target_id:
        update.message.reply_text("Пользователь не найден.")
        return

    # Проверка наличия предмета в инвентаре пользователя
    if item_to_delete not in data[target_id].get('inventory', []):
        update.message.reply_text(f"У пользователя @{target_nickname} нет предмета '{item_to_delete}' в инвентаре.")
        return

    # Удаление предмета из инвентаря пользователя
    data[target_id]['inventory'].remove(item_to_delete)

    # Сохранение обновленных данных
    save_data(data)

    update.message.reply_text(f"Предмет '{item_to_delete}' успешно удален из инвентаря пользователя @{target_nickname}.")
