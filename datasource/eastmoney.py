import requests

fs = {
    "sh": "m:1 t:2,m:1 t:23",
    "sz": "m:0 t:6,m:0 t:80",
    "bj": "m:0 t:81 s:2048",
    "gem": "m:0 t:80",
    "star": "m:1 t:23",
    "shhk": "b:BK0707",
    "szhk": "b:BK0804",
}


def get_stock_list(fs):
    params = {"pn": "1", "pz": "10000", "fields": "f12,f14,f26", "fs": fs}

    r = requests.get("https://33.push2.eastmoney.com/api/qt/clist/get", params=params)

    j = r.json()["data"]["diff"]
    stock_list = []
    for _, value in j.items():
        stock_list.append(
            {"f12": value["f12"], "f14": value["f14"], "f26": value["f26"]}
        )
    return [
        {"code": code, "name": name, "listed_date": date}
        for code, name, date in ((i["f12"], i["f14"], i["f26"]) for i in stock_list)
    ]


def get_all_stocks():
    sh_list = get_stock_list(fs["sh"])
    sz_list = get_stock_list(fs["sz"])
    bj_list = get_stock_list(fs["bj"])

    star_temp = set(i["code"] for i in get_stock_list(fs["star"]))
    gem_temp = set(i["code"] for i in get_stock_list(fs["gem"]))
    shhk_temp = {i["code"] for i in get_stock_list(fs["shhk"])}
    szhk_temp = {i["code"] for i in get_stock_list(fs["szhk"])}

    for i in bj_list:
        i["exchange"] = "bj"
        i["market"] = "main"

    for i in sh_list:
        i["exchange"] = "sh"
        i["market"] = "sh_star" if i["code"] in star_temp else "main"
        i["hksc"] = i["code"] in shhk_temp

    for i in sz_list:
        i["exchange"] = "sz"
        i["market"] = "sz_gem" if i["code"] in gem_temp else "main"
        i["hksc"] = i["code"] in szhk_temp

    return sz_list + sh_list + bj_list
