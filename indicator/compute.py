import pandas as pd
import numpy as np


def ma(df, period):
    return df.close.rolling(window=period).mean()


# 定义 SMMA（平滑移动平均线）函数
def smma(series, period):
    smma_values = [series.iloc[0]]  # 初始化第一个值为第一个数据
    alpha = 1 / period  # 平滑因子
    for price in series.iloc[1:]:
        smma_values.append(smma_values[-1] + alpha * (price - smma_values[-1]))
    return pd.Series(smma_values, index=series.index)


# 计算鳄鱼线，包括蓝线 (Jaw)、红线 (Teeth)、绿线 (Lips)。
def calculate_alligator(data):
    data["Jaw"] = smma(data["close"], 13).shift(8)  # 蓝线，13周期 SMMA 平移 8 天
    data["Teeth"] = smma(data["close"], 8).shift(5)  # 红线，8周期 SMMA 平移 5 天
    data["Lips"] = smma(data["close"], 5).shift(3)  # 绿线，5周期 SMMA 平移 3 天
    return data


# 找到向上分形（Fractal Up）和向下分形（Fractal Down）。
def calculate_fractals(data):
    data["Fractal_Up"] = np.nan
    data["Fractal_Down"] = np.nan

    # 计算向上分形（high 大于前后两天的 high）
    data["Fractal_Up"] = data["high"][
        (data["high"] > data["high"].shift(1))
        & (data["high"] > data["high"].shift(2))
        & (data["high"] > data["high"].shift(-1))
        & (data["high"] > data["high"].shift(-2))
    ]

    # 计算向下分形（low 小于前后两天的 low）
    data["Fractal_Down"] = data["low"][
        (data["low"] < data["low"].shift(1))
        & (data["low"] < data["low"].shift(2))
        & (data["low"] < data["low"].shift(-1))
        & (data["low"] < data["low"].shift(-2))
    ]

    return data


# 计算 AO（Awesome Oscillator）动量指标。
def calculate_ao(data, fast_period=5, slow_period=34):
    data["Median_Price"] = (data["high"] + data["low"]) / 2
    data["Fast_SMA"] = data["Median_Price"].rolling(window=fast_period).mean()
    data["Slow_SMA"] = data["Median_Price"].rolling(window=slow_period).mean()
    data["AO"] = data["Fast_SMA"] - data["Slow_SMA"]

    data.drop(columns=["Median_Price", "Fast_SMA", "Slow_SMA"], inplace=True)

    return data


# 计算 AC（Accelerator Oscillator，加速震荡指标）。
def calculate_ac(data, ao_fast_period=5):
    data["SMA_AO"] = data["AO"].rolling(window=ao_fast_period).mean()
    data["AC"] = data["SMA_AO"] - data["AO"]

    data.drop(columns=["SMA_AO"], inplace=True)

    return data


def check_alligator_up(data, n=5):
    """
    判断最近 n 天是否满足收盘价 > 绿线 > 红线 > 蓝线。
    :param data: 包含 'close', 'Jaw', 'Teeth', 'Lips' 列的 DataFrame
    :param n: 检查的天数
    :return: True 或 False
    """
    recent_data = data.iloc[-n:]  # 获取最近 n 天的数据
    condition = (
        (recent_data["close"] > recent_data["Lips"])
        & (recent_data["Lips"] > recent_data["Teeth"])
        & (recent_data["Teeth"] > recent_data["Jaw"])
    )
    return condition.all()  # 如果所有天都满足条件，返回 True


# 检查最近 3 天是否突破最近的向上分形
def check_fractal_up(data):
    """
    检查最近 3 天的任意一天是否突破了前面最近的向上分形。
    :param data: 包含 'close' 和 'Fractal_Up' 列的 DataFrame
    :return: True 或 False
    """
    # 找到最近的向上分形（忽略最后 3 天的分形）
    fractal_up = data["Fractal_Up"].dropna()

    # 确保索引是整数索引（如果是时间索引，需要先重置索引）
    if not isinstance(fractal_up.index, pd.RangeIndex):
        fractal_up = fractal_up.reset_index(drop=True)

    # 获取最近的向上分形值（排除最后 3 天）
    recent_fractal_up = fractal_up[fractal_up.index < len(data) - 3]
    if recent_fractal_up.empty:  # 如果没有找到向上分形，返回 False
        return False

    last_fractal_value = recent_fractal_up.iloc[-1]  # 最近的向上分形值

    # 检查最近 3 天的任意一天是否突破
    recent_close = data["close"].iloc[-3:]  # 最近 3 天的收盘价
    return (recent_close > last_fractal_value).any()  # 如果任意一天突破，返回 True


def check_ao_buy_signals(data):
    """
    检查最近三天内是否满足 AO 的买入信号之一：
    1. 零轴交叉。
    2. 双峰信号。
    3. 碟形信号。

    参数：
    - data: pd.DataFrame，必须包含一个 'AO' 列。

    返回：
    - bool: 如果满足任意一个买入条件，返回 True；否则返回 False。
    """
    # 确保数据包含 AO 列
    if "AO" not in data.columns:
        raise ValueError("DataFrame 必须包含 'AO' 列。")

    # 获取最近 3 天的数据
    recent = data.iloc[-3:]

    # 检查零轴交叉信号
    for i in range(1, len(recent)):
        if recent["AO"].iloc[i - 1] < 0 and recent["AO"].iloc[i] > 0:
            return True

    # 检查双峰信号
    if len(data) >= 5:  # 至少需要历史数据支持双峰信号
        for i in range(2, len(recent)):
            # 最近 3 天是否满足条件
            if (
                data["AO"].iloc[-5] < 0  # AO 在零轴下
                and data["AO"].iloc[-4] < data["AO"].iloc[-5]  # 第一个峰值较低
                and data["AO"].iloc[-2] > data["AO"].iloc[-3]  # 第二个峰值较高
                and data["AO"].iloc[-1] > data["AO"].iloc[-2]  # 跟随一个绿色柱状线
            ):
                return True

    # 检查碟形信号
    if len(data) >= 3:  # 至少需要历史数据支持碟形信号
        for i in range(2, len(recent)):
            if (
                data["AO"].iloc[-3] > 0  # AO 在零轴上方
                and data["AO"].iloc[-2] < data["AO"].iloc[-3]  # 连续两个红色柱状线
                and data["AO"].iloc[-1] > data["AO"].iloc[-2]  # 跟随一个绿色柱状线
            ):
                return True

    # 如果没有满足任意条件，则返回 False
    return False
