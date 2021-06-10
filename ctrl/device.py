import psutil, platform, socket
from ctrl import utils


def sys_info():

    uname = platform.uname()
    return {
        'system': uname.system,
        'node': uname.node,
        'release': uname.release,
        'version': uname.version,
        'machine': uname.machine
    }


def cpu_info():
    cpuFreq = psutil.cpu_freq()
    usage = psutil.cpu_percent()

    cpu = {
        'physical': psutil.cpu_count(logical=False),
        'cores': psutil.cpu_count(logical=True),
        'frequency': {
            'max': utils.decimal_size(cpuFreq.max*1000000),
            'min': utils.decimal_size(cpuFreq.min*1000000),
            'current': utils.decimal_size(cpuFreq.current*1000000)
        },
        'usage': str(usage)+'%'
    }

    return cpu


def memory_info():

    svmem = psutil.virtual_memory()

    mem = {
        'total': utils.byte_size(svmem.total),
        'available': utils.byte_size(svmem.available),
        'used': utils.byte_size(svmem.used)
    }

    return mem


def disk_info():
    partitions = psutil.disk_partitions()
    result = {}

    for i, partition in enumerate(partitions):
        key = partition.device
        result[key] = {
            'mountpoint': partition.mountpoint,
            'fstype': partition.fstype
        }

        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)

            result[key]['total'] = utils.byte_size(partition_usage.total)
            result[key]['used'] = utils.byte_size(partition_usage.used)
            result[key]['free'] = utils.byte_size(partition_usage.free)

        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue

    return result


def network_info():
    interfaces = psutil.net_if_addrs()
    result = {}
    for name, addrs in interfaces.items():
        status = {
            "ipv4" : "-",
            "ipv6" : "-",
            "mac" : "-"
        }

        if name != 'lo':
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    status["ipv4"] = addr.address

                if addr.family == socket.AF_INET6:
                    status["ipv6"] = addr.address

                if addr.family == psutil.AF_LINK:
                    status["mac"] = addr.address

            result[name] = status

    return result
