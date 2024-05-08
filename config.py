import os


work_dir = os.getenv("WORK_DIR", "/tmp/tdx/")
feishu_token = os.getenv("FEISHU_TOKEN")
tg_token = os.getenv("TG_TOKEN")
tg_chatid = os.getenv("TG_CHATID")

db_user = os.getenv("DB_USER", "admin")
db_password = os.getenv("DB_PASSWORD", "quest")
db_host = os.getenv("DB_HOST", "127.0.0.1")
db_port = os.getenv("DB_PORT", "8812")
db_database = os.getenv("DB_DATABASE", "qdb")
db_restport = os.getenv("DB_RESTPORT", "9000")


class QuestDBConfig:
    user = db_user
    password = db_password
    host = db_host
    port = db_port
    rest_port = db_restport
    database = db_database
    dsn = "postgresql://{user}:{password}@{host}:{port}/{db}".format(
        user=user, password=password, host=host, port=port, db=database
    )


quest = QuestDBConfig()
