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

output = sys.argv[1]
source_hostname = sys.argv[2]
source_ip = sys.argv[3]
destination = sys.argv[4]
channel = sys.argv[5]
username = sys.argv[6]
bot_name = sys.argv[7]
task_id = sys.argv[8]
status = 'Ok'
result = 'Parsed'

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
_PYCHATOPS_HOME_DIR = os.getenv('PYCHATOPS')
pychatops_config_path_name = _PYCHATOPS_HOME_DIR + "pychatops.config"
config.read(pychatops_config_path_name)
bot_net_oauth_token = config['Slack']['bot_' + bot_name + '_oauth']
bot_cmd_log_file = config['Slack']['bot_' + bot_name + '_cmd_log']
slack_client = SlackClient(bot_net_oauth_token)

try:
    output_dict = ast.literal_eval(output)
except ValueError:
    text = "`Error1: the playbook returned invalid information format`"
    status = 'Failed'
    result = text
else:
    for item in output_dict['results']:

        if 'msg' in item and 'packet_loss' not in item:
            text = "`Error2: {} - {}`".format(source_hostname, item['msg'])
            status = 'Failed'
            result = text
        else:
            command = item['commands'][0]

            ip_address = re.search(r'ping (.*) [r|c]', command)
            hostname = get_ansible_host_name(ip_address[1])
            if hostname:
                destination = hostname
            else:
                destination = ip_address[1]

            pre_text = "From {} ({}) ping to {} ({}) => Tx= {} - Rx= {} - Pkt.Loss= {} - RTT: min= {} - avg= {} - max= {}".format(
                source_hostname, source_ip, destination, ip_address[1], item['packets_tx'], item['packets_rx'],
                item['packet_loss'], item['rtt']['min'], item['rtt']['avg'], item['rtt']['max'])
            print(output_dict)

            if item['packet_loss'].strip('%')[0] == '0':
                text = "```" + pre_text + "```"
            else:
                text = "`" + pre_text + "`"

        slack_ops.send_msg(slack_client, channel, text, bot_name)
        print("Text= " + text)
        log_ops.log_msg(bot_name=bot_name, script_name=script_name,
                        bot_cmd_log_file=bot_cmd_log_file, channel=channel, username=username,
                        cmd=sys.argv[0], auth='Approved', status=status, result=result, task_id=task_id)

    sys.exit(0)

slack_ops.send_msg(slack_client, channel, text, bot_name)
print("Text= " + text)
log_ops.log_msg(bot_name=bot_name, script_name=script_name,
                bot_cmd_log_file=bot_cmd_log_file, channel=channel, username=username,
                cmd=sys.argv[0], auth='Approved', status=status, result=result, task_id=task_id)
