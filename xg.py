import multiprocessing
import pandas as pd

from database import stock, gbbq, csi
from tdx import fq
from config import work_dir
from utils import clean_dir, get_logger, WeChatSender

from indicator import (
    calculate_alligator,
    check_alligator_up,
    calculate_fractals,
    check_fractal_up,
    calculate_ao,
    check_ao_buy_signals,
    ma,
    calculate_ac,
)

import warnings

warnings.simplefilter("ignore", UserWarning)


logger = get_logger(__name__)
wx = WeChatSender()


def get_ma(df):
    tmp = pd.DataFrame()
    tmp["ma10"] = ma(df, 10)
    tmp["ma20"] = ma(df, 20)
    tmp["ma50"] = ma(df, 50)

    return df.merge(tmp, left_index=True, right_index=True)


def cross(df1, df2):
    for i in range(1, len(df1)):
        if df1.iloc[i] > df2.iloc[i] and df1.iloc[i - 1] <= df2.iloc[i - 1]:
            return True
    return False


def check_dapan():
    sh = stock.query("sh999999")
    temp = get_ma(sh)
    tmp = temp.tail(3)
    msg = ""
    if cross(tmp["ma50"], tmp["close"]):
        msg += """## <font color="warning">大盘跌破 50 日均线</font>\n"""
    if cross(tmp["close"], tmp["ma50"]):
        msg += """## <font color="info">大盘突破 50 日均线</font>\n"""
    if tmp["close"].iloc[-1] > tmp["ma50"].iloc[-1]:
        msg += """## <font color="info">大盘在 50 日均线上方</font>\n"""
    else:
        msg += """## <font color="warning">大盘在 50 日均线下方</font>\n"""

    if msg:
        wx.send_markdown_msg(msg)


def check_stock(s):
    code = s["code"]
    symbol = s["symbol"]
    xdxr_data = gbbq.query(code=code)
    bfq_data = stock.query(symbol=symbol)
    data = fq(bfq_data, xdxr_data)
    data = data.iloc[max(len(data) - 200, 0) :]

    # 计算鳄鱼线
    data = calculate_alligator(data)
    data = calculate_fractals(data)
    data = calculate_ao(data)

    # 检查最近 5 天的条件
    if check_alligator_up(data, n=5) and check_fractal_up(data):
        return code


def xg():
    logger.info("开始选股")
    logger.info("清理目录:{}".format(work_dir))
    clean_dir(work_dir)

    check_dapan()

    stocks_df = csi.get_csi()
    stocks_df = stocks_df[~stocks_df.code.str.startswith("68")]
    stocks = stocks_df.to_dict("records")

    with multiprocessing.Pool() as pool:
        my_list = pool.map(check_stock, stocks)

    count = 0
    with open(work_dir.rstrip("/") + "/xg.txt", "w") as file:
        for i in my_list:
            logger.info(i)
            if i is not None:
                count += 1
                file.write(str(i) + "\n")

    logger.info("选股完成")
    msg = f"""### <font color="info">选股完成，共选出 {count} 个</font>\n"""
    wx.send_markdown_msg(msg)


if __name__ == "__main__":
    xg()
