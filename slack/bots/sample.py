# import common modules
from common import ansible_ops
from common import slack_ops


def command_syntax():
    return 'Basic command syntax\n'


def command_help():
    return 'Detailed command help'


def run(**kwargs):
    valid_command = #your_custom_logic
    if valid_command:
        ansible_ops.ansible_cmd()  #(your_parameters)

    else:
        slack_ops.send_msg()  #(your_parameters + response "`Invalid Command`")



