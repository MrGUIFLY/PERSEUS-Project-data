from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import OVSSwitch, RemoteController
import os
import subprocess
import threading
import time
import psutil
import matplotlib.pyplot as plt

def createNetwork():
    net = Mininet(controller=RemoteController, switch=OVSSwitch)
    net.addController('c0', ip='192.168.1.149', port=6653)
    
    switch1 = net.addSwitch('s1', intf='s1-eth0', cls=OVSSwitch, listenPort=6671, protocols='OpenFlow13', intfName='tun0')
    switch2 = net.addSwitch('s2', intf='s2-eth0', cls=OVSSwitch, listenPort=6671, protocols='OpenFlow13', intfName='tun0')
    switch3 = net.addSwitch('s3', intf='s3-eth0', cls=OVSSwitch, listenPort=6671, protocols='OpenFlow13', intfName='tun0')                   

    # Créez les hôtes clients
    client1 = net.addHost('client1', protocols='OpenFlow13', ip='10.0.0.2')
    client1.cmd('ip route add default via 10.0.0.1 dev client1-eth0')
    client2 = net.addHost('client2', protocols='OpenFlow13', ip='10.0.0.3')
    client2.cmd('ip route add default via 10.0.0.1 dev client2-eth0')
    client3 = net.addHost('client3', protocols='OpenFlow13', ip='10.0.0.4')
    client3.cmd('ip route add default via 10.0.0.1 dev client3-eth0')
    client4 = net.addHost('client4', protocols='OpenFlow13', ip='10.0.0.5')
    client4.cmd('ip route add default via 10.0.0.1 dev client4-eth0')
    attacker = net.addHost('attacker', protocols='OpenFlow13', ip='10.0.0.6')
    attacker.cmd('ip route add default via 10.0.0.1 dev attacker-eth0')
    
    net.addLink(client1, switch1, bp=10)
    net.addLink(client2, switch2, bp=10)
    net.addLink(client3, switch3, bp=10)
    net.addLink(client4, switch3, bp=10)
    net.addLink(switch1, switch2, bp=5)
    net.addLink(switch1, switch3, bp=5)
    net.addLink(switch2, switch3, bp=5)
    net.addLink(attacker, switch1, bp=10)
    net.start()
    
    # Exécutez les commandes OpenVPN sur les hôtes clients pour se connecter au serveur
    client1.cmd('openvpn --remote 10.0.0.1 --port 1194 --dev tun --proto tcp-client --remote-cert-tls server --ca /home/mr-guifly/vpn-config/server.crt --cert /home/mr-guifly/vpn-config/client.crt --key /home/mr-guifly/vpn-config/client.key --proto ipv4 &')
    client2.cmd('openvpn --remote 10.0.0.1 --port 1194 --dev tun --proto tcp-client --remote-cert-tls server --ca /home/mr-guifly/vpn-config/server.crt --cert /home/mr-guifly/vpn-config/client.crt --key /home/mr-guifly/vpn-config/client.key &')
    client3.cmd('openvpn --remote 10.0.0.1 --port 1194 --dev tun --proto tcp-client --remote-cert-tls server --ca /home/mr-guifly/vpn-config/server.crt --cert /home/mr-guifly/vpn-config/client.crt --key /home/mr-guifly/vpn-config/client.key &')
    
    # Test the connectivity between the hosts
    client1, client2 = net.get('client1', 'client2')
    result1 = client1.cmd('ping -c1 %s' % client2.IP())
    print(result1)
    result2 = client2.cmd('ping -c1 %s' % client1.IP())
    print(result2)
    result3 = client3.cmd('ping -c1 %s' % client2.IP())
    print(result3)
     
    client1.cmd('route add default gw 10.0.0.1')
    client2.cmd('route add default gw 10.0.0.1')
    client3.cmd('route add default gw 10.0.0.1')
    client4.cmd('route add default gw 10.0.0.1')

    return net, attacker, client1, client2, client3, client4

def monitor_resources(duration=60, interval=5):
    cpu_usage = []
    memory_usage = []
    timestamps = []

    end_time = time.time() + duration
    while time.time() < end_time:
        cpu_usage.append(psutil.cpu_percent(interval=interval))
        memory_usage.append(psutil.virtual_memory().percent)
        timestamps.append(time.time())
        time.sleep(interval)

    return timestamps, cpu_usage, memory_usage

def simulate_ddos_attack(attacker, target_ip, duration=30):
    end_time = time.time() + duration
    while time.time() < end_time:
        attacker.cmd(f'hping3 -S --flood -p 80 {target_ip}')
        time.sleep(1)

def simulate_memory_load(host, duration=30):
    end_time = time.time() + duration
    while time.time() < end_time:
        host.cmd('python3 -c "a = []\nfor i in range(1000000): a.append(i)"')
        time.sleep(1)

def main():
    setLogLevel('info')

    net, attacker, client1, client2, client3, client4 = createNetwork()

    # Monitor resources in a separate thread
    resource_monitor_thread = threading.Thread(target=monitor_resources, args=(60, 5))
    resource_monitor_thread.start()

    # Simulate DDoS attack
    attack_thread = threading.Thread(target=simulate_ddos_attack, args=(attacker, '10.0.0.1', 30))
    attack_thread.start()

    # Simulate memory load on clients
    memory_load_threads = [
        threading.Thread(target=simulate_memory_load, args=(client1, 60)),
        threading.Thread(target=simulate_memory_load, args=(client2, 60)),
        threading.Thread(target=simulate_memory_load, args=(client3, 60)),
        threading.Thread(target=simulate_memory_load, args=(client4, 60))
    ]
    for t in memory_load_threads:
        t.start()

    # Wait for threads to finish
    resource_monitor_thread.join()
    attack_thread.join()
    for t in memory_load_threads:
        t.join()

    # Collect resource usage data
    timestamps, cpu_usage, memory_usage = monitor_resources(60, 5)

    net.stop()

    # Plot resource usage
    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(timestamps, cpu_usage, label='CPU Usage (%)')
    plt.xlabel('Time (seconds)')
    plt.ylabel('CPU Usage (%)')
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(timestamps, memory_usage, label='Memory Usage (%)')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Memory Usage (%)')
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()

