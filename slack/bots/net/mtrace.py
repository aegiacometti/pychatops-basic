import re
from os import path

from pychatops.slack.common import ansible_ops
from pychatops.slack.common import log_ops
from pychatops.slack.common import slack_ops
from pychatops.slack.common import validate_hosts_ops


def command_syntax():
    return '@Bot-Net mtrace src=_csv_device_list_ dst=_destination_'


def command_help():
    return 'Command \"mtrace\" help\n' \
           '*********************\n' \
           'Execute a multiple source and destination trace route command on the devices.\n' \
           'Source and destination must be expresed as csv.\n' \
           'It support inventory device name and groups.\n' \
           'Example:\n' \
           ' - @Bot-Net show.inventory -> will display the inventory\n' \
           ' - @Bot-Net mshow src=hq-core,network dst=isp-internet,windows -> will display traceroute'


def run(**kwargs):
    script_name = path.basename(__file__)
    command_splited = kwargs['command_splited']
    slack_client = kwargs['slack_client']
    channel = kwargs['channel']

    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                    cmd=kwargs['command'], auth='Approved', status='Ok', result='Starting')

    if len(command_splited) >= 3:
        sources = re.search(r'src=(.*)', command_splited[1])
        destinations = re.search(r'dst=(.*)', command_splited[2])

        if sources and destinations:
            list_sources, sources_count, list_destinations, destinations_count =\
                validate_hosts_ops.identify_elements(sources[1], destinations[1])

            total = sources_count * destinations_count

            if sources_count != 0 and destinations_count != 0:

                if total <= int(kwargs['multiple_src_dst']):

                    playbook = "net-mtrace-msg-slack.yml"

                    bot_playbooks_directory = kwargs['bot_playbooks_directory']
                    playbook_full_path = bot_playbooks_directory + playbook
                    ansible_common_inventory_full_path_name = kwargs['ansible_common_inventory_full_path_name']

                    json = True

                    if destinations_count == 1:

                        ansible_ops.ansible_cmd(json, playbook_full_path, ansible_common_inventory_full_path_name,
                                                channel, slack_client, kwargs['username'], kwargs['bot_name'],
                                                kwargs['bot_cmd_log_file'],
                                                source=list(list_sources),
                                                destination=list(list_destinations)[0])

                    else:
                        for item in list_destinations:
                            ansible_ops.ansible_cmd(json, playbook_full_path, ansible_common_inventory_full_path_name,
                                                    channel, slack_client, kwargs['username'], kwargs['bot_name'],
                                                    kwargs['bot_cmd_log_file'],
                                                    source=list(list_sources),
                                                    destination=item)

                else:
                    slack_ops.send_msg(slack_client, channel, "`Too many operations. Max {}`".format(kwargs['multiple_src_dst']), kwargs['bot_name'])
                    log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                                    bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel,
                                    username=kwargs['username'],
                                    cmd=kwargs['command'], auth='Approved', status='Failed',
                                    result='Too many operations. Max {}'.format(kwargs['multiple_src_dst']))

            else:
                slack_ops.send_msg(slack_client, channel, "`Invalid sources or destinations`", kwargs['bot_name'])
                log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                                bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel,
                                username=kwargs['username'],
                                cmd=kwargs['command'], auth='Approved', status='Failed',
                                result='Invalid sources or destinations')

        else:
            slack_ops.send_msg(slack_client, channel, "`Invalid Devices`", kwargs['bot_name'])
            log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                            bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                            cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Devices')

    else:
        slack_ops.send_msg(slack_client, channel, "`Invalid Syntax`", kwargs['bot_name'])
        log_ops.log_msg(bot_name=kwargs['bot_name'], script_name=script_name,
                        bot_cmd_log_file=kwargs['bot_cmd_log_file'], channel=channel, username=kwargs['username'],
                        cmd=kwargs['command'], auth='Approved', status='Failed', result='Invalid Syntax')
