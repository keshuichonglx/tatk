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

root_dir = os.path.dirname(__file__)
sys.path.insert(0, root_dir)
from tatk.dialog_agent import PipelineAgent, BiSession
from tatk.nlu.svm.multiwoz.nlu import SVMNLU
from tatk.dst.rule import RuleDST
from tatk.policy.rule.multiwoz.rule import Rule
from tatk.nlg.template_nlg.multiwoz.multiwoz_template_nlg import MultiwozTemplateNLG

nlu = SVMNLU('usr', model_file=os.path.join(root_dir, 'res/svm_multiwoz_usr.zip'))
dst = RuleDST()
policy = Rule()
nlg = MultiwozTemplateNLG(is_user=False)
sys_agent = PipelineAgent(nlu, dst, policy, nlg)
