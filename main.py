from telegram.ext import Updater, CommandHandler
from handlers import (register, rating, mining, transfer_coins, balance, shop, buy, 
                        inventory, rob, give_item, detective, help_command, bank, 
                        delete_item, all_users, send_message_to_all_users, 
                        send_coins_to_all_users, hunt, sell_item)

def main():
    updater = Updater("TOKEN", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("reg", register))
    dp.add_handler(CommandHandler("rating", rating))
    dp.add_handler(CommandHandler("mining", mining))
    dp.add_handler(CommandHandler("transfer", transfer_coins))
    dp.add_handler(CommandHandler("balance", balance))
    dp.add_handler(CommandHandler("shop", shop))
    dp.add_handler(CommandHandler("buy", buy))
    dp.add_handler(CommandHandler("inventory", inventory))
    dp.add_handler(CommandHandler("rob", rob))
    dp.add_handler(CommandHandler("give", give_item))
    dp.add_handler(CommandHandler("detective", detective))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("bank", bank))
    dp.add_handler(CommandHandler("delete_item", delete_item))
    dp.add_handler(CommandHandler("all_user", all_users))
    dp.add_handler(CommandHandler("send", send_message_to_all_users))
    dp.add_handler(CommandHandler("send_all", send_coins_to_all_users))
    dp.add_handler(CommandHandler("hunt", hunt))
    dp.add_handler(CommandHandler("start", help_command))
    dp.add_handler(CommandHandler("sell", sell_item))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()