import ast
import configparser
import os
import sys

from pychatops.slack.common import log_ops
from pychatops.slack.common import slack_ops
from slackclient import SlackClient

script_name = os.path.basename(__file__)

# print("sys.argv= " + str(sys.argv))

source = sys.argv[1]
output = sys.argv[2]
ip_address = sys.argv[3]
object_group = sys.argv[4]
channel = sys.argv[5]
username = sys.argv[6]
bot_name = sys.argv[7]
task_id = sys.argv[8]

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
    print('yes')
else:
    if 'msg' in output_dict:
        text = "`Error2: connection to device \"{}\" failed`".format(source)
        status = 'Failed'
        result = text
        print('yes')
    else:
        text = "Device \"{}\"".format(source)
        ip_host_mask = ip_address.split()[1] + " 255.255.255.255"
        if ip_address in output.lower() or ip_host_mask in output.lower():
            print('yes')
            text += " - IP " + ip_address + " already in group \"" + object_group + "\""
            text = "`" + text + "`"
            status = 'Already'
            result = 'Parsed'
        else:
            print('no')
            status = 'Ok'
            result = 'Parsed'
            text = "Adding to object group"

if status == 'Failed' or status == 'Already':
    slack_ops.send_msg(slack_client, channel, text, bot_name)

print("Text= " + text)
log_ops.log_msg(bot_name=bot_name, script_name=script_name,
                bot_cmd_log_file=bot_cmd_log_file, channel=channel, username=username,
                cmd=sys.argv[0], auth='Approved', status=status, result=result, task_id=task_id)
