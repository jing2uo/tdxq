import datetime
import subprocess
import requests

from subprocess import check_output, Popen, CalledProcessError
from typing import NewType

from utils import unzip_file, download_file, clean_dir
from config import work_dir


datestr = NewType("datestr", str())
"""
date: %Y%m%d
datestr: "20220218"
"""


class TdxDataTool:
    def __init__(self) -> None:
        self.work_dir = work_dir
        try:
            cmd = ["which", "datatool"]
            check_output(cmd)
        except CalledProcessError:
            raise FileNotFoundError("Please install datatool(v4) to PATH")

    def _check_if_workday(self, date: datestr) -> bool:
        url = "https://www.tdx.com.cn/products/data/data/g4day/{}.zip".format(date)
        if requests.head(url).status_code == 200:
            self.url = url
            return True
        else:
            return False

    def download_dayfile(self, date: datestr = None) -> str:
        if not date:
            date = datetime.date.today().strftime("%Y%m%d")
        workday = self._check_if_workday(date)
        if not workday:
            return "not workday"
        if workday:
            today_dir = work_dir.rstrip("/") + "/" + date
            clean_dir(today_dir)
            sh_day_dir = today_dir + "/sh/lday"
            sz_day_dir = today_dir + "/sz/lday"
            bj_day_dir = today_dir + "/bj/lday"

            dt_ini = """[PATH]\nVIPDOC={}\n""".format(today_dir)
            with open(today_dir + "/datatool.ini", "w") as f:
                f.write(dt_ini)

            filepath = download_file(
                url=self.url, target_path=today_dir, check_url=False
            )
            zip_extract_to = today_dir + "/refmhq"
            unzip_file(file_path=filepath, target_path=zip_extract_to)
            p = Popen(
                ["datatool", "day", "create", date],
                cwd=today_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            p.wait()

            aio = today_dir + "/allinone"
            p = Popen(
                """mkdir -p {aio} && mv {sh_day_dir} {aio}/sh && mv {sz_day_dir} {aio}/sz && mv {bj_day_dir} {aio}/bj
                """.format(
                    aio=aio,
                    sz_day_dir=sz_day_dir,
                    sh_day_dir=sh_day_dir,
                    bj_day_dir=bj_day_dir,
                ),
                shell=True,
            )
            p.wait()

            return aio


datatool = TdxDataTool()
