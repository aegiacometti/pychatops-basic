from slack.common import log_ops, slack_ops
from os import path


def command_syntax():
    return '@Bot-Skynet help'


def command_help():
    return 'Command \"help\" usage\n' \
           '********************\n' \
           'By using only the word \"help\" you can get the list of available commands.\n' \
           'Later, by using the word \"help\" and adding the name of a command, you will get the help about that' \
           'specific command.\nExamples:\n' \
           ' - @Bot-Skynet help -> to get the list of commands\n' \
           ' - @Bot-Skynet help bot.log -> to get the help about the command \"log\"'


def run(**kwargs):
    script_name = path.basename(__file__)
    discovered_plugins = kwargs['discovered_plugins']
    command_splited = kwargs['command_splited']
    slack_client = kwargs['slack_client']
    channel = kwargs['channel']

    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                    cmd=kwargs['command'], auth='Approved', status='Ok', result='Starting')

    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                    cmd=kwargs['command'], auth='Approved', status='Ok', result='Running')

    if len(command_splited) == 1:
        response = "```This is the available list of commands:\n"
        for cmd_syntax in discovered_plugins.values():
            response += "- " + cmd_syntax.command_syntax() + "\n"
        response += "```"

    elif command_splited[1].replace(".", "_") not in discovered_plugins.keys():
        response = "`The command \"{}\" don't exists`".format(command_splited[1])
        slack_ops.send_msg(slack_client, channel, response, kwargs['bot_name'])
        log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                        bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                        cmd=kwargs['command'], auth='Approved', status='Failed', result=response)
        return

    else:
        response = "```" + discovered_plugins[command_splited[1].replace('.', '_')].command_help() + "```"

    slack_ops.send_msg(slack_client, channel, response, kwargs['bot_name'])
    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                    cmd=kwargs['command'], auth='Approved', status='Ok', result='Finished')
