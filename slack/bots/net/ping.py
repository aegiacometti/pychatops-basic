from os import path

from pychatops.slack.common import ansible_ops
from pychatops.slack.common import log_ops
from pychatops.slack.common import slack_ops
from pychatops.slack.common import validate_hosts_ops


def command_syntax():
    return '@Bot-Net ping _source_device_ destination_ip_address_'


def command_help():
    return 'Command \"ping\" help\n' \
           '*******************\n' \
           'Test ICMP connectivity between the _source_device_ and the _destination_ip_address_.\n' \
           'The _source_device_ must be the name of the device according the inventory.\n' \
           'If you don\'t know the exact name, you can display the list of devices with the command \"Bot-Net ' \
           'show.inventory\" \n' \
           'Optionally you can add the number of probes to send. Default is 4, maximum is 100.' \
           'Example:\n' \
           ' - @Bot-Net ping hq-core 8.8.8.8 -> will display the ping executed from hq-core to 8.8.8.8\n' \
           ' - @Bot-Net ping hq-core 8.8.8.8 50 -> will display the ping executed from hq-core to 8.8.8.8 50\n' \
           ' - @Bot-Net show.inventory -> will display the list of network devices'


def run(**kwargs):
    script_name = path.basename(__file__)
    command_splited = kwargs['command_splited']
    slack_client = kwargs['slack_client']
    channel = kwargs['channel']

    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                    cmd=kwargs['command'], auth='Approved', status='Ok', result='Starting')

    if 3 <= len(command_splited) <= 4:
        source = validate_hosts_ops.verify_source_in_inventory(command_splited[1])

        if source:
            destination = validate_hosts_ops.verify_host_address(command_splited[2])
            if not destination:
                _, destination = validate_hosts_ops.verify_destination_ip_in_inventory(command_splited[2])
                if len(destination) != 0:
                    destination = list(destination)[0]

            if destination:
                count = 4
                if len(command_splited) == 4 and command_splited[3] <= 100:
                    count = command_splited[3]

                playbook = "net-ping-msg-slack.yml"

                bot_playbooks_directory = kwargs['bot_playbooks_directory']
                playbook_full_path = bot_playbooks_directory + playbook
                json = False

                ansible_common_inventory_full_path_name = kwargs['ansible_common_inventory_full_path_name']

                ansible_ops.ansible_cmd(json, playbook_full_path, ansible_common_inventory_full_path_name, channel,
                                        slack_client, kwargs['username'], kwargs['bot_name'],
                                        kwargs['bot_cmd_log_file'],
                                        source=source, destination=destination,
                                        count=count)

            else:
                slack_ops.send_msg(slack_client, channel, "`Invalid Destination`", kwargs['bot_name'])
                log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                                bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel,
                                username=kwargs['username'],
                                cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Destination')

        else:
            slack_ops.send_msg(slack_client, channel, "`Invalid Source`", kwargs['bot_name'])
            log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                            bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                            cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Source')

    else:
        slack_ops.send_msg(slack_client, channel, "`Invalid Syntax`", kwargs['bot_name'])
        log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                        bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                        cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Syntax')
