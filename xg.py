import multiprocessing
import mplfinance as mpf
import pandas as pd
import numpy as np
from datetime import timedelta


from db import stock, gbbq
from tdx import fq
from indicator.compute import get_ao, get_alligator, get_ma
from datasource.eastmoney import get_all_stocks

from config import work_dir
from utils import clean_dir, get_logger

logger = get_logger(__name__)


def make_plot(df):
    p = df[-90:]

    def plot_check(df, column_name):
        if not np.isnan(df[column_name]).all():
            return True
        else:
            return False

    add_study = []
    if plot_check(p, "jaws") and plot_check(p, "lips") and plot_check(p, "teeth"):
        add_study.append(mpf.make_addplot(p["jaws"], color="b", linestyle="-", panel=0))
        add_study.append(mpf.make_addplot(p["lips"], color="g", linestyle="-", panel=0))
        add_study.append(
            mpf.make_addplot(p["teeth"], color="r", linestyle="-", panel=0)
        )
    if plot_check(p, "ma50"):
        add_study.append(
            mpf.make_addplot(p["ma50"], color="dimgray", linestyle="--", panel=0)
        )
    if plot_check(p, "ma200"):
        add_study.append(
            mpf.make_addplot(p["ma200"], color="orange", linestyle="--", panel=0)
        )
    if plot_check(p, "ao"):
        add_study.append(
            mpf.make_addplot(
                p["ao"],
                type="bar",
                width=0.7,
                panel=2,
                color="dimgray",
                alpha=1,
                secondary_y=False,
            ),
        )
    symbol = df["symbol"].iloc[0]
    mc = mpf.make_marketcolors(up="r", down="g")
    s = mpf.make_mpf_style(marketcolors=mc)
    mpf.plot(
        p,
        type="candle",
        addplot=add_study,
        title=symbol,
        style=s,
        volume=True,
        savefig=work_dir.rstrip("/") + "/{}.png".format(symbol),
    )


def eyu(symbol):
    code = symbol[2:]
    xdxr_data = gbbq.query(code=code)
    bfq_data = stock.query(symbol=symbol)

    df = fq(bfq_data, xdxr_data)

    tmp = pd.DataFrame()
    tmp["ao"] = get_ao(df)
    tmp["ma50"] = get_ma(df, 50)
    tmp["ma200"] = get_ma(df, 200)
    tmp["jaws"], tmp["teeth"], tmp["lips"] = get_alligator(df)

    return df.merge(tmp, left_index=True, right_index=True)


def cross(df1, df2):
    for i in range(1, len(df1)):
        if df1.iloc[i] > df2.iloc[i] and df1.iloc[i - 1] <= df2.iloc[i - 1]:
            return True
    return False


def check(s):
    symbol = s["exchange"] + s["code"]
    df_all = eyu(symbol)

    sh_latest = stock.latest_data("sh999999").index[0]
    start_date = sh_latest - timedelta(15)
    df = df_all[start_date:]
    if (
        not df.empty
        and df["close"].iloc[-1] > df["ma50"].iloc[-1]
        and df["ao"].iloc[-1] < 0
        and df["ao"].iloc[-1] > df["ao"].iloc[-2] > df["ao"].iloc[-3]
        # if (
        # cross(df["ma50"], df["ma200"])
        # or cross(df["close"], df["ma50"])
        # or cross(df["close"], df["ma200"])
        # or cross(df["lips"], df["teeth"])
        # or cross(df["lips"], df["jaws"])
    ):
        try:
            make_plot(df_all)
            return s["code"]
        except:
            logger.error("生成图表失败:{}".format(symbol))


def xg():
    logger.info("开始选股")
    logger.info("清理目录:{}".format(work_dir))
    clean_dir(work_dir)
    stocks_list = get_all_stocks()
    pre_list = []
    for s in stocks_list:
        if (
            s["exchange"] != "bj"
            and s["market"] != "sh_star"
            and s["listed_date"] != 0
            and "退" not in s["name"]
            and "停" not in s["name"]
            and "ST" not in s["name"]
        ):
            pre_list.append(s)

    with multiprocessing.Pool() as pool:
        my_list = pool.map(check, pre_list)

    with open(work_dir.rstrip("/") + "/xg.txt", "w") as file:
        for i in my_list:
            if i is not None:
                file.write(str(i) + "\n")

    logger.info("选股完成")


if __name__ == "__main__":
    xg()
