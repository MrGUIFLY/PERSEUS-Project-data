from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import OVSSwitch, RemoteController
import os
import subprocess

def createNetwork():
    net = Mininet(controller=RemoteController, switch=OVSSwitch)
    net.addController('c0', ip='192.168.1.149', port=6653)
    switch1 = net.addSwitch('s1', intf='s1-eth0', cls=OVSSwitch, listenPort=6671, protocols='OpenFlow13',
                   intfName='tun0')
    switch2 = net.addSwitch('s2', intf='s2-eth0', cls=OVSSwitch, listenPort=6671, protocols='OpenFlow13',
                   intfName='tun0')
    switch3 = net.addSwitch('s3', intf='s3-eth0', cls=OVSSwitch, listenPort=6671, protocols='OpenFlow13',
                   intfName='tun0')                   

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
    client4.cmd('ip route add default via 10.0.0.1 dev attacker-eth0')
    
    net.addLink(client1, switch1, bp=10)
    net.addLink(client2, switch2, bp=10)
    net.addLink(client3, switch3, bp=10)
    net.addLink(client4, switch3, bp=10)
    net.addLink(switch1, switch2, bp=5)
    net.addLink(switch1, switch3, bp=5)
    net.addLink(switch2, switch3, bp=5)
    net.addLink(attacker, switch1, bp=10)
    net.start()
    
    
    # Start web server on h1
    h1.cmd('python3 -m http.server 80 &')

    return net, client1, client2, attacker
    
    # Exécutez les commandes OpenVPN sur les hôtes clients pour se connecter au serveur
    client1.cmd('openvpn --remote 10.0.0.1 --port 1194 --dev tun --proto tcp-client  --remote-cert-tls server --ca /home/mr-guifly/vpn-config/server.crt --cert /home/mr-guifly/vpn-config/client.crt --key /home/mr-guifly/vpn-config/client.key --proto ipv4')
    client2.cmd('openvpn --remote 10.0.0.1 --port 1194 --dev tun --proto tcp-client --remote-cert-tls server --ca /home/mr-guifly/vpn-config/server.crt --cert /home/mr-guifly/vpn-config/client.crt --key /home/mr-guifly/vpn-config/client.key')
    client3.cmd('openvpn --remote 10.0.0.1 --port 1194 --dev tun --proto tcp-client --remote-cert-tls server --ca /home/mr-guifly/vpn-config/server.crt --cert /home/mr-guifly/vpn-config/client.crt --key /home/mr-guifly/vpn-config/client.key')
    

    
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

    
# Configuration et activation du tunnel VPN
#    os.system('sudo ifconfig tun0 10.0.0.1 netmask 255.255.255.0 up')
    
# Configuration de la route par défaut via tun0
#    os.system('sudo ip route add default dev tun0')


# Exécute la commande "ls" dans le répertoire courant et récupère la sortie
    result = subprocess.check_output("ls")
    print(result)

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    createNetwork()
