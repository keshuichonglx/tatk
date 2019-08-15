#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    :   dep_cam_svm_rule_rule_temp
@Time    :   2019-07-10
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
from tatk.nlu.svm.camrest import SVMNLU
from tatk.dst.rule.camrest.state_tracker import RuleDST
from tatk.policy.rule.camrest import Rule
from tatk.nlg.template.camrest import TemplateNLG

from DeployClient import DeployClient, FunctionRunError, MyLock

# 这里设置服务启动相关设置,port=开放的端口,max_items=最大缓存数据条数,expire_sec=缓存超时时间(秒)
app = DeployClient(module_name=__name__, port=7778, max_items=1000, expire_sec=600)

# 这里进行模型的实例化或一些模型必要的加载和初始化工作
nlu = SVMNLU('usr', model_file=os.path.join(root_dir, 'res/svm_camrest_usr.zip'))
dst = RuleDST()
policy = Rule()
nlg = TemplateNLG(is_user=False)
# sys_agent = PipelineAgent(nlu, dst, policy, nlg)
sys_agent = PipelineAgent(None, dst, policy, None)
state_tracker_ini = copy.deepcopy(sys_agent.tracker.state)
state_policy_ini = copy.deepcopy(sys_agent.policy.policy.last_state)

model_lock = MyLock()


@app.inference_buffer('camrest_svm_rule_rule_temp')
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
    if 'post' not in input.keys() and 'da' not in input.keys():
        raise FunctionRunError('Missing argument in input')

    print('[opt: normal]')
    model_lock.enter()
    # 获得当前轮次的状态
    if buffer['states']:
        cur_state = buffer['states'][-1]
    else:
        print('ini new state')
        cur_state = copy.deepcopy({'tra': state_tracker_ini, 'pol': state_policy_ini})

    print('input state :' + str(cur_state))
    try:
        sys_agent.tracker.state = cur_state['tra']
        sys_agent.policy.policy.last_state = cur_state['pol']

        if 'da' in input.keys():
            dialog_act = input['da']
        else:
            dialog_act = nlu.predict(input['post'])

        action = sys_agent.response(dialog_act)
        resp = nlg.generate(action)

        buffer['states'].append({'tra': sys_agent.tracker.state, 'pol': sys_agent.policy.policy.last_state})
        new_buffer = copy.deepcopy(buffer)
    except Exception:
        raise FunctionRunError('running error')
    finally:
        model_lock.leave()

    print('output state:' + str(new_buffer))
    # back
    output = {'resp': resp, 'action': action}

    return output, new_buffer


if __name__ == '__main__':
    app.run()
