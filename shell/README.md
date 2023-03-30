# 树莓派配置

## 树莓派AP模式

### 安装配置 hostapd 服务

Hostapd 是一个运行在用户态，提供热点访问和鉴权的服务端进程。

1. 安装服务：

```s
sudo apt install hostapd
sudo systemctl stop hostapd
```

2. 我们需要配置一下热点参数。配置文件地址在 `/etc/hostapd/hostapd.conf`，打开并编辑（如果没有这个文件的话，新建一个即可）

```s
sudo nano /etc/hostapd/hostapd.conf
```

写入如下配置项。注意要根据自己的实际情况，替换 ??? 处的内容：

```s
interface=wlan0
driver=nl80211
ssid=???            # WiFi 名称，8~64 个字符，最好用英文字母，不要出现特殊字符
hw_mode=???         # WiFi 网络模式，一般填 g 即可，设备支持的话可以填 a 启用 5G 频段
channel=???         # 信道编号
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=???  # WiFi 密码，最好用英文加数字，不要出现特殊字符
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
```

注意：

- 如果上面配置了 `hw_mode=g` 使用 2.4G 频段，则一般填 7 即可。如果配置了 5G 频段，则信道编号有所不同，具体参考：WLAN 信道列表
- WiFi 网络模式：
  - a = IEEE 802.11a (5 GHz)
  - b = IEEE 802.11b (2.4 GHz)
  - g = IEEE 802.11g (2.4 GHz)

配置项示例：

```s
interface=wlan0
driver=nl80211
ssid=raspberry_hotspot
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=12345678
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
```

3. 给 hostapd 指定我们刚刚配置的配置文件

打开 `/etc/default/hostapd` 这个文件，去掉 `DAEMON_CONF` 的注释，并配置成 `/etc/hostapd/hostapd.conf`，如图所示。意思就是告诉 `hostapd` 要从 `/etc/hostapd/hostapd.conf` 读取配置参数

4. 启动 hostapd 服务

```s
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd
```

如果服务启动失败，比如报错 `"systemctl status hostapd.service" and "journalctl -xe" for details` 等，可以按如下步骤逐一排查：

- 重启树莓派，再尝试启动 hostapd
- 命令行执行 `sudo /usr/sbin/hostapd /etc/hostapd/hostapd.conf`，直接运行 hostapd，观察输出日志，一般都能发现问题

比如常见的：

- `hostapd.conf` 配置错误导致启动失败。检查配置文件，修改后，新启动 hostapd 即可
- wlan0 端口未开启导致启动失败。执行 `sudo ifconfig wlan0 up` 开启端口后，重新启动 hostapd 即可

若看到 `"ENABLED"` 字样就表示启动成功了

*这个时候可能还是看不到热点了，但不用急，请继续下面的步骤*

5. 配置 wlan 静态 IP

用于 WiFi 热点的 `wlan0` 端口需要有固定的 IP 地址。假设树莓派热点的 IP 网段是 `192.168.4.x`，那么 wlan0 的 IP 就要设置成静态地址 `192.168.4.1` 。

树莓派以及大多数 Linux 发行版都由 dhcpcd 服务通过 DHCP（动态主机配置协议）获取自己的 IP 地址，所以这里我们要改掉 dhcpcd 的配置，让 wlan0 端口有静态 IP。

编辑 dhcpcd 配置文件：

```s
sudo nano /etc/dhcpcd.conf
```

```s
interface wlan0
static ip_address=192.168.4.1/24
nohook wpa_supplicant
```

编辑 dhcpcd 配置文件：
```s
sudo nano /etc/dhcpcd.conf
```

在文件末尾添加：
```s
interface wlan0
static ip_address=192.168.4.1/24
nohook wpa_supplicant
```

保存后，如果你是用ssh登陆，不建议这时重启 dhcpcd 服务，因为开启热点会占用WiFi网卡的口，使树莓派与原本连接的WiFi断开，进而导致ssh断开

重启 dhcpcd 服务：
```s
sudo systemctl restart dhcpcd
```

执行 `ifconfig` 可以看到，wlan0 的 IP 地址已经固定成 `192.168.4.1` 了。

6. 安装配置 dnsmasq 服务
dnsmasq 是一个小型的用于配置 DNS 和 DHCP 的工具，适用于小型网络，它提供了 DNS 和 DHCP 功能。

**首先安装 dnsmasq 服务。**

