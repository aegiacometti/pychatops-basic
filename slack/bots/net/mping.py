import re
from os import path

from pychatops.slack.common import ansible_ops
from pychatops.slack.common import log_ops
from pychatops.slack.common import slack_ops
from pychatops.slack.common import validate_hosts_ops


def command_syntax():
    return '@Bot-Net mping src=_source_device_csv_ dst=_destination_device_csv_'


def command_help():
    return 'Command \"mping\" help\n' \
           '**************************\n' \
           'Test ICMP connectivity between multiple _source_device_ and _destination_ip_address_.\n' \
           'The _source_device_ must be the name of the device according the inventory.\n' \
           'If you don\'t know the exact name, you can display the list of devices with the command \"Bot-Net ' \
           'show.inventory\" \n' \
           '\n' \
           '* The source device/s had to be represented by:\n' \
           '- the name of the device in the inventory\n' \
           '- the group name of devices in the inventory\n' \
           '\n' \
           '* The destination device can be any format of:\n' \
           '- inventory name\n' \
           '- partial name\n' \
           '- group name\n' \
           '- hostname\n' \
           '- IP address\n' \
           '\n' \
           'In the syntaxis specify \"src=\" or \"dst=\" with a list with coma separated values.\n' \
           '\n' \
           'Optionally you can add the number of probes to send. Default is 4, maximum is at setup file.\n' \
           'Example:\n' \
           ' - @Bot-Net mping src=network,branch-lan dst=8.8.8.8,isp-internet -> will display the ping from ' \
           'all the src to all ' \
           'dst\n' \
           ' - @Bot-Net show.inventory -> will display the network devices in the inventory'


def run(**kwargs):
    script_name = path.basename(__file__)
    command_splited = kwargs['command_splited']
    slack_client = kwargs['slack_client']
    channel = kwargs['channel']

    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                    cmd=kwargs['command'], auth='Approved', status='Ok', result='Starting')

    if 3 <= len(command_splited) <= 4:

        sources = re.search(r'src=(.*)', command_splited[1])
        destinations = re.search(r'dst=(.*)', command_splited[2])

        if sources and destinations:
            list_sources, sources_count, list_destinations, destinations_count =\
                validate_hosts_ops.identify_elements(sources[1], destinations[1])
        else:
            slack_ops.send_msg(slack_client, channel, "`Invalid Syntax`", kwargs['bot_name'])
            log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                            bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                            cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Syntax')
            return

        volume = sources_count * destinations_count

        if sources_count == 0:
            slack_ops.send_msg(slack_client, channel, "`Invalid source`", kwargs['bot_name'])
            log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                            bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel,
                            username=kwargs['username'],
                            cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Sources')
            return
        if destinations_count == 0:
            slack_ops.send_msg(slack_client, channel, "`Invalid destination`", kwargs['bot_name'])
            log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                            bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel,
                            username=kwargs['username'],
                            cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid destination')
            return

        if volume > int(kwargs['multiple_src_dst']):
            slack_ops.send_msg(slack_client, channel, "`Too many combinations src/dst. Max {}`".format(kwargs['multiple_src_dst']), kwargs['bot_name'])
            log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                            bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel,
                            username=kwargs['username'],
                            cmd=kwargs['command'], auth='Approved', status='Failed',
                            result="`Too many combinations src/dst. Max {}`".format(kwargs['multiple_src_dst']))
            return

        count = 4
        if len(command_splited) == 4 and command_splited[3] <= 100:
            count = command_splited[3]

        playbook = "net-mping-msg-slack.yml"

        bot_playbooks_directory = kwargs['bot_playbooks_directory']
        playbook_full_path = bot_playbooks_directory + playbook
        json = True

        ansible_common_inventory_full_path_name = kwargs['ansible_common_inventory_full_path_name']

        ansible_ops.ansible_cmd(json, playbook_full_path, ansible_common_inventory_full_path_name, channel,
                                slack_client, kwargs['username'], kwargs['bot_name'], kwargs['bot_cmd_log_file'],
                                source=list(list_sources),
                                destination=list(list_destinations), count=count)

    else:
        slack_ops.send_msg(slack_client, channel, "`Invalid Syntax`", kwargs['bot_name'])
        log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                        bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                        cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Syntax')
