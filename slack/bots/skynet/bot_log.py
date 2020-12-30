from slack.common import bot_ops, log_ops, slack_ops
import subprocess
from os import path


def command_syntax():
    return '@Bot-Skynet bot.log _bot_name_'


def command_help():
    return 'Command \"bot.log\" help\n' \
           '***********************\n' \
           'View the log file of a Bot.\n' \
           'Specify number of lines to display. Maximum 2000, default 400.\n' \
           'Example:\n' \
           ' - @Bot-Skynet bot.log ad -> will display the last 400 lines\n' \
           ' - @Bot-Skynet bot.log ad 600 -> will display the last 600 lines'


def run(**kwargs):
    script_name = path.basename(__file__)
    command_splited = kwargs['command_splited']
    slack_client = kwargs['slack_client']
    channel = kwargs['channel']
    lines = "400"
    bot_log_file_name = 'slack-{}.log'.format(command_splited[1].lower())
    log_file = kwargs['netorchestra_home_directory'] + 'log/{}'.format(bot_log_file_name)

    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                    cmd=kwargs['command'], auth='Approved', status='Ok', result='Starting')

    if 2 <= len(command_splited) <= 3:

        bot_name = command_splited[1]
        valid_bot = bot_ops.verify_bot(kwargs['bots_directory'], bot_name)

        if valid_bot:
            if len(command_splited) == 3:
                if command_splited[2] < "2001":
                    lines = command_splited[2]

                    cmd = 'tail -n {} {}'.format(lines, log_file)
                    slack_ops.send_msg(slack_client, channel, "```Executing command```", kwargs['bot_name'])
                    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel,
                                    username=kwargs['username'],
                                    cmd=kwargs['command'], auth='Approved', status='Ok', result='Running')

                    output = subprocess.run(cmd, shell=True, universal_newlines=True,
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    output_text = output.stderr + "\n" + output.stdout
                    slack_ops.send_msg(slack_client, channel, output_text, kwargs['bot_name'])
                    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel,
                                    username=kwargs['username'],
                                    cmd=kwargs['command'], auth='Approved', status='Ok', result='Finished')

                else:
                    log_ops.log_msg("CMD= " + str(command_splited))
                    slack_ops.send_msg(slack_client, channel, "`Too many lines requested, Max 2000`",
                                       kwargs['bot_name'])
                    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel,
                                    username=kwargs['username'], cmd=kwargs['command'], auth='Approved',
                                    status='Failed', result='Too many lines requested, Max 2000')

            else:
                cmd = 'tail -n {} {}'.format(lines, log_file)
                slack_ops.send_msg(slack_client, channel, "```Executing command```", kwargs['bot_name'])
                log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                                bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel,
                                username=kwargs['username'],
                                cmd=kwargs['command'], auth='Approved', status='Ok', result='Running')

                output = subprocess.run(cmd, shell=True, universal_newlines=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output_text = output.stderr + "\n" + output.stdout
                slack_ops.send_msg(slack_client, channel, output_text, kwargs['bot_name'])
                log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                                bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel,
                                username=kwargs['username'],
                                cmd=kwargs['command'], auth='Approved', status='Ok', result='Finished')

        else:
            slack_ops.send_msg(slack_client, channel, "`Invalid Bot Name`", kwargs['bot_name'])
            log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                            bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                            cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Bot Name')

    else:
        slack_ops.send_msg(slack_client, channel, "`Invalid Syntax`", kwargs['bot_name'])
        log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                        bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                        cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Syntax')
