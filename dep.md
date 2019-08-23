# 1. 部署地址
|  模块  |  地址  | 状态  | 其他 |
| :--- |  :--- | :--- |  :--- |
| 后台DEMO中控 | 166.111.7.192:9999 | 已部署 | http://coai.cs.tsinghua.edu.cn/deploy |
| DEMO:chat | 118.192.65.44:9999 | 已部署 ||
| DEMO:multiwoz_svm_rule_rule_temp | 115.182.62.169:7777 | 已部署 | |
| DEMO:camrest_svm_rule_rule_temp | 115.182.62.169:7778 | 已部署 | |
| DEMO:multiwoz_sequicity | 115.182.62.169:7781 | 已部署 | |
| DEMO:camrest_sequicity | 115.182.62.169:7782 | 已部署 | |
| DEMO:multiwoz_mdbt_rule_temp | 115.182.62.169:7790 | 已部署 | |
| DEMO:multiwoz_bert_rule_rule_temp | 115.182.62.169:7779 | 已暂停 | |
| DEMO:camrest_bert_rule_rule_temp | 115.182.62.169:7780 | 已暂停 | |


# 2. 接口
## 2.0 基本约定
- **协议**
post，application/json

- **服务调用接口**
    - http://coai.cs.tsinghua.edu.cn/deploy
    - 参数：model - 需要调用的模, token - 会话唯一标识
```
例：
http://coai.cs.tsinghua.edu.cn/deploy?model=multiwoz_svm_rule_rule_temp&token=2349237492sdufih947
```
- **错误返回**
当出现不正确的后台处理时，返回的json数据不再是模型约定的返回结果，而是包含"Error"和"ErrorMsg"的json数据返回。
例：
```json
{
	"Error": "UNKNOW_MODEL",
	"ErrorMsg": "Unknow Model : multiwoz_svm_rule_ddd_temp"
}
```

## 2.1 对话框架DEMO
model = chat

**发送**
```json
{
    "utterance": "post utterance"
}
```

**返回**
```json
{
	"bot": "xxxx",
	"emotion": "None",
	"token": "xxxxx",
	"utterance": "request utterance"
}
```

## 2.2 multiwoz and camrest DEMO

### 2.2.1 文本 -> 文本
**model**
- multiwoz_sequicity
- camrest_sequicity

**发送**
```json
{
    "post": "post utterance"
}
```

**返回**
```json
{
    "resp": "request utterance"
}
```

### 2.2.2 文本 -> 文本 + sys_da
**model**
- multiwoz_mdbt_rule_temp

**发送**
```json
{
    "post": "post utterance"
}
```

**返回**
```json
{
    "resp": "request utterance",
    "sys_da": {...}
}
```

### 2.2.3 文本 or usr_da -> 文本 + sys_da + usr_da
**model**
- multiwoz_svm_rule_rule_temp
- camrest_svm_rule_rule_temp

**发送**
```json
{
    "post": "post utterance"
}
or
{
    "usr_da": {...}
}
```

**返回**
```json
{
    "resp": "request utterance",
    "sys_da": {...},
    "usr_da": {...}
}
```

### 2.2.4 recall
**model**
- multiwoz_sequicity
- camrest_sequicity
- multiwoz_svm_rule_rule_temp
- camrest_svm_rule_rule_temp
- multiwoz_mdbt_rule_temp

**发送**
```json
{
    "recall": true
}
```

**返回**
```json
{
    "turns": n
}
```
n为剩余可回滚轮次

# 20190815 模型部署增加功能支持
|model|da输入|action输出|recall|
|:---|:---|:---|:---|
|multiwoz_sequicity|`no`|`no`|`yes`|
|camrest_sequicity|`no`|`no`|`yes`|
|multiwoz_svm_rule_rule_temp|`yes`|`yes`|`yes`|
|camrest_svm_rule_rule_temp|`yes`|`yes`|`yes`|
|multiwoz_mdbt_rule_temp|`no`|`yes`|`yes`|