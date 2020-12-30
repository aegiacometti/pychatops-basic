from os import path

from pychatops.slack.common import ansible_ops
from pychatops.slack.common import log_ops
from pychatops.slack.common import slack_ops
from pychatops.slack.common import validate_hosts_ops
import ipaddress

def command_syntax():
    return '@botnet unblock.ip _ip_address_ _mask_(optional)'


def command_help():
    return 'Command \"unblock.ip\" help\n' \
           '***********************\n' \
           'UNblock an IP Address in the infrastructure firewalls.\n' \
           'Commonly used for stopping the spread of a new virus or similar use, in this case is to remove that block.\n' \
           'The specified IP will be removed from the \"blacklist\" group.\n' \
           'Optionally you can add the network mask in decimal format (24 to 31).\n' \
           'Example:\n' \
           ' - @botnet unblock.ip 10.1.1.1 -> will unblock the IP in all firewalls \n' \
           ' - @botnet unblock.ip 10.1.1.0 24 -> will unblock the subnet 10.1.1.0/24 in all firewalls'


def run(**kwargs):
    script_name = path.basename(__file__)
    command_splited = kwargs['command_splited']
    slack_client = kwargs['slack_client']
    channel = kwargs['channel']

    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                    cmd=kwargs['command'], auth='Approved', status='Ok', result='Starting')

    if 2 <= len(command_splited) <= 3:

        ip = command_splited[1]
        valid_ip = validate_hosts_ops.verify_host_address(ip)
        ip_text = ''

        if valid_ip:
            if len(command_splited) == 3:
                if command_splited[2].isnumeric():
                    if 24 <= int(command_splited[2]) <= 31:
                        ip_data = ipaddress.ip_network(valid_ip + "/" + command_splited[2], strict=False)
                        ip_data = ip_data.with_netmask
                        ip_data = str(ip_data)
                        ip_data = ip_data.split('/')
                        valid_subnet = True
                        ip_text = ip_data[0] + " " + ip_data[1]

                    else:
                        valid_subnet = False

                else:
                    valid_subnet = False

            else:
                ip_text = "host " + valid_ip
                valid_subnet = True

            if valid_ip and valid_subnet:

                playbook = "net-asa-no-obj-grp-msg-slack.yml"

                bot_playbooks_directory = kwargs['bot_playbooks_directory']
                playbook_full_path = bot_playbooks_directory + playbook
                json = True

                source = 'all'
                ip_address = ip_text
                object_group = "blacklist"

                ansible_common_inventory_full_path_name = kwargs['ansible_common_inventory_full_path_name']

                ansible_ops.ansible_cmd(json, playbook_full_path, ansible_common_inventory_full_path_name, channel,
                                        slack_client, kwargs['username'], kwargs['bot_name'], kwargs['bot_cmd_log_file'],
                                        ip_address=ip_address, object_group=object_group, source=source, function='remove')

            else:
                slack_ops.send_msg(slack_client, channel, "`Invalid Subnet`", kwargs['bot_name'])
                log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                                bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                                cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Subnet')

        else:
            slack_ops.send_msg(slack_client, channel, "`Invalid IP address`", kwargs['bot_name'])
            log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                            bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                            cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid IP address')
    else:
        slack_ops.send_msg(slack_client, channel, "`Invalid Syntax. Try \"@botnet help block.ip\"`", kwargs['bot_name'])
        log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                        bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                        cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Syntax')
