import mplfinance as mpf

from db import stock, gbbq
from tdx import fq
from indicator.compute import get_ao, get_alligator, get_ma


def eyu(symbol):
    code = symbol[2:]
    xdxr_data = gbbq.query(code=code)
    bfq_data = stock.query(symbol=symbol)
    df = fq(bfq_data, xdxr_data)

    df["ao"] = get_ao(df)
    df["ma250"] = get_ma(df, 250)
    df["jaws"], df["teeth"], df["lips"] = get_alligator(df)

    p = df[-90:]

    add_study = [
        mpf.make_addplot(p["jaws"], color="b", linestyle="--", panel=0),
        mpf.make_addplot(p["lips"], color="g", linestyle="--", panel=0),
        mpf.make_addplot(p["teeth"], color="r", linestyle="--", panel=0),
        mpf.make_addplot(p["ma250"], color="purple", linestyle="--", panel=0),
        mpf.make_addplot(
            p["ao"],
            type="bar",
            width=0.7,
            panel=2,
            color="dimgray",
            alpha=1,
            secondary_y=False,
        ),
    ]

    mc = mpf.make_marketcolors(up="r", down="g")
    s = mpf.make_mpf_style(marketcolors=mc)
    mpf.plot(p, type="candle", addplot=add_study, title=symbol, style=s, volume=True)
