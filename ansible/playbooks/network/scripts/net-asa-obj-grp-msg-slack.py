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
ip_address = sys.argv[2]
object_group = sys.argv[3]
output_add = sys.argv[4]
output_verify = sys.argv[5]
channel = sys.argv[6]
username = sys.argv[7]
bot_name = sys.argv[8]
task_id= sys.argv[9]

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
_PYCHATOPS_HOME_DIR = os.getenv('PYCHATOPS')
pychatops_config_path_name = _PYCHATOPS_HOME_DIR + "pychatops.config"
config.read(pychatops_config_path_name)
bot_net_oauth_token = config['Slack']['bot_' + bot_name + '_oauth']
bot_cmd_log_file = config['Slack']['bot_' + bot_name + '_cmd_log']
slack_client = SlackClient(bot_net_oauth_token)

try:
    output_add_dict = ast.literal_eval(output_add)
    output_verify_dict = ast.literal_eval(output_verify)
except ValueError:
    text = "`Error1: the playbook returned invalid information format`"
    status = 'Failed'
    result = text
else:
    if 'msg' in (output_add_dict or output_verify_dict):
        text = "`Error2: connection to device \"{}\" failed`".format(source)
        status = 'Failed'
        result = text
    else:
        text = "Device \"{}\"".format(source)
        if ip_address in output_verify:
            text += str(" - IP \"{}\" added OK to \"{}\"".format(ip_address, object_group))
            text = "```" + text + "```"
            status = 'Ok'
            result = 'Parsed'
        else:
            text += str(" - IP \"{}\" failed to add to \"{}\"".format(ip_address, object_group))
            text = "`" + text + "`"
            status = 'Failed'
            result = 'Parsed'

slack_ops.send_msg(slack_client, channel, text, bot_name)
print("Text= " + text)
log_ops.log_msg(bot_name=bot_name, script_name=script_name,
                bot_cmd_log_file=bot_cmd_log_file, channel=channel, username=username,
                cmd=sys.argv[0], auth='Approved', status=status, result=result, task_id=task_id)
