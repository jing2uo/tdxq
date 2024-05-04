import talib
import pandas as pd


def get_ma(df, period):
    return df.close.rolling(window=period).mean()


def get_macd(df):
    macd_dif, macd_dea, macd_bar = talib.MACD(
        df["close"].values, fastperiod=12, slowperiod=26, signalperiod=9
    )
    return macd_dif, macd_dea, macd_bar


def get_smma(df, period, df_col):
    column_name = "SMMA" + str(period)
    df[column_name] = df[df_col].rolling(period).mean()

    df_smma = df.reset_index()
    for index, row in df_smma.iterrows():
        if index > period:
            df_smma.at[index, column_name] = (
                (period - 1) * df_smma.at[index - 1, column_name]
                + df_smma.at[index, column_name]
            ) / period
    df_smma = df_smma.set_index("date")

    return df_smma[column_name]


def get_ao(df):
    tmp = pd.DataFrame()
    tmp["median_price"] = (df["high"] + df["low"]) / 2
    tmp["sma5"] = tmp["median_price"].rolling(window=5).mean()
    tmp["sma34"] = tmp["median_price"].rolling(window=34).mean()

    return tmp["sma5"] - tmp["sma34"]


def get_alligator(df):
    period_jaws = 13
    period_teeth = 8
    period_lips = 5
    shift_jaws = 8
    shift_teeth = 5
    shift_lips = 3

    tmp = pd.DataFrame()
    tmp["median_price"] = (df["high"] + df["low"]) / 2

    tmp["jaws"] = get_smma(tmp, period_jaws, "median_price")
    tmp["teeth"] = get_smma(tmp, period_teeth, "median_price")
    tmp["lips"] = get_smma(tmp, period_lips, "median_price")

    jaws = tmp["jaws"].shift(shift_jaws)
    teeth = tmp["teeth"].shift(shift_teeth)
    lips = tmp["lips"].shift(shift_lips)

    return (jaws, teeth, lips)
