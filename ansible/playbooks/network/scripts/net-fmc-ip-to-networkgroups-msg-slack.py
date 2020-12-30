import configparser
import json
import os
import sys

import fmcapi
from ansible_vault import Vault
from slackclient import SlackClient
from pychatops.slack.common import log_ops
from pychatops.slack.common import slack_ops
import netaddr

script_name = os.path.basename(__file__)
config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
_PYCHATOPS_HOME_DIRECTORY = os.getenv('PYCHATOPS')
pychatops_config_path_name = _PYCHATOPS_HOME_DIRECTORY + "pychatops.config"
config.read(pychatops_config_path_name)
bot_net_oauth_token = config['Slack']['bot_net_oauth']
bot_cmd_log_file = config['Slack']['bot_net_cmd_log']
slack_client = SlackClient(bot_net_oauth_token)
ansible_vault_file = config['Ansible']['ansible_vault_file']

# print("sys.argv= " + str(sys.argv))

source = sys.argv[1]
host = sys.argv[2]
function = sys.argv[3]
network_group = sys.argv[4].capitalize()
ip_address = sys.argv[5]
channel = sys.argv[6]
username = sys.argv[7]
bot_name = sys.argv[8]
task_id = sys.argv[9]

ip_address = ip_address.replace('host ', '')
ip_address = ip_address.split(' ')
if len(ip_address) != 1:
    ip_address = ip_address[0] + "/" + str(netaddr.IPAddress(ip_address[1]).netmask_bits())
else:
    ip_address = ip_address[0]

read_file = open(ansible_vault_file, 'r')
vault_file_content = read_file.read().strip()
read_file.close()

vault = Vault(vault_file_content)
secrets = vault.load(open(_PYCHATOPS_HOME_DIRECTORY + 'devices/group_vars/fmc').read())


def search(resp, ipa):
    if 'literals' in resp:
        for item in resp['literals']:
            if item['value'] == ipa:
                return True
    if 'objects' in resp:
        ipa = ipa.replace('/', '_')
        for item in resp['objects']:
            if item['name'] == ipa:
                return True


def main():
    text = "Device \"{}\"".format(source)
    status = 'Ok'
    result = 'Executed'

    if function == 'list':
        with fmcapi.FMC(host=host, username=secrets['ansible_user'], password=secrets['ansible_password'],
                        autodeploy=True) as fmc:
            obj1 = fmcapi.NetworkGroups(fmc=fmc, name=network_group)
            response = obj1.get()
            if 'id' not in response.keys():
                print('Failed Object Group \"{}\" does not exist'.format(network_group))
            else:
                print('Object Group \"{}\" Found'.format(network_group))
                print(json.dumps(response))

    elif function == 'add':
        with fmcapi.FMC(host=host, username=secrets['ansible_user'], password=secrets['ansible_password'], autodeploy=False) as fmc:
            obj1 = fmcapi.NetworkGroups(fmc=fmc, name=network_group)
            response = obj1.get()
            #print(json.dumps(obj1.format_data()))

            if 'id' not in response.keys():
                text += ' - Object Group \"{}\" not found'.format(network_group)
                text = "`" + text + "`"

            else:
                present = search(response, ip_address)
                if not present:
                    obj1.unnamed_networks(action='add', value=ip_address)
                    print('Adding IP \"{}\" to object group \"{}\"'.format(ip_address, network_group))
                    response = obj1.put()
                    #print(response)
                    if response:
                        print('Verifying add IP \"{}\" to object group \"{}\"'.format(ip_address, network_group))
                        response = obj1.get()
                        present = search(response, ip_address)

                        if present:
                            text += ' - IP \"{}\" added to \"{}\"'.format(ip_address, network_group)
                            text = "```" + text + "```"

                        else:
                            text += ' Failed to add IP \"{}\" to \"{}\"'.format(ip_address, network_group)
                            text = "`" + text + "`"

                    else:
                        text += ' Failed to add IP \"{}\" to \"{}\"'.format(ip_address, network_group)
                        text = "`" + text + "`"

                else:
                    text += ' - IP \"{}\" already exist in \"{}\"'.format(ip_address, network_group)
                    text = "`" + text + "`"

    elif function == 'remove':
        with fmcapi.FMC(host=host, username=secrets['ansible_user'], password=secrets['ansible_password'],
                        autodeploy=True) as fmc:
            obj1 = fmcapi.NetworkGroups(fmc=fmc, name=network_group)
            response = obj1.get()
            #print(json.dumps(obj1.format_data()))

            if 'id' not in response.keys():
                text += ' - Object Group \"{}\" not found'.format(network_group)
                text = "`" + text + "`"

            else:
                present = search(response, ip_address)

                if not present:
                    text += ' - IP \"{}\" not in \"{}\"'.format(ip_address, network_group)
                    text = "`" + text + "`"

                else:
                    obj1.unnamed_networks(action='remove', value=ip_address)
                    print('Removing IP \"{}\" to object group \"{}\"'.format(ip_address, network_group))
                    response = obj1.put()
                    #print(response)

                    if response:
                        #print(json.dumps(obj1.format_data()))
                        print('Verifying removal IP \"{}\" to object group \"{}\"'.format(ip_address, network_group))
                        response = obj1.get()
                        present = search(response, ip_address)

                        if not present:
                            text += ' - IP \"{}\" removed from \"{}\"'.format(ip_address, network_group)
                            text = "```" + text + "```"

                        else:
                            text += ' - Failed to remove IP \"{}\" from \"{}\"'.format(ip_address, network_group)
                            text = "`" + text + "`"

                    else:
                        text += ' - Failed to remove IP \"{}\" from \"{}\"'.format(ip_address, network_group)
                        text = "`" + text + "`"

    else:
        print('Invalid option')

    slack_ops.send_msg(slack_client, channel, text, bot_name)
    print("Text= " + text)
    log_ops.log_msg(bot_name=bot_name, script_name=script_name,
                    bot_cmd_log_file=bot_cmd_log_file, channel=channel, username=username,
                    cmd=sys.argv[0], auth='Approved', status=status, result=result, task_id=task_id)

if __name__ == "__main__":
    #function = 'add'
    #ip_address = '10.10.21.11'
    #network_group = 'blacklist'
    main()
