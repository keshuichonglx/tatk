#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    :   dep_mul_mdbt_rule_temp
@Time    :   2019-07-23
@Software:   PyCharm
@Author  :   Li Xiang
@Desc    :   
"""
import sys
import os
import copy

root_dir = os.path.dirname(__file__)
sys.path.insert(0, root_dir)
from tatk.dialog_agent import PipelineAgent

from tatk.dst.mdbt.multiwoz.mdbt import MultiWozMDBT
from tatk.policy.rule.multiwoz import Rule
from tatk.nlg.template_nlg.multiwoz import TemplateNLG

from DeployClient import DeployClient, FunctionRunError, MyLock

# 这里设置服务启动相关设置,port=开放的端口,max_items=最大缓存数据条数,expire_sec=缓存超时时间(秒)
app = DeployClient(module_name=__name__, port=7790, max_items=1000, expire_sec=600)

# 这里进行模型的实例化或一些模型必要的加载和初始化工作
nlu = None
dst = MultiWozMDBT()
policy = Rule()
nlg = TemplateNLG(is_user=False)
sys_agent = PipelineAgent(nlu, dst, policy, nlg)
state_tracker_ini = copy.deepcopy(sys_agent.tracker.state)
state_policy_ini = copy.deepcopy(sys_agent.policy.policy.last_state)

model_lock = MyLock()

@app.inference_buffer('multiwoz_mdbt_rule_temp')
def inference(input: dict, buffer: dict) -> (dict, dict):
    # 这里通过input作为输入，计算得到output结果
    if 'post' not in input.keys():
        raise FunctionRunError('Missing argument in input')

    # 如果是第一轮，那么给一个初始默认的空dict
    if not buffer:
        print('ini new state')
        buffer = copy.deepcopy({'tra': state_tracker_ini, 'pol': state_policy_ini})

    print('input state :' + str(buffer))

    # 开始执行
    model_lock.enter()
    try:
        sys_agent.tracker.state = buffer['tra']
        sys_agent.policy.policy.last_state = buffer['pol']

        resp = sys_agent.response(input['post'])

        new_buffer = copy.deepcopy({'tra': sys_agent.tracker.state, 'pol': sys_agent.policy.policy.last_state})
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
