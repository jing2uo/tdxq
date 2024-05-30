import logging
import os
import json
import requests

from colorama import Fore, Style


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


class WeChatSender:
    def __init__(self) -> None:
        self.token = os.environ.get("QW_TOKEN", "")
        self.webhook = (
            f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={self.token}"
        )

    def send_markdown_msg(self, msg: str):
        content = {
            "msgtype": "markdown",
            "markdown": {
                "content": msg,
            },
        }
        return self.send(content)

    def send(self, content: dict):
        headers = {"Content-type": "application/json"}
        response = requests.post(
            self.webhook, data=json.dumps(content), headers=headers
        )

        resp_data = response.json()
        if resp_data.get("errcode") != 0:
            raise Exception(
                f"post wechat message failed, status code: {response.status_code}, "
                "content: {response.content}"
            )
