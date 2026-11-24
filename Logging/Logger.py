import logging

# Файл создаётся в текущей рабочей папке (gitignored). level=INFO, иначе все
# Logger.info в проекте молча отбрасываются фильтром уровня.
logging.basicConfig(
    filename="ProjPSU.log",
    level=logging.INFO,
    format="%(asctime)s -- %(levelname)s -- %(message)s",
    encoding="utf-8",
)


class Logger:
    @staticmethod
    def info(message: str) -> None:
        logging.info(message)

    @staticmethod
    def error(message: str) -> None:
        logging.error(message)