#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    :   dep_cam_sequicity
@Time    :   2019-07-12
@Software:   PyCharm
@Author  :   Li Xiang
@Desc    :   
"""
import sys
import os
import copy

root_dir = os.path.dirname(__file__)
sys.path.insert(0, root_dir)

from tatk.e2e.sequicity.camrest import Sequicity
from DeployClient import DeployClient, FunctionRunError, MyLock

# 这里设置服务启动相关设置,port=开放的端口,max_items=最大缓存数据条数,expire_sec=缓存超时时间(秒)
app = DeployClient(module_name=__name__, port=7782, max_items=1000, expire_sec=600)

# 这里进行模型的实例化或一些模型必要的加载和初始化工作
mod = Sequicity()
state_ini = copy.deepcopy(mod.kw_ret)

model_lock = MyLock()


@app.inference_buffer('camrest_sequicity')
def inference(input: dict, buffer: dict) -> (dict, dict):
    # 这里通过input作为输入，计算得到output结果
    if 'post' not in input.keys():
        raise FunctionRunError('Missing argument in input')

    # 如果是第一轮，那么给一个初始默认的空dict
    if not buffer:
        print('ini new state')
        buffer = copy.deepcopy(state_ini)
    print('input state :' + str(buffer))

    # 开始执行
    model_lock.enter()
    try:
        mod.kw_ret = buffer
        resp = mod.response(input['post'])
        new_buffer = copy.deepcopy(mod.kw_ret)
    except Exception:
        raise FunctionRunError('running error')
    finally:
        model_lock.leave()

    print('output state:' + str(new_buffer))
    # back
    output = {'resp': resp}

    return output, new_buffer


if __name__ == '__main__':
    app.run()
