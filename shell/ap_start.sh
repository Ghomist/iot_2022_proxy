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