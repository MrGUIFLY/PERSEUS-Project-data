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
    
    # Initialisation du temps de départ
    start_time = time.time()

    end_time = start_time + duration
    while time.time() < end_time:
        cpu_usage.append(psutil.cpu_percent(interval=interval))
        memory_usage.append(psutil.virtual_memory().percent)
        timestamps.append(time.time() - start_time)  # Utilisation du temps écoulé
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
        host.cmd('dd if=/dev/zero of=/dev/null bs=1M count=100')
        time.sleep(1)

def measure_response_time(client, server_ip, duration=30):
    response_times = []
    timestamps = []
    start_time = time.time()

    end_time = start_time + duration
    while time.time() < end_time:
        response_time = client.cmd(f'curl -o /dev/null -s -w "%{{time_total}}" http://{server_ip}')
        response_times.append(float(response_time))
        timestamps.append(time.time() - start_time)
        time.sleep(1)

    return timestamps, response_times

def main():
    setLogLevel('info')

    net, attacker, client1, client2, client3, client4 = createNetwork()

    # Start a simple HTTP server on client1
    client1.cmd('python3 -m http.server 80 &')

    # Measure response time before attack
    timestamps_before, response_times_before = measure_response_time(client2, client1.IP(), 60)

    # Simulate DDoS attack
    attack_thread = threading.Thread(target=simulate_ddos_attack, args=(attacker, client1.IP(), 30))
    attack_thread.start()

    # Measure response time during attack
    timestamps_during, response_times_during = measure_response_time(client2, client1.IP(), 30)

    # Wait for the attack to finish
    attack_thread.join()

    # Plot response times
    plt.figure()
    plt.plot(timestamps_before, response_times_before, label='Response Time (Before DDoS)')
    plt.plot(timestamps_during, response_times_during, label='Response Time (During DDoS)', linestyle='--')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Response Time (seconds)')
    plt.legend()

    plt.tight_layout()
    plt.show()

    net.stop()


if __name__ == '__main__':
    main()

