import time
import traceback
from database import DB
import logging

db =DB()

class Log():
    def log(self, message, error=None):
        # timestamp = time.strftime("%Z %Y-%m-%d %H:%M:%S", time.localtime())
        # if error:
        #     trace = traceback.format_exc()
        #     message += "\n" + trace
        # message = timestamp + " " + message
        # try:
        #     db.insert_log(message, error)
        #     print(message)
        # except Exception as err:
        #     print("Errore di log!!")
        #     print(err)

        #Creating and Configuring Logger

        Log_Format = "%(levelname)s %(asctime)s - %(message)s"

        logging.basicConfig(filename = "logfile.log",
                            filemode = "w",
                            format = Log_Format, 
                            level = logging.ERROR)

        logger = logging.getLogger()

        #Testing our Logger

        logger.error(message)