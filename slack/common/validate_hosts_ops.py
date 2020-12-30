import ipaddress
import os
import re

import dns.resolver
from pychatops.slack.common import log_ops
from pychatops.slack.common import slack_ops

_PYCHATOPS_HOME_DIRECTORY = os.getenv('PYCHATOPS')


def verify_source_in_inventory(source):
    with open(_PYCHATOPS_HOME_DIRECTORY + "devices/hosts", "r") as file:
        for line in file:
            match = re.search("^" + source + " ", line)
            if match:
                return source
    return False


def verify_destination_ip_in_inventory(source):
    count = 0
    hosts = set()
    with open(_PYCHATOPS_HOME_DIRECTORY + "devices/hosts", "r") as file:
        for line in file:
            host = line.split(" ")
            ansible_host = re.search(source, host[0])
            if ansible_host:
                try:
                    h = host[1].split("=")
                except IndexError:
                    pass
                else:
                    count += 1
                    hosts.add(h[1])
    return count, hosts


def fix_hostname(host):
    if "http" in host:
        host = re.search(r'\|(.*)>', host)
        return host[1]
    else:
        return host


def verify_host_address(host):
    try:
        ipaddress.ip_address(host)
    except ValueError:
        try:
            host = dns.resolver.query(fix_hostname(host))
        except dns.resolver.NXDOMAIN:
            return False
        except dns.resolver.NoNameservers:
            return False
        else:
            return host[0].to_text()
    else:
        return host


def is_ansible_group(group):
    with open(_PYCHATOPS_HOME_DIRECTORY + "devices/hosts", "r") as file:
        for line in file:
            if line.startswith("[") and line.endswith("]\n"):
                match = re.search(r'\[(.*)\]', line)
                if group == match[1]:
                    return True
    return False


def identify_ansible_groups():
    group_list = {}
    with open(_PYCHATOPS_HOME_DIRECTORY + "devices/hosts", "r") as file:
        for line in file:
            if line.startswith("[") and line.endswith("]\n"):
                match = re.search(r'\[(.*)\]', line)
                group_list[match.group(1)] = []
                continue
            ansible_host = re.search(r'(.*) ansible_host=([^\s]+)', line)
            if ansible_host:
                ip_host_ansible = get_ansible_host_ip(ansible_host[1])
                if ip_host_ansible:
                    group_list[match.group(1)].append(ip_host_ansible)
    return group_list


def get_ansible_host_ip(item):
    # i = list(item)[0]
    with open(_PYCHATOPS_HOME_DIRECTORY + "devices/hosts", "r") as file:
        for line in file:
            if item in line:
                ansible_host = re.search(r'(.*) ansible_host=([^\s]+)', line)
                return ansible_host[2]
    return False


def get_ansible_host_name(item):
    # i = list(item)[0]
    with open(_PYCHATOPS_HOME_DIRECTORY + "devices/hosts", "r") as file:
        for line in file:
            if item in line:
                ansible_host = re.search(r'(.*) ansible_host=([^\s]+)', line)
                return ansible_host[1]
    return False


def identify_elements(source_csv, destination_csv):
    group_source_list = set()
    group_destination_list = set()
    source_count = 0
    destination_count = 0

    ansible_groups = identify_ansible_groups()

    source_elements = source_csv.split(',') if ',' in source_csv else [source_csv]
    destination_elements = destination_csv.split(',') if ',' in destination_csv else [destination_csv]

    for element in source_elements:
        if element in ansible_groups.keys():
            group_source_list.add(element)
            source_count += len((ansible_groups[element]))
            continue
        ansible_host = verify_source_in_inventory(element)
        if ansible_host:
            group_source_list.add(element)
            source_count += 1

    for element in destination_elements:
        if element in ansible_groups.keys():
            for item in ansible_groups[element]:
                group_destination_list.add(item)
            destination_count += len(ansible_groups[element])
            continue
        ansible_host = verify_source_in_inventory(element)
        if ansible_host:
            ip = get_ansible_host_ip(ansible_host)
            group_destination_list.add(ip)
            destination_count += 1
            continue
        valid_host = verify_host_address(element)
        if valid_host:
            group_destination_list.add(valid_host)
            destination_count += 1

    return group_source_list, source_count, group_destination_list, destination_count


def list_inventory(slack_client, channel, string_filter, bot_cmd_log_file, username, cmd, bot_name):
    text = ""
    is_first = True
    script_name = os.path.basename(__file__)

    log_ops.log_msg(bot_name=bot_name, script_name=script_name, bot_cmd_log_file=bot_cmd_log_file,
                    channel=channel, username=username, cmd=cmd, auth='Approved', status='Ok', result='Running')

    if string_filter == '':
        text = "```"
        with open(_PYCHATOPS_HOME_DIRECTORY + "devices/hosts", "r") as file:
            for line in file:

                if '[' in line:
                    match = re.search(r'\[(.*)\]', line)
                    if match:
                        if is_first:
                            text += "\n=========================================================\n" + \
                                    "| {:<53} |".format(match.group(1).lower()) \
                                    + "\n=========================================================\n"
                            is_first = False

                        else:
                            text += "=========================================================\n" + \
                                    "\n=========================================================\n" + \
                                    "| {:<53} |".format(match.group(1).lower()) \
                                    + "\n=========================================================\n"
                match = re.search(r'(.*) ansible_host=([^\s]+)(.*)platform=([^\s]+)', line)

                if match:
                    text += '| {:<20}  | {:<18} | {:<8} |\n'.format(match[1], match[2], match[4])

        text += "=========================================================```"

    else:
        with open(_PYCHATOPS_HOME_DIRECTORY + "devices/hosts", "r") as file:
            for line in file:

                if '[' in line:
                    continue

                match_line = re.search(string_filter, line)

                if match_line:
                    match_capture_detail = re.search(r'(.*) ansible_host=([^\s]+)(.*)platform=([^\s]+)', line)

                    if match_capture_detail:
                        text += '| {:<20}  | {:<18} | {:<8} |\n'.format(match_capture_detail[1], match_capture_detail[2], match_capture_detail[4])

        text += ""

        if len(text) == 0:
            text = "`No matching devices`"
        else:
            text = "```" + text + "```"

    slack_ops.send_msg(slack_client, channel, text, bot_name)

    log_ops.log_msg(bot_name=bot_name, script_name=script_name, bot_cmd_log_file=bot_cmd_log_file,
                    channel=channel, username=username, cmd=cmd, auth='Approved', status='Ok', result='Finished')
