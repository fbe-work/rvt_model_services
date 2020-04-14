import os.path as op
import configparser
import smtplib
from email.mime.text import MIMEText


def fetch_config(prj_number):
    config = configparser.ConfigParser()
    ini_file = op.join(op.dirname(op.abspath(__file__)), "config.ini")
    if op.exists(ini_file):
        config.read(ini_file)
        if prj_number in config:
            server = config[prj_number]["server"]
            sender = config[prj_number]["sender"]
            receiver = config[prj_number]["receiver"]
            return server, sender, receiver
    return None, None, None


def notify(prj_number, prj_path, journal_excerpt, subject="", port=25):
    mail_server, mail_sender, mail_recipients = fetch_config(prj_number)
    if not subject:
        subject = "rvt model corrupt!!"
    if mail_server and  mail_sender and mail_recipients:
        mail_text = f"warning - rvt model {prj_number} at path {prj_path} : {subject}! \nsee: {journal_excerpt}"
        msg = MIMEText(mail_text)
        msg['From'] = mail_sender
        msg['To'] = mail_recipients
        msg['Subject'] = f"{prj_number} - {subject}"

        with smtplib.SMTP(f"{mail_server}:{port}") as smtp_con:
            smtp_con.send_message(msg)