```s
sudo apt install dnsmasq
sudo systemctl stop dnsmasq
```

**接着，配置 dnsmasq 参数。**打开 `/etc/dnsmasq.conf` 配置文件，把里面的其他内容都注释掉，添加新的配置项：

```s
sudo nano /etc/dnsmasq.conf
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
```

```s
sudo nano /etc/dnsmasq.conf
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
```

dhcp-range 配置项的意思是，dhcp 服务会给客户端分配 `192.168.4.2` 到 `192.168.4.20` 的 IP 空间，24 小时租期。

**然后，重启 dnsmasq 服务。**

```s
sudo systemctl reload dnsmasq
```

此时用设备去连接热点，就能看到成功分配了动态 IP。

7. 配置 IP 包转发

上面我们给树莓派安装了 hostapd 热点服务 和 dnsmasq DHCP 服务，已经可以让手机连接 WiFi 热点并分配到动态 IP 了，但仍不能联网，所以现在就剩最后一步：给树莓派配置 IP 包转发，让手机连接 WiFi 后能正常上网。

**首先，开启 Linux 内核的 ip 转发功能。**
> 打开 /etc/sysctl.conf 系统配置文件，去掉 net.ipv4.ip_forward=1 这个配置项的注释：
出于安全考虑，Linux系统默认是禁止数据包转发的。所谓转发即当主机拥有多于一块的网卡时，其中一块收到数据包，根据数据包的目的ip地址将数据包发往本机另一块网卡，该网卡根据路由表继续发送数据包。这通常是路由器所要实现的功能。
要让Linux系统具有路由转发功能，需要配置一个Linux的内核参数net.ipv4.ip_forward。这个参数指定了Linux系统当前对路由转发功能的支持情况；其值为0时表示禁止进行IP转发；如果是1,则说明IP转发功能已经打开。

然后，修改 Linux 防火墙规则，完成报文源地址目标转换。

>其中 usb0 为 L610 给树莓派提供的网卡，可自由调整

```s
sudo iptables -t nat -A  POSTROUTING -o usb0 -j MASQUERADE
```

**接着，设置开机自动导入防火墙规则。**

```s
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"
```

编辑 `/etc/rc.local`，把 `iptables-restore < /etc/iptables.ipv4.nat` 加到最后一行 exit 0 的前面：

然后，重启树莓派：

```s
sudo reboot
```

重启树莓派后，手机连接树莓派热点。一切正常的话，手机就可以 WiFi 上网了。

## 树莓派开机自启动设置

1. 脚本代码

自启 L610网卡，树莓派上云 start_up.sh

```s
# wait for system boot
sleep 15s

# set tty_usb0
sudo modprobe option
sudo sh -c 'echo " 1782 4d11" > /sys/bus/usb-serial/drivers/option1/new_id'
# remove lock file
sudo rm /var/lock/LCK..ttyUSB0

# kill last minicom
pkill -f minicom

# open screen
pkill -f "SCREEN -dmS minic"
screen -dmS minic

# input command
screen -S minic -p 0 -X stuff "minicom^M"
sleep 1s
screen -S minic -p 0 -X stuff "AT+GTUSBMODE=32^M"
sleep 1s
screen -S minic -p 0 -X stuff "AT+CGDCONT=2,\"IP\",\"CMNET\"^M"
sleep 1s
screen -S minic -p 0 -X stuff "AT+GTRNDIS=1,2^M"

# start mqtt proxy
screen -dmS proxy
screen -S proxy -p 0 -X stuff "cd ~/SmartElectricPile-Proxy^M"
screen -S proxy -p 0 -X stuff "python main.py"

# exit
# pkill -f minicom
# pkill -f "SCREEN -dmS minic"

# end
echo done!
```

自启热点 开启树莓派AP模式 ap_start.sh

```s
sleep 10s

# start hostapd
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd

# restart dhcpcd
sudo systemctl restart dhcpcd

# restart dnsmasq
sudo systemctl reload dnsmasq

# config iptable
sudo iptables -t nat -A  POSTROUTING -o eth0 -j MASQUERADE

# import firewall rule
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"
```

2. 可能的问题
在设置 L610 的开机自启时可能会由于上次的不正常退出导致 usb 口被锁死，可以在脚本中加入如下内容来解开

```s
sudo rm /var/lock/LCK..ttyUSB0
```

>注意为防止开机时程序阻塞，可以在脚本中加入sleep来延后脚本的执行