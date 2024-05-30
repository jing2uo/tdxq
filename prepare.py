import os
import sys
import argparse
import multiprocessing

from config import work_dir
from tdx import dayfile
from tdx import gbbq as gbbq_tdx
from utils import unzip_file, clean_dir, list_dir
from database import stock
from database import gbbq as gbbq_db

from utils import get_logger

logger = get_logger(__name__)


if __name__ == "__main__":
    sh_history = "https://www.tdx.com.cn/products/data/data/vipdoc/shlday.zip"
    sz_history = "https://www.tdx.com.cn/products/data/data/vipdoc/szlday.zip"
    bj_histoty = "https://www.tdx.com.cn/products/data/data/vipdoc/bjlday.zip"
    zs_history = "https://www.tdx.com.cn/products/data/data/vipdoc/tdxzs_day.zip"

    parser = argparse.ArgumentParser(description="初始化历史数据")

    parser.add_argument(
        "--sh",
        type=str,
        required=True,
        help="上证所有证券日线文件路径, 可以从 {} 下载".format(sh_history),
    )
    parser.add_argument(
        "--sz",
        type=str,
        required=True,
        help="深证所有证券日线文件路径, 可以从 {} 下载".format(sz_history),
    )
    parser.add_argument(
        "--bj",
        type=str,
        required=True,
        help="北证所有证券日线文件路径, 可以从 {} 下载".format(bj_histoty),
    )

    parser.add_argument(
        "--zs",
        type=str,
        required=True,
        help="通达信板块指数日线文件路径, 可以从 {} 下载".format(zs_history),
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()

    sh = os.path.abspath(args.sh)
    sz = os.path.abspath(args.sz)
    bj = os.path.abspath(args.bj)
    zs = os.path.abspath(args.zs)

# 检查文件是否存在
if not os.path.exists(sz) or not os.path.exists(sh) or not os.path.exists(bj):
    if not os.path.exists(sz):
        print(f"错误: 文件 {sz} 不存在.")
    if not os.path.exists(sh):
        print(f"错误: 文件 {sh} 不存在.")
    if not os.path.exists(bj):
        print(f"错误: 文件 {bj} 不存在.")
    if not os.path.exists(zs):
        print(f"错误: 文件 {zs} 不存在.")
    exit(1)


logger.info("开始创建 stock 表")
stock.create_table()
logger.info("创建 stock 表成功")

logger.info("开始创建 gbbq 表")
gbbq_db.create_table()
logger.info("创建 gbbq 表成功")


logger.info("准备工作目录")
prepare_dir = work_dir.rstrip("/") + "/prepare"
clean_dir(prepare_dir)
logger.info("准备工作目录完成：{}".format(prepare_dir))
logger.info("解压证券日线文件")
unzip_file(file_path=sh, target_path=prepare_dir, remove_file=False)
unzip_file(file_path=sz, target_path=prepare_dir, remove_file=False)
unzip_file(file_path=bj, target_path=prepare_dir, remove_file=False)
unzip_file(file_path=zs, target_path=prepare_dir, remove_file=False)
logger.info("日线文件解压完成")

logger.info("转换 day 文件为 csv")
p = multiprocessing.Pool()
for f in list_dir(prepare_dir):
    p.apply_async(dayfile.convert_to_csv, (f,))
p.close()
p.join()
logger.info("转换完成")

logger.info("将 csv 导入到 stock 表")
p = multiprocessing.Pool()
for f in list_dir(prepare_dir):
    if f.endswith(".csv"):
        p.apply_async(stock.bulk_insert_csv, (f,))
p.close()
p.join()
logger.info("导入完成")

logger.info("导入 gbbq 表 (股本变迁)")
gbbq = gbbq_tdx.get_gbbq()
gbbq_file = work_dir.rstrip("/") + "/gbbq.csv"
gbbq.to_csv(gbbq_file, index=False)
gbbq_db.bulk_insert_csv(file_path=gbbq_file)
logger.info("导入完成")
