import json
import re
import requests


def adj_factor(symbol):
    factor = {}

    qfq_api = "https://finance.sina.com.cn/realstock/company/{}/qfq.js".format(symbol)
    hfq_api = "https://finance.sina.com.cn/realstock/company/{}/hfq.js".format(symbol)

    if requests.head(qfq_api).status_code == 200:
        q = requests.get(qfq_api)
        h = requests.get(hfq_api)
        factor["qfq"] = json.loads(re.search(r"({.*})", q.text).group(0))["data"]
        factor["hfq"] = json.loads(re.search(r"({.*})", h.text).group(0))["data"]

        return factor


def get_stock_state_and_capital(symbol):
    """
    symbol = sh000001
    0:无该记录
    1:上市正常交易
    2:未上市
    3:退市
    """
    url = "http://finance.sina.com.cn/realstock/company/{symbol}/jsvar.js".format(
        symbol=symbol
    )
    if requests.head(url).status_code == 200:
        r = requests.get(url)
        status = re.search(r"(stock_state = \d)", r.text).group(0).split(" = ")[-1]
        # totalcapital = re.search(r" totalcapital = \d+(.\d+)?",
        #                         r.text).group(0).split(" = ")[-1]
        # curracapital = re.search(r" curracapital = \d+(.\d+)?",
        #                         r.text).group(0).split(" = ")[-1]
        return {
            "symbol": symbol,
            "status": status,
            #    'total_capital': totalcapital,
            #    'curra_capital': curracapital
        }
