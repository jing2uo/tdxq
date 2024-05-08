import requests
import json
import logging
import telebot

from colorama import Fore, Style

from config import feishu_token, tg_token, tg_chatid


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = ColorFormatter(
        "%(asctime)s - %(filename)s - %(levelname)s - %(message)s"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


class ColorFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.INFO:
            level_color = Fore.GREEN
        elif record.levelno == logging.WARNING:
            level_color = Fore.YELLOW
        elif record.levelno == logging.ERROR:
            level_color = Fore.RED
        else:
            level_color = ""

        format_str = f"{level_color}%(asctime)s - %(filename)s - %(levelname)s - %(message)s{Style.RESET_ALL}"
        formatter = logging.Formatter(format_str)
        return formatter.format(record)


def feishu_notify(text: str):
    url = "https://open.feishu.cn/open-apis/bot/v2/hook/{token}".format(
        token=feishu_token
    )
    keyword = "股票提醒"
    payload = {"msg_type": "text", "content": {"text": keyword + text}}
    headers = {"Content-Type": "application/json"}
    requests.post(url, headers=headers, data=json.dumps(payload))


def tg_notify(text: str):
    bot = telebot.TeleBot(tg_token)
    bot.send_message(tg_chatid, text)
