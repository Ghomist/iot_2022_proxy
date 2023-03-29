# 配置流程

## 参考

[知乎文章《从零开始：树莓派共享 WiFi 秒变无线热点（树莓派路由器》](https://zhuanlan.zhihu.com/p/102598741)

## 快速流程

该快速流程无原理解释，具体可直接找参考的那一篇文章

```s
$ sudo apt install hostapd
$ sudo systemctl stop hostapd
```

<!-- hostapd.conf 配置

-   ssid: WiFi 名称，8~64 个字符，最好用英文字母，不要出现特殊字符
-   hw_mode: WiFi 网络模式，一般填 g 即可，设备支持的话可以填 a 启用 5G 频段：
    -   a = IEEE 802.11a (5 GHz)
    -   b = IEEE 802.11b (2.4 GHz)
    -   g = IEEE 802.11g (2.4 GHz)
-   channel: 信道编号。如果上面配置了 hw_mode=g 使用 2.4G 频段，则一般填 7 即可。如果配置了 5G 频段，则信道编号有所不同，具体参考：[WLAN 信道列表](https://zh.wikipedia.org/wiki/WLAN%E4%BF%A1%E9%81%93%E5%88%97%E8%A1%A8)
-   wpa_passphrase: WiFi 密码，最好用英文加数字，不要出现特殊字符 -->

```s
$ sudo nano /etc/hostapd/hostapd.conf
> modify
interface=wlan0
driver=nl80211
ssid=???                    # e. g. raspberry_wifi
hw_mode=???                 # e. g. g
channel=???                 # e. g. 7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=???          # e. g. 12345678
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
```

```s
$ sudo nano /etc/default/hostapd
> modify
DAEMON_CONF="/etc/hostapd/hostapd.conf"
```

```s
$ sudo nano /etc/dhcpcd.conf
> append
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
```

```s
$ sudo apt install dnsmasq
$ sudo systemctl stop dnsmasq
```

```s
$ sudo nano /etc/dnsmasq.conf
> append (注释掉其它的)
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
```

```s
$ sudo nano /etc/sysctl.conf
> modify
net.ipv4.ip_forward=1
```
