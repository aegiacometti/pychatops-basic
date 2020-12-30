from slackclient import SlackClient
import sys
import os
import configparser
import time
import re


config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
_NETORCHESTRA_HOME_DIRECTORY = os.getenv('NETORCHESTRA')
netorchestra_config_path_name = _NETORCHESTRA_HOME_DIRECTORY + "netorchestra.config"
config.read(netorchestra_config_path_name)
bot_name = "skynet"
bot_oauth_token = config['Slack']['bot_' + bot_name + '_oauth']
integration_tests_dir = _NETORCHESTRA_HOME_DIRECTORY + 'pychatops/slack/tests/integration/tests-OK/'
list_dir = []


def send_msg(sc, channel_sm, msg):
    sc.api_call('chat.postMessage', as_user=True, channel=channel_sm, text=msg)


def read_file(sc, channel_rf, file_name):
    delay = 60
    f = open(integration_tests_dir + file_name, 'r')
    for line in f:
        match = re.search('delay = (.*)', line)
        if match:
            delay = match.group(1)
            print("delay = " + delay)
        if line.startswith('<@'):
            send_msg(sc, channel_rf, line)
            print(line)
            time.sleep(int(delay))
    f.close()


if __name__ == "__main__":
    try:
        option = sys.argv[1]
        channel = sys.argv[2]
    except IndexError:
        print("\nInvalid syntax. Example: slack-send-test.py _file_name_or_full_ _slack_channel_to_use_for_testing_\n")
    else:
        for file in os.listdir(integration_tests_dir):
            if file.endswith(".txt"):
                list_dir.append(file)

        slack_client = SlackClient(bot_oauth_token)
        if slack_client.rtm_connect():
            print("Client connected")
            if option == 'full':
                for item in list_dir:
                    read_file(slack_client, channel, item)
            elif option in list_dir:
                read_file(slack_client, channel, option)
            else:
                print('\ninvalid test file\n')
                sys.exit(1)
        else:
            print("Connection Failed")
