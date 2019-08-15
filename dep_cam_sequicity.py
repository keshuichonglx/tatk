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
model_lock = MyLock()


def update_x2y(x: dict, y: dict):
    dkeys = ['prev_z_len', 'prev_z_input', 'prev_z_input_np']
    for key in dkeys:
        if key in x.keys():
            y[key] = copy.deepcopy(x[key])
        elif key in y.keys():
            del y[key]
    return y


@app.inference_buffer('camrest_sequicity')
def inference(input: dict, buffer: dict) -> (dict, dict):
    buffer.setdefault('states', [])

    if input.get('recall', False):
        print('[opt: recall]')
        model_lock.enter()
        if buffer['states']:
            del buffer['states'][-1]
        new_buffer = copy.deepcopy(buffer)
        output = {'turns': len(buffer['states'])}
        model_lock.leave()
        return output, new_buffer

    # 这里通过input作为输入，计算得到output结果
    if 'post' not in input.keys():
        raise FunctionRunError('Missing argument in input')

    print('[opt: normal]')
    model_lock.enter()
    # 获得当前轮次的状态
    if buffer['states']:
        cur_state = buffer['states'][-1]
    else:
        print('ini new state')
        cur_state = {}

    print('input state :' + str(cur_state))
    try:
        mod.kw_ret = update_x2y(cur_state, mod.kw_ret)

        resp = mod.response(input['post'])

        buffer['states'].append(update_x2y(mod.kw_ret, cur_state))
        new_buffer = copy.deepcopy(buffer)
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
