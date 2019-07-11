#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    :   dep_svm_rule_rule_temp
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
from tatk.nlu.svm.multiwoz import SVMNLU
from tatk.dst.rule.multiwoz import RuleDST
from tatk.policy.rule.multiwoz import Rule
from tatk.nlg.template_nlg.multiwoz import TemplateNLG

from DeployClient import DeployClient, FunctionRunError, MyLock

# 这里设置服务启动相关设置,port=开放的端口,max_items=最大缓存数据条数,expire_sec=缓存超时时间(秒)
app = DeployClient(module_name=__name__, port=7777, max_items=1000, expire_sec=600)

'''
# 这里进行模型的实例化或一些模型必要的加载和初始化工作
nlu = SVMNLU('usr', model_file=os.path.join(root_dir, 'res/svm_multiwoz_usr.zip'))
dst = RuleDST()
policy = Rule()
nlg = TemplateNLG(is_user=False)
sys_agent = PipelineAgent(nlu, dst, policy, nlg)
state_ini = copy.deepcopy(sys_agent.tracker.state)

model_lock = MyLock()


@app.inference_buffer('multiwoz_svm_rule_rule_temp')
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
        sys_agent.tracker.state = buffer
        reqt = sys_agent.response(input['post'])
        new_buffer = copy.deepcopy(sys_agent.tracker.state)
    except Exception:
        raise FunctionRunError('running error')
    finally:
        model_lock.leave()

    print('output state:' + str(new_buffer))
    # back
    output = {'reqt': reqt}

    return output, new_buffer
'''
# 这里进行模型的实例化或一些模型必要的加载和初始化工作
nlu = SVMNLU('usr', model_file=os.path.join(root_dir, 'res/svm_multiwoz_usr.zip'))
policy = Rule()
nlg = TemplateNLG(is_user=False)
state_ini = copy.deepcopy(RuleDST().state)


@app.inference_buffer('multiwoz_svm_rule_rule_temp')
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
    dst = RuleDST()
    sys_agent = PipelineAgent(nlu, dst, policy, nlg)
    try:
        sys_agent.tracker.state = buffer
        resp = sys_agent.response(input['post'])
        new_buffer = copy.deepcopy(sys_agent.tracker.state)
    except Exception:
        raise FunctionRunError('running error')

    print('output state:' + str(new_buffer))
    # back
    output = {'resp': resp}

    return output, new_buffer


if __name__ == '__main__':
    app.run()
