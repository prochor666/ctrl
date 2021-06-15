import time
import datetime
import socket
from core.ctrl import device


def device_ip():

    netifs = device.network_info()
    ips = []
    for netif in netifs:
        # if netifs[netif]['ipv4'] != '-':
        #    ips.append(netifs[netif]['ipv4'])
        ips.append(netifs[netif]['ipv4'])
        ips.append(netifs[netif]['ipv6'])
    return ips


def ssh_port():
    return 22


def scan():
    ips = device_ip()
    result = []
    for itype, ip in ips.items():
        result.append(scan_ip(ip))

    return result


def scan_ip(ip, ports=[21, 22, 80, 443, 3306]):
    start_time = time.time()
    ip_target = str(ip)
    ttl = 5
    result = {
        'ports': {},
        'scan_result': 'Failed, no init',
        'scan_status': False,
        'time': 0
    }

    try:
        for port in ports:

            port = int(port)
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(ttl)
                scan_result = sock.connect_ex((ip_target, port))

                if scan_result == 0:
                    result['ports'][port] = True
                else:
                    result['ports'][port] = False
                sock.close()

            except Exception as e:
                result['ports'][port] = "Exception type %s" % (e)

        result['scan_result'] = 'Scanned'
        result['scan_status'] = True

    except KeyboardInterrupt:
        result = {
            'ports': {},
            'scan_result': 'You pressed Ctrl+C',
            'scan_status': False,
            'time': 0
        }

    delta = time.time() - start_time
    result['time'] = str(datetime.timedelta(seconds=delta))
    return result
