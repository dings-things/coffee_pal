import threading
import time
import schedule
from db.reservation import FileDB


class Scheduler(threading.Thread):
    def __init__(self, db: FileDB, at: str):
        super().__init__()
        self.db = db
        self.at = at
        self.daemon = True

    def run(self):
        print("Scheduler started")
        schedule.every().day.at(self.at, "Asia/Seoul").do(self.db.reload)
        while True:
            schedule.run_pending()
            time.sleep(1)
