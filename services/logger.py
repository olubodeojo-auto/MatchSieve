from datetime import datetime


class Logger:

    @staticmethod
    def line():
        print("=" * 60)

    @staticmethod
    def info(message):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[INFO {now}] {message}")

    @staticmethod
    def success(message):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[SUCCESS {now}] {message}")

    @staticmethod
    def warning(message):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[WARNING {now}] {message}")

    @staticmethod
    def error(message):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[ERROR {now}] {message}")