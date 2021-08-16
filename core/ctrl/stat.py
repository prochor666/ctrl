import re
from core import utils

def memory(sample):
    lines = sample.split("\n")
    stat = {}

    for line in lines:
        reg = re.search(f"^MemFree|^MemTotal|^Buffers|^Cached", line)
        #print(type(reg))
        if reg is not None:
            info = line.split(':')
            key = str(info[0].strip())
            value = info[1].strip()
            value = int(value.split(' ')[0])
            stat[key] = value*1024


    total = stat['MemTotal']
    free = stat['MemFree'] + stat['Buffers'] + stat['Cached']
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


def cpu(sample1, sample2):
    stat1 = core_info(sample1)
    stat2 = core_info(sample2)
    cpu = cpu_percentage(stat1, stat2)
    return cpu


def core_info(sample):

    lines = sample.split("\n")
    data = []
    for line in lines:
        reg = re.findall(f"^cpu[0-9]", line)

        if len(reg)>0:
            info = line.split(' ')
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
