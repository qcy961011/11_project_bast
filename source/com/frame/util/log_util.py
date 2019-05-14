# -*- coding: utf-8 -*-
"""
log_util.py
Created on 2019/5/13 23:33
Copyright 2019/5/13
@author: qcy
"""
from com.frame.util.content import Content
from logging.handlers import TimedRotatingFileHandler
import logging
from com.frame.configs import configs


class LogUtil:
    base_logger = Content._NULL_STR

    log_dict = {}

    def get_base_logger(self):
        if LogUtil.base_logger == Content._NULL_STR:
            LogUtil.base_logger = self.__get_logger('info', 'info')
        return LogUtil.base_logger

    def get_logger(self, log_name, file_name):
        key = log_name + file_name
        if key not in LogUtil.log_dict:
            LogUtil.log_dict[key] = self.__get_logger(log_name, file_name)

        return LogUtil.log_dict[key]

    def __get_new_logger(self, log_name, file_name):

        l = LogUtil()
        l.__get_logger(log_name, file_name)
        return l

    def __get_logger(self, log_name, file_name):
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.INFO)

        fh = TimedRotatingFileHandler(configs._LOG_DIR % (file_name), "D")
        fh.suffix = "%Y%m%d.log"
        fh.setLevel(logging.INFO)

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        return self

    def info(self, msg):
        self.logger.info(msg)
        self.logger.handlers[0].flush()

    def error(self, msg):
        self.logger.error(msg)
        self.logger.handlers[0].flush()

    def exception(self, msg='Exception Logged'):
        self.logger.exception(msg)
        self.logger.handlers[0].flush()
