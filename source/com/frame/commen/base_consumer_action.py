# -*- coding: utf-8 -*-
"""
base_consumer_action.py
Created on 2019/5/13 21:55
Copyright 2019/5/13
@author: qcy
"""

class ConsumerAction:
    """
    消费者基类
    """

    def __init__(self):
        """
        :try_num:       当前消费动作失败的重试次数
        :consumser_thread_name      消费该动作线程的名称
        """
        self.try_num = 1
        self.consumser_thread_name = ""

    def action(self):
        """
        执行消费动作，是一个抽象方法，需要根据不同的消费需求进行实现
        :return: 执行完消费动作的返回结果
        """
        pass

    def result(self, is_success, values):
        """
        '''
        根据消费动作(action方法的结果)，选择是执行success_action还是fail_action

        :param is_success:          消费动作的成功状态       True或False
        :param values:              执行完消费信息的返回结果
        :return:                    合并消费动作的状态和消费信息的返回结果
        """
        '''
        根据消费动作(action方法的结果)，选择是执行success_action还是fail_action

        :param is_success:          消费动作的成功状态       True或False
        :param values:              执行完消费信息的返回结果
        :return:                    合并消费动作的状态和消费信息的返回结果
        '''
        return_value = []
        return_value.append(is_success)

        if not is_success:
            self.fail_cation(values)
        else:
            self.success_action(values)

        for re in values:
            return_value.append(re)

        return return_value


    def fail_cation(self, values):
        """
        执行消费动作完成之后的失败动作

        :param values:          执行完消费信息的返回结果
        :return:
        """

        pass

    def success_action(self, values):
        """
        执行消费动作完成之后的成功动作

        :param values:          执行完消费信息的返回结果
        :return:
        """
        pass
