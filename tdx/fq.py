import pandas as pd


def fq(bfq_data, xdxr_data, fqtype="qfq"):
    if xdxr_data is None:
        info = ""
    else:
        info = xdxr_data.query("category==1")
    bfq_data = bfq_data.assign(if_trade=1)

    if len(info) > 0:
        data = pd.concat(
            [bfq_data, info.loc[bfq_data.index[0] : bfq_data.index[-1], ["category"]]],
            axis=1,
        )
        data.fillna({"if_trade": 0}, inplace=True)
        data.ffill()
        data = pd.concat(
            [
                data,
                info.loc[
                    bfq_data.index[0] : bfq_data.index[-1],
                    ["fenhong", "peigu", "peigujia", "songgu"],
                ],
            ],
            axis=1,
        )
    else:
        data = pd.concat(
            [
                bfq_data,
                info.loc[:, ["category", "fenhong", "peigu", "peigujia", "songgu"]],
            ],
            axis=1,
        )
    data.ffill()

    data["preclose"] = (
        data["close"].shift(1) * 10 - data["fenhong"] + data["peigu"] * data["peigujia"]
    ) / (10 + data["peigu"] + data["songgu"])

    if fqtype == "qfq":
        data["adj"] = (
            (data["preclose"].shift(-1) / data["close"]).fillna(1)[::-1].cumprod()
        )
    else:
        data["adj"] = (
            (data["close"] / data["preclose"].shift(-1)).cumprod().shift(1).fillna(1)
        )

    for col in ["open", "high", "low", "close", "preclose"]:
        data[col] = data[col] * data["adj"]
        data[col] = round(data[col], 2)

    return data.query("if_trade==1 and open != 0").drop(
        [
            "fenhong",
            "peigu",
            "peigujia",
            "songgu",
            "if_trade",
            "category",
            "preclose",
            "adj",
        ],
        axis=1,
    )
