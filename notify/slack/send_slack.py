"""
Used to send messages to a specified Slack channel. 
Set the token and channel in the config.ini file in the /slack folder

Install Slack Developer Kit for Python
http://slackapi.github.io/python-slackclient/

Usage:
from notify.slack import send_slack

send_slack.notify(project_code, project_path, "Your message here")
"""

from slackclient import SlackClient
import os.path as op
import configparser


def fetch_config(prj_number):
    config = configparser.ConfigParser()
    ini_file = op.join(op.dirname(op.abspath(__file__)), "config.ini")
    if op.exists(ini_file):
        config.read(ini_file)
        if prj_number in config:
            token = config[prj_number]["token"]
            channel = config[prj_number]["channel"]
            return token, channel
    return None, None


def notify(prj_number, prj_path, msg):
    slack_token, slack_channel = fetch_config(prj_number)
    if slack_token and slack_channel:
        sc = SlackClient(slack_token)
        notify_text = f"warning - rvt model {prj_number} at path {prj_path} is corrupt! \nsee journal: {msg}"

        sc.api_call(
                    "chat.postMessage",
                    channel=slack_channel,
                    text=notify_text,
                    username="rvt_model_services",
                    # placeholder icon
                    icon_url="http://lorempixel.com/48/48/"
                    )
