from slack.common import bot_ops, log_ops, slack_ops
from os import path


def command_syntax():
    return '@Bot-Skynet bot.list'


def command_help():
    return 'Command \"bot.list\" help\n' \
           '***************************\n' \
           'List the available bots in the system.\n' \
           'Example:\n' \
           ' - @Bot-Skynet bot.list -> will display the list of bots'


def run(**kwargs):
    script_name = path.basename(__file__)
    command_splited = kwargs['command_splited']
    slack_client = kwargs['slack_client']
    channel = kwargs['channel']

    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                    cmd=kwargs['command'], auth='Approved', status='Ok', result='Starting')

    if len(command_splited) == 1:
        bot_list = bot_ops.list_bots(kwargs['bots_directory'])

        log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                        bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                        cmd=kwargs['command'], auth='Approved', status='Ok', result='Running')
        text = "List of available Bots:\n"
        text += "*******************\n"
        for item in bot_list:
            text += "- @" + str(item).upper() + "\n"
        slack_ops.send_msg(slack_client, channel, "```" + text + "```", kwargs['bot_name'])
        log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                        bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                        cmd=kwargs['command'], auth='Approved', status='Ok', result='Finished')

    else:
        slack_ops.send_msg(slack_client, channel, "`Invalid Syntax`", kwargs['bot_name'])
        log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                        bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                        cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Syntax')
