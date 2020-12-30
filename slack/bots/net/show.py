from os import path

from pychatops.slack.common import ansible_ops
from pychatops.slack.common import log_ops
from pychatops.slack.common import slack_ops
from pychatops.slack.common import validate_hosts_ops


def command_syntax():
    return '@Bot-Net show _device_ \"_command_\"'


def command_help():
    return 'Command \"show\" help\n' \
           '*******************\n' \
           'Execute a show command on the specified device.\n' \
           'Example:\n' \
           ' - @Bot-Net show hq-core-1 "show ip arp" -> will display the ARP table'


def run(**kwargs):
    script_name = path.basename(__file__)
    command_splited = kwargs['command_splited']
    slack_client = kwargs['slack_client']
    channel = kwargs['channel']

    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                    cmd=kwargs['command'], auth='Approved', status='Ok', result='Starting')

    if len(command_splited) >= 3 and str(command_splited[-1]).endswith("\"") and\
            str(command_splited[2]).startswith("\""):
        source = command_splited[1]
        valid_source = validate_hosts_ops.verify_source_in_inventory(source)

        if valid_source:
            join_cmd = command_splited[2:]
            pre_cmd = ""
            for item in join_cmd:
                pre_cmd += item + " "
            final_cmd = pre_cmd[1:-2]

            if len(final_cmd) < 51:
                if final_cmd.startswith("sh"):
                    playbook = "net-ios-show-msg-slack.yml"

                    bot_playbooks_directory = kwargs['bot_playbooks_directory']
                    playbook_full_path = bot_playbooks_directory + playbook
                    ansible_common_inventory_full_path_name = kwargs['ansible_common_inventory_full_path_name']

                    json = True

                    ansible_ops.ansible_cmd(json, playbook_full_path, ansible_common_inventory_full_path_name, channel,
                                            slack_client, kwargs['username'], kwargs['bot_name'],
                                            kwargs['bot_cmd_log_file'],
                                            source=source, cmd=final_cmd)
            else:
                slack_ops.send_msg(slack_client, channel, "`Command too long, max. 50 characters`", kwargs['bot_name'])
                log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                                bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel,
                                username=kwargs['username'],
                                cmd=kwargs['command'], auth='Approved', status='Failed',
                                result='Command too long, max. 50 characters')
        else:
            slack_ops.send_msg(slack_client, channel, "`Invalid Device`", kwargs['bot_name'])
            log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                            bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                            cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Device')

    else:
        slack_ops.send_msg(slack_client, channel, "`Invalid Syntax`", kwargs['bot_name'])
        log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                        bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                        cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Syntax')
