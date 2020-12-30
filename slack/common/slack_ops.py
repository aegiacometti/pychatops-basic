import io
import os
import re
import time
import traceback

from pychatops.slack.common import log_ops

_MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


def parse_bot_commands(starterbot_id, slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and "subtype" not in event:
            user_id, message = parse_direct_mention(event["text"])

            # <http://quadrant.net|quadrant.net> Eliminate from messages the link format autoadded
            match = re.search(r'<(.*)\|(.*)>', message)
            if match and match[1] and match[2] and match[1].endswith(match[2]):
                message = message.replace(match[0], match[2])

            if user_id == starterbot_id:
                return message, event["channel"], str(event["user"])
    return None, None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(_MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def send_msg(slack_client, channel, response, bot_name):
    # Sends the response back to the channel
    script_name = os.path.basename(__file__)
    # noinspection PyBroadException

    if len(response) <= 3800:
        try:
            slack_client.api_call("chat.postMessage", channel=channel, text=response)
        except Exception:
            trace_string = traceback.format_exc()
            log_ops.log_msg(bot_name=bot_name, script_name=script_name, cmd='Send message to Slack', status='Failed',
                            result="Failed\n" + trace_string + "\n")
    else:
        if response.startswith('```'):
            response = response[3:-3]
            is_error = False
        else:
            response = response[1:-1]
            is_error = True

        step = 3800
        response_list = []
        for i in range(0, len(response), 3800):
            response_list.append(response[i:step])
            step += 3800

        for i in range(0, len(response_list)):
            if is_error:
                text = '`' + response_list[i] + '`'
            else:
                text = '```' + response_list[i] + '```'

            slack_client.api_call("chat.postMessage", channel=channel, text=text)

            time.sleep(1)


def send_file(slack_client, channel, filename, bot_name, title, initial_comment):
    # Sends the response back to the channel
    script_name = os.path.basename(__file__)
    # noinspection PyBroadException
    text = 'test'
    try:
        slack_client.api_call("files.upload", channel=channel, title='Automated Inventory Collection', file=filename)
        #slack_client.api_call("chat.postMessage", channel=channel, text=text)
        with open(filename, 'rb') as f:
            slack_client.api_call(
                "files.upload",
                channels=channel,
                filename=filename,
                title=title,
                initial_comment=initial_comment,
                file=io.BytesIO(f.read()))

    except Exception:
        trace_string = traceback.format_exc()
        log_ops.log_msg(bot_name=bot_name, script_name=script_name, cmd='Send message to Slack', status='Failed',
                        result="Failed\n" + trace_string + "\n")
