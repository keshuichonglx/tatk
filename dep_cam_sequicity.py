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
    # 这里通过input作为输入，计算得到output结果
    if 'post' not in input.keys():
        raise FunctionRunError('Missing argument in input')

    print('input state :' + str(buffer))

    # 开始执行
    model_lock.enter()
    try:
        mod.kw_ret = update_x2y(buffer, mod.kw_ret)

        resp = mod.response(input['post'])

        new_buffer = update_x2y(mod.kw_ret, buffer)
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
