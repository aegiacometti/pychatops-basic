import os


def verify_bot(bots_directory, bot_name):
    bot_list = list_bots(bots_directory)
    return bot_name in bot_list


def list_bots(bots_directory):
    bot_list = []
    directories = os.listdir(bots_directory)
    for item in directories:
        if os.path.isdir(bots_directory + item):
            bot_full_name = "bot-" + item
            bot_list.append(bot_full_name)
    return bot_list
