# 智慧电桩网关代码

## 警告

**本项目仅为比赛用，其使命已经完成，故公开存档留作学习或纪念。请不要试图部署运行！另外项目中所储存的信息（例如设备ID等）均已注销，仅做纪念**

## 环境配置

### 树莓派配置

<!-- TODO -->

#### 自启动脚本

自启动脚本可参考 [shell](./shell/) 目录下的文件以及 README

### Python

安装以下 pip 包

```shell
$ pip install picamera paho-mqtt numpy
```

### DEVICES-KEY.bib

`DEVICES-KEY.bib` 是在**华为 IoTDA** 申请设备时会下发的一个文件，唯一标识了一台设备，并附有密钥。请把该文件放在根目录下方便配置读取，*并且不要将其上传至公开仓库*

### 语音播报

在 `config.py` 中的 `voice player settings` 部分，特别是语音文件的根目录、语音文件名，都需要自行填写，并提前准备好

## 使用

### 运行

**强烈建议在 Screen 中开启网关程序！**

```shell
$ cd path/to/root
$ python main.py
```

### 可选参数

`--log` 或 `-d`：打印日志
`--test` 或 `-t`：测试模式，不导入树莓派专属的模块，方便在 windows/linux 环境下调试
