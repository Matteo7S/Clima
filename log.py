import time
import traceback

class Log():
    def log(self, message, error=None):
        timestamp = time.strftime("%Z %Y-%m-%d %H:%M:%S", time.localtime())
        if error:
            trace = traceback.format_exc()
            message += "\n" + trace
        message = timestamp + " " + message
        print(message)