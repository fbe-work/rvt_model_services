import os.path as op
import configparser
import requests


def fetch_config(prj_number):
    config = configparser.ConfigParser()
    ini_file = op.join(op.dirname(op.abspath(__file__)), "config.ini")
    if op.exists(ini_file):
        config.read(ini_file)
        if prj_number in config:
            url = config[prj_number]["url"]
            ssl_verify = config[prj_number]["ssl_verify"]
            return url, ssl_verify
    return None, None


def notify(prj_number, prj_path, journal_excerpt):
    url, ssl_verify = fetch_config(prj_number)
    verify_map = {"true": True, "false": False}
    text = f"warning - rvt model: {prj_number}\nat path: {prj_path}\n is corrupt! see journal:\n{journal_excerpt}"
    requests.post(url, data={"text": text}, verify=verify_map[ssl_verify])
