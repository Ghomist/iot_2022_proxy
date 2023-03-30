# 智慧电桩网关代码

## 环境配置

### 树莓派配置

<!-- TODO -->
树莓派AP模式
write by boxiao
sudo nano /etc/dnsmasq.conf
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
dhcp-range 配置项的意思是，dhcp 服务会给客户端分配 192.168.4.2 到 192.168.4.20 的 IP 空间，24 小时租期。
然后，重启 dnsmasq 服务。
sudo systemctl reload dnsmasq
此时用设备去连接热点，就能看到成功分配了动态 IP。
配置 IP 包转发
上面我们给树莓派安装了 hostapd 热点服务 和 dnsmasq DHCP 服务，已经可以让手机连接 WiFi 热点并分配到动态 IP 了，但仍不能联网，所以现在就剩最后一步：给树莓派配置 IP 包转发，让手机连接 WiFi 后能正常上网。
首先，开启 Linux 内核的 ip 转发功能。打开 /etc/sysctl.conf 系统配置文件，去掉 net.ipv4.ip_forward=1 这个配置项的注释：
出于安全考虑，Linux系统默认是禁止数据包转发的。所谓转发即当主机拥有多于一块的网卡时，其中一块收到数据包，根据数据包的目的ip地址将数据包发往本机另一块网卡，该网卡根据路由表继续发送数据包。这通常是路由器所要实现的功能。
要让Linux系统具有路由转发功能，需要配置一个Linux的内核参数net.ipv4.ip_forward。这个参数指定了Linux系统当前对路由转发功能的支持情况；其值为0时表示禁止进行IP转发；如果是1,则说明IP转发功能已经打开。
然后，修改 Linux 防火墙规则，完成报文源地址目标转换。
其中 usb0 为 L610 给树莓派提供的网卡，可自由调整
sudo iptables -t nat -A  POSTROUTING -o usb0 -j MASQUERADE
接着，设置开机自动导入防火墙规则。
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"
编辑 /etc/rc.local，把 iptables-restore < /etc/iptables.ipv4.nat 加到最后一行 exit 0 的前面：
然后，重启树莓派：
sudo reboot
重启树莓派后，手机连接树莓派热点。一切正常的话，手机就可以 WiFi 上网了。
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