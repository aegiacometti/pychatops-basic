# by now this is only a stopper for too many ansible/salt tasks currently running and without memory to queue tasks.
# In the future it should be a real scheduler which receives and run tasks from all the bots and queue them if
# they must be delayed because of too many tasks already running. Or not, beause on the other hand could be useful
# to avoid a queue attack/lockdown/DoS

import configparser
import os

import psutil

# PREVIOUSLY SETUP THE OPERATING SYSTEM ENVIRONMENT VALUE "NETOR" AT OS LEVEL, NET HERE
_PYCHATOPS_HOME_DIRECTORY = os.getenv('PYCHATOPS')

pychatops_config_path_name = _PYCHATOPS_HOME_DIRECTORY + "pychatops.config"
config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
config.read(pychatops_config_path_name)
allowed_processes_to_run = config['Pychatops']['allowed_processes_to_run']


def go(process_name):
    count = 0

    for process in psutil.process_iter(["name", "exe", "cmdline"]):
        for item in process.info['cmdline']:
            if process_name in item:
                count += 1

    max_allowed_processes = int(allowed_processes_to_run)
    return count <= max_allowed_processes
