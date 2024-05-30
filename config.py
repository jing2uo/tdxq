import os


work_dir = os.getenv("WORK_DIR", "/tmp/tdx/")
qw_token = os.getenv("QW_TOKEN")


class QuestDBConfig:
    user = os.getenv("DB_USER", "admin")
    password = os.getenv("DB_PASSWORD", "quest")
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "8812")
    rest_port = os.getenv("DB_RESTPORT", "9000")
    database = os.getenv("DB_DATABASE", "qdb")
    dsn = f"postgresql://{user}:{password}@{host}:{port}/{database}"


quest = QuestDBConfig()
