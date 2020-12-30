import subprocess
import sys
import threading
import time
from os import path
from random import randint

from pychatops.slack.common import log_ops
from pychatops.slack.common import scheduler
from pychatops.slack.common import slack_ops


class AnsibleExecThread(threading.Thread):

    def __init__(self, slack_client, channel, cmd, username, bot_name, bot_cmd_log_file, task_id):
        threading.Thread.__init__(self)
        self.slack_client = slack_client
        self.channel = channel
        self.cmd = cmd
        self.username = username
        self.bot_name = bot_name
        self.bot_cmd_log_file = bot_cmd_log_file
        self.task_id = task_id

    def run(self):
        script_name = path.basename(__file__)
        proc = subprocess.Popen(self.cmd, shell=True, stdout=sys.stdout, stderr=sys.stdout, universal_newlines=True)
        # pid = proc.pid

        slack_ops.send_msg(self.slack_client, self.channel,
                           "```Executing command - TaskID={}```".format(str(self.task_id)), self.bot_name)

        log_ops.log_msg(bot_cmd_log_file=self.bot_cmd_log_file, script_name=script_name, bot_name=self.bot_name,
                        username=self.username, channel=self.channel,
                        cmd=self.cmd, task_id=self.task_id, status="Ok", result="Running")

        while proc.poll() is None:
            time.sleep(2)

        msg = "Command finished - TaskID={}".format(str(self.task_id))
        slack_ops.send_msg(self.slack_client, self.channel, "```{}```".format(msg), self.bot_name)
        log_ops.log_msg(bot_cmd_log_file=self.bot_cmd_log_file, script_name=script_name, bot_name=self.bot_name,
                        username=self.username, channel=self.channel,
                        cmd=self.cmd, task_id=self.task_id, status="Ok", result="Finished")


def ansible_cmd(json, playbook_full_path_name, ansible_common_inventory_full_path_name, channel, slack_client,
                username, bot_name, bot_cmd_log_file, **kwargs):
    script_name = path.basename(__file__)
    cmd = "ansible-playbook " + playbook_full_path_name + \
          " -i " + ansible_common_inventory_full_path_name + " --extra-vars \""

    task_id = randint(0, 999999)

    if json:
        extra_vars_json = {key: value for key, value in kwargs.items()}
        extra_vars_json["channel"] = channel
        extra_vars_json["username"] = username
        extra_vars_json["bot_name"] = bot_name
        extra_vars_json["task_id"] = task_id
        cmd += str(extra_vars_json) + "\" -vvvv"
    else:
        for key, value in kwargs.items():
            cmd += key + "=" + str(value) + " "
        cmd += "channel=" + channel + " username=" + username + " bot_name=" + bot_name + " task_id=" + str(task_id) + "\" -vvvv"

    process_name = "ansible-playbook"

    if scheduler.go(process_name):
        thread = AnsibleExecThread(slack_client, channel, cmd, username, bot_name, bot_cmd_log_file, task_id)
        thread.start()
    else:
        msg = "Scheduler: Can't launch task, too many running, wait a couple of minutes and try again"
        slack_ops.send_msg(slack_client, channel, "```{}```".format(msg), bot_name)
        log_ops.log_msg(bot_name=bot_name, script_name=script_name, username=username, channel=channel,
                        status="Failed", result='Scheduler: Too many tasks running')
