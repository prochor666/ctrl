import re
import math
from slugify import slugify
from core import utils


def network(sample1, sample2, stats):
    devices_data = get_alive_devices(stats)
    devices = get_net_streams(devices_data, sample1, sample2)

    return devices


def get_net_streams(devices_data, sample1, sample2):
    lines1 = sample1.strip().split("\n")
    lines1.pop(0)
    lines2 = sample2.strip().split("\n")
    lines2.pop(0)
    streams = []

    for line in lines1:
        i = lines1.index(line)
        info1 = line.strip().split(':')
        info2 = lines2[i].strip().split(':')

        device_key = info1[0].strip()

        if device_key in devices_data:
            stream = parse_net_streams(info1[1], info2[1])

            streams.append({
                'device': device_key,
                'rx': devices_data[device_key]['RX'],
                'tx': devices_data[device_key]['TX'],
                'downstream': stream['downstream'],
                'upstream': stream['upstream'],
                'human_rx': utils.byte_size(int(devices_data[device_key]['RX'])),
                'human_tx': utils.byte_size(int(devices_data[device_key]['TX'])),
                'human_downstream': stream['human_downstream'],
                'human_upstream': stream['human_upstream']
            })

    return streams


def parse_net_streams(line1, line2):
    data1 = line1.strip().split()
    data2 = line2.strip().split()

    stream = {
        'downstream': (abs(int(data2[0]) - int(data1[0]))*8)/1000000,
        'upstream': (abs(int(data2[1]) - int(data1[1]))*8)/1000000,
        'human_downstream': utils.byte_size(abs(int(data2[0]) - int(data1[0]))),
        'human_upstream': utils.byte_size(abs(int(data2[1]) - int(data1[1])))
    }

    return stream


def get_alive_devices(stats):
    lines = stats.strip().split("\n")
    devices = {}
    index = 'none'

    for line in lines:
        reg = re.search(f"^Device|^RX|^TX", line)

        if reg is not None:
            info = line.split(':')
            key = str(info[0].strip())
            value = str(info[1].strip())

            if key == 'Device':
                value = str(value.split(' ')[0])
                index = value
            else:
                value = int(value.split(' ')[0])

            if index != 'none':

                if index not in devices:
                    devices[index] = {}

                devices[index][key] = value

    return devices



def storage(sample):
    lines = sample.strip().split("\n")
    stat = {}

    res = {
        'total': 0,
        'free': 0,
        'used': 0,
        'total_human': utils.byte_size(0),
        'free_human': utils.byte_size(0),
        'used_human': utils.byte_size(0),
    }

    if len(lines)>1:
        line = lines[1].split()
        total = int(line[1].strip())*1024
        free = int(line[3].strip())*1024
        used = int(line[2].strip())*1024

        res = {
            'total': total,
            'free': free,
            'used': used,
            'total_human': utils.byte_size(total),
            'free_human': utils.byte_size(free),
            'used_human': utils.byte_size(used),
        }

    return res


def memory(sample):
    lines = sample.strip().split("\n")
    stat = {}

    for line in lines:
        reg = re.search(f"^MemFree|^MemTotal|^Buffers|^Cached", line)
        #print(type(reg))
        if reg is not None:
            info = line.split(':')
            key = str(info[0].strip())
            value = str(info[1].strip())
            value = int(value.split(' ')[0])
            stat[key] = value*1024

    total = stat['MemTotal'] if 'MemTotal' in stat else 0
    _free = stat['MemFree'] if 'MemFree' in stat else 0
    _buffers = stat['Buffers'] if 'Buffers' in stat else 0
    _cached = stat['Cached'] if 'Cached' in stat else 0

    free = _free + _buffers + _cached
    used = total - free

    res = {
        'total': total,
        'free': free,
        'used': used,
        'total_human': utils.byte_size(total),
        'free_human': utils.byte_size(free),
        'used_human': utils.byte_size(used),
    }

    return res


def cpu(sample):
    lines = sample.strip().split("\n")
    cores = {}
    index = -1

    for line in lines:

        reg = re.search(f"^processor|^model name|^core id|^cpu MHz|^cache size", line)
        if reg is not None:
            info = line.split(':')
            key = slugify(str(info[0].strip()), separator='_')
            value = str(info[1].strip())
            value = str(value.split(' ')[0])

            if key == 'cpu_mhz':
                key = 'cpu_frequency'
                value = utils.decimal_size(math.ceil(float(value)*1000000))

            if key == 'processor':
                index = value
                cores[index] = {}

            cores[index][key] = value

    return cores


def cpu_load(sample1, sample2):
    stat1 = core_info(sample1)
    stat2 = core_info(sample2)
    cpu = cpu_percentage(stat1, stat2)
    return cpu


def core_info(sample):

    lines = sample.strip().split("\n")
    data = []
    for line in lines:
        reg = re.findall(f"^cpu[0-9]", line)

        if len(reg)>0:
            info = line.split()
            data.append({
                'user': info[1],
                'nice': info[2],
                'sys':  info[3],
                'idle': info[4]
            })

    return data


def cpu_percentage(stat1, stat2):

    if len(stat1) != len(stat2):
        return []

    cpus = []

    for s in stat1:
        cpu = {}
        i = stat1.index(s)

        dif = {
            'user': int(stat2[i]['user']) - int(s['user']),
            'nice': int(stat2[i]['nice']) - int(s['nice']),
            'sys': int(stat2[i]['sys']) - int(s['sys']),
            'idle': int(stat2[i]['idle']) - int(s['idle'])
        }
        total = sum(v for k, v in dif.items())

        for k, v in dif.items():
            cpu[k] = round(v/total*100, 1)

        cpus.append(cpu)

    return cpus
