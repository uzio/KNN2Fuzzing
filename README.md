<<<<<<< HEAD
# KNN2Fuzzing
Screening seeds with fastKNN for kitty frame based fuzzing
=======
## 开发环境安装步骤

系统环境为Ubuntu18.04

- 192.168.1.188 西门子  S7-1200 PLC
- 192.168.1.172 施耐德 bmx M340 PLC
- 192.168.1.189 欧姆龙 cj2m PLC
-  iface = wlx3c46d8d8ef65  //  数据报文发送的接口 ，可以使用 lo
-  monitor_iface = lo 		    //	抓包的接口

1. 安装node

```shell
sudo apt update
sudo apt install nodejs
sudo apt install npm
```

2. 进入frontend目录，执行`npm install`安装前端相关依赖。
3. 返回Fuzz目录，创建python虚拟环境，目前运行环境中python版本为2.7

```shell
不能使用sudo,确保在当前用户环境下运行Fuzz
pip install virtualenv
virtualenv -p /usr/bin/python2.7 venv
source venv/bin/activate

```

4. 安装python依赖，`pip install -r requirement.txt`
5. 安装MongoDB，参考[Install MongoDB Community Edition](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/#install-mongodb-community-edition)

```shell
wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.2.list
sudo apt-get update
sudo apt-get install -y mongodb-org
```

6. 安装Redis，参考[How To Install and Secure Redis on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-18-04)

## 运行程序

### 开发阶段

1. `cd /home/icdm/Fuzz/frontend 执行 npm run dev`，开始开发模式的前端编译，每次前端代码更改都会引起浏览器中页面重绘。

2. `venv/bin/python app.py`，执行后端代码

3. `sudo venv/bin/python runner.py` ，runner脚本中从mongodb的jobs集合中取任务，然后执行对应的测试用例脚本。

4. `venv/bin/rq worker scan`，在漏洞扫描任务中，创建执行zgrab2对目标IP进行设备信息获取以及漏洞匹配工作。
5. 修改 zgrab和模糊测试的pcap文件路径 /home/icdm/Fuzz/ics.ini ，并执行 `venv/bin/python app.py + sudo venv/bin/python runner.py`\n
   scanner = /home/icdm/Fuzz/zgrab2
   scan_config_path = /home/icdm/Fuzz
6.  修改 /home/icdm/Fuzz/runner.py 中 `params['INTERFACE'] = 'xxxx'` xxx为自己的网卡名称如 ifconfig : eno1,并重启` sudo venv/bin/python runner.py`
7.  漏洞演示脚本 Fuzz/snap7_vul.py

### 部署阶段

1. `npm run build`，该命令在frontend目录下创建`dist`目录，该目录存放了前端相关静态资源和前端页面。
2. 将dist目录复制到Fuzz目录下，也就是和后端放在统一目录中。

剩下的步骤与开发阶段相同。



## 项目结构

```
-frontend 前端相关代码
-cases 测试用例脚本
	-arp ARP协议测试用例脚本
	-cip CIP协议测试用例脚本
	-dnp3
	-ethip
	...
-protocols 协议实现，用于模糊测试数据包生成 
-kitty Kittyfuzzer工具源代码，在此基础上进行修改
-kitnap Kittyfuzzer工具对不同测试对象工具的实现
-workstation 提供给前端的接口
app.py 后端接口主程序
ics_fuzzer.py 用于替代Kittyfuzzer工具自带的fuzzer，主要用于将测试进度保存在Mongodb
ics_logger.py 自定义日志记录函数
runner.py 该脚本单独运行从Mongodb中取出待运行的任务，然后运行任务所需要的测试用例脚本

-scan_vuls 使用zgrab2识别设备信息
-scan_modules 使用不同协议的设备信息对漏洞库进行文本搜索，以此获得该设备漏洞
zgrab2 可执行文件，由zgrab2项目中编译生成
ics.ini 配置文件，主要用于漏洞扫描任务
hardware.ini 配置文件，主要用于设备识别
```


### 测试用例脚本

测试用例脚本在Kittyfuzzer以及Scapy工具的基础上实现，每个测试用例脚本包含INFO字典、fuzz函数。

- INFO字典：包含这个测试用例的名称title、描述des、id、类型type、创建人creator、创建时间create_time、测试协议protocol。
- fuzz函数：使用params字典作为参数。在函数中首先使用scapy工具提供的协议字段原语构建报文对象（packet），然后将报文对象放入Template中，这里之所以Scapy能与Kitty共同使用，是因为Kitty中实现了ScapyField字段。最后fuzz函数内构建GraphModel，kitty框架根据图模型将报文发向`params['TARGET_IP']`指定的被测目标设备IP地址。

params字典需要传入fuzz函数中包括以下字段：

```python
params={
    'FUZZ_COUNT':2,
	'DELAY':1,
    'TARGET_IP':'192.168.1.189',
    'TIME_OUT':2,
}
```

测试用例脚本在cases文件中

```python
INFO = {
    'title':'PLC Run,模糊 Service_ID',
    'des':  'PLC Run,模糊 Service_ID',
    'id':   '2',
    'type': '1',
    'creator': 'liuyongpan',
    'create_time': '05/04/2019',
    'protocol':'omron_fins'
}

def fuzz(params):

    Packet = OMRON_Header(Service_ID=RandByte(),Command_code=0x0401)
    template = Template(name='PLC Run,模糊 Service_ID', fields=[
        ScapyField(Packet,
                   name='template',
                   fuzzable=True,
                   seed=RANDSEED,
                   fuzz_count=params['FUZZ_COUNT']
                   ),
    ])


    model = GraphModel()
    model.connect(template)
    modbus_target = UdpTarget(name='modbus target', host= params['TARGET_IP'], port=9600, timeout=params['TIME_OUT'])
    modbus_target.set_expect_response(True)
    fuzzer = ICSFuzzer(params)
    fuzzer.set_interface(EmptyInterface())
    fuzzer.set_model(model)
    fuzzer.set_target(modbus_target)
    fuzzer.set_delay_between_tests(params['DELAY'])
    fuzzer.set_skip_env_test(True)
    fuzzer.start()
    fuzzer.stop()
```

### runner.py

`CaseRunner`类，运行测试用例脚本。

## 测试流程

首先运行`runner.py`脚本，该脚本不断从mongodb的fuzz数据库的jobs Collections中取出任务。

然后我们需要在前端页面中，创建相关任务，在任务创建页面添加测试用例以及测试目标IP地址。

## 后端接口

后端主要从`app.py`作为入口开始，各个页面所需要的接口通过`register_blueprint`注册

后端依赖的包：

```python
backports.functools-lru-cache==1.6.1
beautifulsoup4==4.9.0
broadlink==0.13.1
certifi==2020.4.5.1
cffi==1.14.0
chardet==3.0.4
click==7.1.1
cryptography==2.9
enum34==1.1.10
Flask==1.1.2
Flask-Cors==3.0.8
idna==2.9
ipaddress==1.0.23
itsdangerous==1.1.0
Jinja2==2.11.2
MarkupSafe==1.1.1
pkg-resources==0.0.0
pycparser==2.20
pymongo==3.10.1
redis==3.4.1
requests==2.23.0
rq==1.3.0
six==1.14.0
soupsieve==1.9.5
urllib3==1.25.9
Werkzeug==1.0.1
```



## 测试用例

测试用例存放地址 `vuls/<protocol>/<用例>.py`

## 依赖
`kitty`
`katnip`
`pycrypto`

## 漏洞搜索

需要对mongodb的vulnerability添加全文索引使用`db.vulnerability.createIndex( { "$**" : "text" } )`全文索引，
`$**`：通配符，索引所有字段。 

## 前端

前端主要在`frontend`文件夹，其中各文件内容如下：

```shell
assets 存放图片
icons 存放图标矢量图
Layout 存放布局组件
shared 通用组件
stores 前端保存的数据
styles 公用css设定
utils 通用工具
views 各个页面组件
router.js 路由设置
```

## 问题汇总
1. 
``` 
Traceback (most recent call last): File "/home/icdm/Fuzz/kitty/targets/server.py", line 93, in transmit self._send_to_target(payload) File "/home/icdm/Fuzz/katnip/targets/arp.py", line 48, in _send_to_target sock = conf.L2socket(iface='en0') File "/home/icdm/Fuzz/venv/local/lib/python2.7/site-packages/scapy/arch/linux.py", line 477, in __init__ set_promisc(self.ins, self.iface) File "/home/icdm/Fuzz/venv/local/lib/python2.7/site-packages/scapy/arch/linux.py", line 165, in set_promisc mreq = struct.pack("IHH8s", get_if_index(iff), PACKET_MR_PROMISC, 0, b"") File "/home/icdm/Fuzz/venv/local/lib/python2.7/site-packages/scapy/arch/linux.py", line 380, in get_if_index return int(struct.unpack("I", get_if(iff, SIOCGIFINDEX)[16:20])[0]) File "/home/icdm/Fuzz/venv/local/lib/python2.7/site-packages/scapy/arch/common.py", line 59, in get_if ifreq = ioctl(sck, cmd, struct.pack("16s16x", iff.encode("utf8"))) IOError: [Errno 19] No such device 
```
需要修改 /home/icdm/Fuzz/katnip/targets/arp.py 中 sock = conf.L2socket(iface='en0') 中 en0为自己的网卡名称 eth0
然后执行 sudo venv/bin/python runner.py 
备注：所有的测试用例都是由runner执行

2. 测试snap7时需要确保所在的网络是Lab501 才能使用 192.168.1.142，其他网络环境亦然。
>>>>>>> 27cbda7 (knn for fuzzing)
