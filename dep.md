# 1. 部署地址
|  模块  |  地址  | 状态  | 其他 |
| :--- |  :--- | :--- |  :--- |
| 后台DEMO中控 | 166.111.7.192:9999 | 已部署 | http://coai.cs.tsinghua.edu.cn/deploy |
| DEMO:chat | 118.192.65.44:9999 | 已部署 ||
| DEMO:multiwoz_svm_rule_rule_temp | 115.182.62.169:7777 | 已部署 | |
| DEMO:camrest_svm_rule_rule_temp | 115.182.62.169:7778 | 部署中 | |

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

## 2.2 multiwoz_svm_rule_rule_temp
model = multiwoz_svm_rule_rule_temp

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

## 2.3 camrest_svm_rule_rule_temp
model = camrest_svm_rule_rule_temp

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