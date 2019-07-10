#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    :   DeployClinet
@Time    :   2019-06-27
@Software:   PyCharm
@Author  :   Li Xiang
@Desc    :   
"""

import datetime
import threading
import copy
from flask import Flask, request, Response, jsonify
#Response(json.dumps(result),  mimetype='application/json')

class DeployClient(object):
    def __init__(self, module_name: str, port: int, max_items=None, expire_sec=None, host: str = '0.0.0.0'):
        # flask module
        self.module_name = module_name
        self.host = host
        self.port = port
        self.app = Flask(self.module_name)

        # function list
        self.fun_infer = dict({})
        self.fun_infer_b = dict({})

        # buffer
        self.buffers = ExpireDict(max_items, expire_sec)

        # 注册
        @self.app.route('/<name>', methods=['POST'])
        def register_Response(name):
            input = self.get_json_obj(request)
            if not isinstance(input, dict):
                Msg = 'Input parameter type is incorrect! type=%s data=%s' % (str(type(input)), str(input))
                print(Msg)
                return jsonify({'Error': 'INPUT_TYPE_INCORRECT', 'ErrorMsg': Msg})

            print('<' + str(input))

            # process
            # inference
            if name in self.fun_infer.keys():
                fun = self.fun_infer[name]
                try:
                    output = fun(input)
                except FunctionRunError as e:
                    return jsonify({'Error': 'FUNCTION_RUN_ERROR', 'ErrorMsg': name + '->' + e.error_msg})

            # inference_buffer
            elif name in self.fun_infer_b.keys():
                fun, token_name = self.fun_infer_b[name]
                token = request.args.get(token_name)
                if token is None:
                    return jsonify({'Error': 'INPUT_LACK_OF_TOKEN', 'ErrorMsg': 'Can not find %s key in the input' % token_name})

                try:
                    output, new_buffer = fun(input, self.buffers.get(token, dict({})))
                    self.buffers[token] = copy.deepcopy(new_buffer)
                except FunctionRunError as e:
                    return jsonify({'Error': 'FUNCTION_RUN_ERROR', 'ErrorMsg': name + '->' + e.error_msg})

            # 没有找到对应的响应
            else:
                return jsonify({'Error': 'FUNCITON_UNK', 'ErrorMsg': 'can not found %s funciotn' % name})

            print('>' + str(output))
            return jsonify(output)

    def run(self):
        print(self.fun_infer)
        print(self.fun_infer_b)
        self.app.run(host=self.host, port=self.port)

    def inference(self, fun_name: str):
        """
        注册某个function为接口处理函数，函数需满足输入输出均为dict，工作过程中产生错误请通过raise返回FunctionRunError错误
        :param fun_name: 自定义处理方法的名称
        """

        def decorator(f):
            assert fun_name not in self.fun_infer.keys(), '%s方法被重复定义' % fun_name
            assert fun_name not in self.fun_infer_b.keys(), '%s方法已在inference_buffer中被定义' % fun_name
            self.fun_infer[fun_name] = f
            return f

        return decorator

    def inference_buffer(self, fun_name: str, token_name: str = 'token'):
        """
        注册某个function为接口处理函数，另外提供本地缓存，函数需满足输入输出均为dict，
        工作过程中产生错误请通过raise返回FunctionRunError错误
        :param fun_name: 自定义处理方法的名称
        :param token_name: 唯一标识名称，默认'token',一般默认建议不要设置，直接使用默认值，以便与前端系统统一
        """

        def decorator(f):
            assert fun_name not in self.fun_infer_b.keys(), '%s方法被重复定义' % fun_name
            assert fun_name not in self.fun_infer.keys(), '%s方法已在inference中被定义' % fun_name
            self.fun_infer_b[fun_name] = (f, token_name)
            return f

        return decorator

    @staticmethod
    def get_json_obj(reqt):
        in_dict = None
        if 'application/json' in reqt.headers.environ['CONTENT_TYPE']:
            in_dict = reqt.json
        elif 'application/x-www-form-urlencoded' in reqt.headers.environ['CONTENT_TYPE']:
            in_dict = reqt.form.to_dict()
        return in_dict


class FunctionRunError(Exception):
    def __init__(self, error_msg: str = ''):
        super().__init__(self)
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg


class ExpireDict(object):
    """
    key: [time_stamp, data]
    """
    def __init__(self, max_items=None, expire_sec=None):
        self.max_items = max_items
        self.expire_sec = expire_sec
        self.values = dict({})
        self.lock = MyLock()

    def __len__(self):
        return len(self.values)

    def __getitem__(self, key):
        if key not in self.values.keys():
            raise KeyError
        self.lock.enter()  # in
        val = self.__getitem(key)
        self.lock.leave()  # out
        return val

    def __setitem__(self, key, value):
        self.lock.enter()  # in
        self.__setitem(key, value)
        self.lock.leave()  # out

    def __delitem__(self, key):
        self.lock.enter()  # in
        self.__delitem(key)
        self.lock.leave()  # out

    def __iter__(self):
        return iter(self.values)

    def __str__(self):
        return self.values.__str__()

    def keys(self):
        return self.values.keys()

    def get(self, key, default_value=None):
        try:
            value = self[key]
        except KeyError:
            value = default_value
        return value

    def __getitem(self, key):
        self.values[key][0] = self.__time_stamp()
        return copy.deepcopy(self.values[key][1])

    def __setitem(self, key, value):
        if key not in self.values.keys():
            self.__clear_expire()
        self.values[key] = [self.__time_stamp(), value]

    def __delitem(self, key):
        if key in self.values.keys():
            del self.values[key]

    def __clear_expire(self):
        expire_keys = set({})
        if self.max_items is not None:
            if len(self.values) >= self.max_items:
                items_sorted = sorted(self.values.items(), key=lambda x: x[1][0])
                expire_keys = expire_keys.union(set([k for k, _ in items_sorted[:self.max_items // 2]]))
            pass

        if self.expire_sec is not None:
            now = self.__time_stamp()
            for key, value in self.values.items():
                if now - value[0] > self.expire_sec:
                    expire_keys.add(key)
            pass

        for key in expire_keys:
            self.__delitem(key)

    @staticmethod
    def __time_stamp():
        return datetime.datetime.now().timestamp()


class MyLock(object):
    def __init__(self, num=1):
        if num <= 1:
            self.__lock = threading.Lock()
        else:
            self.__lock = threading.Semaphore(num)

    def enter(self):
        self.__lock.acquire()

    def leave(self):
        self.__lock.release()


def test():
    aa = ExpireDict(max_items=4, expire_sec=3)
    aa['1'] = 123
    aa['2'] = "eee"
    aa['3'] = ["ddd", 123]
    print(aa['1'])
    aa['4'] = "ssddd"
    aa['5'] = "as"
    for b in aa:
        print(b)

    print(aa)


if __name__ == '__main__':
    test()
