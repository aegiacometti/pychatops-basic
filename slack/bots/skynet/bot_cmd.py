import subprocess
from slack.common import bot_ops, log_ops, slack_ops

from os import path


def command_syntax():
    return '@Bot-Skynet bot.cmd _bot_name_ start/stop/restart/status'


def command_help():
    return 'Command \"bot.cmd\" help\n' \
           '**********************\n' \
           'Start, stop, restart and view de status of a bot.\n' \
           'Example:\n' \
           ' - @Bot-Skynet bot.cmd bot-ad start/stop/restart/status'


def run(**kwargs):
    script_name = path.basename(__file__)
    command_splited = kwargs['command_splited']
    slack_client = kwargs['slack_client']
    channel = kwargs['channel']

    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                    cmd=kwargs['command'], auth='Approved', status='Ok', result='Starting')

    if len(command_splited) == 3:
        bot_name = command_splited[1]
        valid_bot = bot_ops.verify_bot(kwargs['bots_directory'], bot_name)
        if valid_bot:
            request = command_splited[2].lower()

            if request in ['start', 'stop', 'restart', 'status']:

                cmd = 'sudo /usr/sbin/service slack-{} {}'.format(bot_name, request)
                log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                                bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel,
                                username=kwargs['username'],
                                cmd=kwargs['command'], auth='Approved', status='Ok', result='Running')
                output_cmd = subprocess.Popen(cmd, shell=True, universal_newlines=True,
                                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = output_cmd.communicate()

                if request in ['start', 'stop', 'restart']:
                    cmd = 'sudo /usr/sbin/service slack-{} {}'.format(bot_name, 'status')
                    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel,
                                    username=kwargs['username'],
                                    cmd=kwargs['command'], auth='Approved', status='Ok', result='Checking')
                    output_cmd = subprocess.Popen(cmd, shell=True, universal_newlines=True,
                                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = output_cmd.communicate()

                output_text = stderr + "\n" + stdout
                log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                                bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel,
                                username=kwargs['username'],
                                cmd=kwargs['command'], auth='Approved', status='Ok', result='Finished')
                slack_ops.send_msg(slack_client, channel, output_text, kwargs['bot_name'])

            else:
                slack_ops.send_msg(slack_client, channel, "`Invalid Request`", kwargs['bot_name'])
                log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                                bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel,
                                username=kwargs['username'],
                                cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Request')

        else:
            slack_ops.send_msg(slack_client, channel, "`Invalid bot name`", kwargs['bot_name'])
            log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                            bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                            cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Bot Name')

    else:
        slack_ops.send_msg(slack_client, channel, "`Invalid Syntax`", kwargs['bot_name'])
        log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                        bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                        cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Syntax')
