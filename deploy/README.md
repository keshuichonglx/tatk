# Visualization Service Deployment

## 1. How to run
- Quick Model(DEBUG):

  ```bash
  python ./deploy/run.py
  ```

- Deployment Model(WSGI Http Server):
  > The related parameter usage method can be found in the [gunicorn documentation](https://docs.gunicorn.org/en/stable/run.html). An example is given below.

  ```bash
  gunicorn -b 0.0.0.0:8888 deploy.run:app --threads 4
  ```

## 2. How to configure
> All execution configuration parameters can be set in `deploy/dep_config.json`. This is a json file, and you need to follow the json writing specifications when editing.

### Network Field (`net`)

  - Description

  |KEY|DES|DEF|
  |:---|:---|:---:|
  |`port`|Backend service open port|_not default_|
  |`app_name`|Service access interface path name|_not default_|
  |`session_time_out`|The longest life cycle (seconds) in which a session is idle|600|

  - Example

  ```json
  "net":
  {
    "port": 8787,
    "app_name": "tatk",
    "session_time_out": 300
  }
  ```


### Module Field (`nlu`, `dst`, `policy`, `nlg`)
   > The candidate models can be configured under the key values of `nlu`, `dst`, `policy`, `nlg`. The model under each module needs to set a unique name as the key.

   - Description

   |KEY|DES|DEF|
   |:---|:---|:---:|
   |`class_path`|Target model class relative path|_not default_|
   |`data_set`|The data set used by the model|_not default_|
   |`ini_params`|The parameters required for the class to be instantiated|`{}`|
   |`model_name`|Model name displayed on the front end|model key|
   |`max_core`|The maximum number of cores this model allows to start|1|
   |`enable`|If false, the system will ignore this configuration|`true`

   - Example

   ```json
   "nlu":
   {
     "svm-cam":
     {
       "class_path": "tatk.nlu.svm.camrest.nlu.SVMNLU",
       "data_set": "camrest",
       "ini_params": {"mode": "usr"},
       "model_name": "svm",
       "max_core": 2,
       "enable": true
     },

     "my-model":
     {
       "class_path": "tatk.nlu.svm.multiwoz.nlu.xxx",
       "data_set": "multiwoz"
     }
   }
   ```

## 3. How to use
TODO: 前端使用部分
