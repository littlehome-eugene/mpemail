from django.apps import AppConfig
import time
import os

import logging
from logging.handlers import TimedRotatingFileHandler
from django.conf import settings



class EmailConfig(AppConfig):
    name = 'mpemail'

    def ready(self):

        import mpemail.signals.email
        # self.prepare_log()


    def prepare_log(self):

        # format the log entries
        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')

        handler = TimedRotatingFileHandler(os.path.join(settings.LOG_DIR, 'logfile.log'),
                                           when='midnight',
                                           backupCount=365*10)
        handler.setFormatter(formatter)
    #     logger = logging.getLogger(__name__)
    #     logger.addHandler(handler)
    #     logger.setLevel(logging.DEBUG)
