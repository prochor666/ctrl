from core import utils
from core.ctrl import servers, remote, stat


def survey(id):

    result = {
        'status': False,
        'message': f"Server not found",
        'shell': []
    }

    monitor = compose_monitor_tasks(id)

    if type(monitor) is not dict:
        return result

    result = remote.init_client(monitor['server'], monitor['tasks'])
    result['shell'] = ''.join(result['shell'])

    parts = parse_monitor_result(result['shell'])

    result['shell'] = stat.cpu(parts['stats1'], parts['stats2'])
    result['shell'] = stat.memory(parts['memory'])
    result['status'] = True

    return result


def compose_monitor_tasks(id):

    server = servers.load_server({
        'id': id
    })

    # Server validation
    if type(server) is not dict:
        return False

    tasks = [
        'echo "SSH server hostname: $(hostname)"',
        'echo "<control-monitor-cpu>"',
        'echo "$(cat /proc/cpuinfo)"',
        'echo "</control-monitor-cpu>"',
        'echo "<control-monitor-stat-sample1>"',
        'echo "$(cat /proc/stat)"',
        'echo "</control-monitor-stat-sample1>"',
        'sleep 2',
        'echo "<control-monitor-stat-sample2>"',
        'echo "$(cat /proc/stat)"',
        'echo "</control-monitor-stat-sample2>"',
        'echo "<control-monitor-mem>"',
        'echo "$(cat /proc/meminfo)"',
        'echo "</control-monitor-mem>"',
        'echo "<control-monitor-storage>"',
        'echo "$(df -h /var/www)"',
        'echo "</control-monitor-storage>"',
        'echo "<control-monitor-net>"',
        'echo "$(cat /proc/net/dev)"',
        'echo "</control-monitor-net>"',
    ]

    return {
        'server': server,
        'tasks': tasks
    }


def parse_monitor_result(raw):

    cpu = utils.tag_parse('control-monitor-cpu', raw)
    memory = utils.tag_parse('control-monitor-mem', raw)
    net = utils.tag_parse('control-monitor-net', raw)
    storage = utils.tag_parse('control-monitor-storage', raw)
    stats1 = utils.tag_parse('control-monitor-stat-sample1', raw)
    stats2 = utils.tag_parse('control-monitor-stat-sample2', raw)

    return {
        'cpu': cpu,
        'memory': memory,
        'net': net,
        'storage': storage,
        'stats1': stats1,
        'stats2': stats2,
    }
