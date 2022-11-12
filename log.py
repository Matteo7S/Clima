import time
import traceback
from database import DB

db =DB()

class Log():
    def log(self, message, error=None):
        timestamp = time.strftime("%Z %Y-%m-%d %H:%M:%S", time.localtime())
        if error:
            trace = traceback.format_exc()
            message += "\n" + trace
        message = timestamp + " " + message
        try:
            db.insert_log(message)
            print(message)
        except Exception as err:
            print("Errore di log!!")