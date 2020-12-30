import ast
import configparser
import os
import sys
import re

from slackclient import SlackClient

from pychatops.slack.common import log_ops
from pychatops.slack.common import slack_ops
from pychatops.slack.common.validate_hosts_ops import get_ansible_host_name

script_name = os.path.basename(__file__)

# print("sys.argv= " + str(sys.argv))

source = sys.argv[1]
output = sys.argv[2]
source_ip = sys.argv[3]
channel = sys.argv[4]
username = sys.argv[5]
bot_name = sys.argv[6]
task_id = sys.argv[7]
status = 'Ok'
result = 'Parsed'

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
_PYCHATOPS_HOME_DIR = os.getenv('PYCHATOPS')
pychatops_config_path_name = _PYCHATOPS_HOME_DIR + "pychatops.config"
config.read(pychatops_config_path_name)
bot_net_oauth_token = config['Slack']['bot_' + bot_name + '_oauth']
bot_cmd_log_file = config['Slack']['bot_' + bot_name + '_cmd_log']
slack_client = SlackClient(bot_net_oauth_token)

if ('timed out' in str(sys.argv)) or ('Authentication failed' in str(sys.argv)) or (
        'Unable to connect' in str(sys.argv)) or ('No authentication methods' in str(sys.argv)):
    text = "`Can't connect to source device \"{}\"`".format(source)
    status = 'Failed'
    result = text
else:
    try:
        output_dict = ast.literal_eval(output)
    except ValueError:
        text = "`Error1: the playbook returned invalid information format`"
        status = 'Failed'
        result = text
    else:
        command = str(output_dict['commands'])

        ip_address = re.search(r'ping (.*) [r|c]', command)
        hostname = get_ansible_host_name(ip_address[1])
        if hostname:
            destination = hostname
        else:
            destination = ip_address[1]

        pre_text = "From {} ({}) ping to {} ({}) => Tx= {} - Rx= {} - Pkt.Loss= {} - RTT: min= {} - avg= {} - max= {}".format(
            source, source_ip, destination, ip_address[1], output_dict['packets_tx'], output_dict['packets_rx'],
            output_dict['packet_loss'], output_dict['rtt']['min'], output_dict['rtt']['avg'], output_dict['rtt']['max'])

        if output_dict['packet_loss'].strip('%')[0] == '0':
            text = "```" + pre_text + "```"
        else:
            text = "`" + pre_text + "`"

slack_ops.send_msg(slack_client, channel, text, bot_name)
print("Text= " + text)
log_ops.log_msg(bot_name=bot_name, script_name=script_name,
                bot_cmd_log_file=bot_cmd_log_file, channel=channel, username=username,
                cmd=sys.argv[0], auth='Approved', status=status, result=result, task_id=task_id)
