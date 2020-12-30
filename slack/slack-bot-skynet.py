#!/usr/bin/python3
# -*- coding: iso-8859-15 -*-

from pychatops.slack.common import bot

# Update bot name to identify parameters in the configuration file "netor.conf"
_BOT_NAME = 'skynet'

if __name__ == "__main__":
    bot.start(bot_name=str(_BOT_NAME).upper())

