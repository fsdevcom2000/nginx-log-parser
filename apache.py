# parsers/apache.py
import re
from datetime import datetime

APACHE_COMBINED_PATTERN = re.compile(
    r'(?P<ip>[\d\.]+|\[[^\]]+\]|\S+) '           
    r'(?P<ident>\S+) '
    r'(?P<user>\S+) '
    r'\[(?P<time>[^\]]+)\] '
    r'"(?P<request>[^"]*)" '
    r'(?P<status>\d+) '
    r'(?P<size>\S+) '
    r'(?:"(?P<referer>[^"]*)")?'
    r' "(?P<ua>[^"]*)"'
)

# exaple Apache: 10/Oct/2000:13:55:36 -0700
TIME_FORMAT = '%d/%b/%Y:%H:%M:%S %z'

def parse_apache_log(line: str):
    line = line.strip()
    if not line:
        return {'raw': line, 'level': 'UNKNOWN'}

    match = APACHE_COMBINED_PATTERN.match(line)
    if not match:
        simple_pattern = re.compile(
            r'(?P<ip>\S+) (?P<ident>\S+) (?P<user>\S+) \[(?P<time>[^\]]+)\] "(?P<request>[^"]*)" (?P<status>\d+) (?P<size>\S+)'
        )
        match = simple_pattern.match(line)

    if not match:
        return {
            'raw': line,
            'level': 'UNKNOWN',
            'time': 'N/A'
        }

    data = match.groupdict()

    try:
        time_str = data['time']
        if ' ' not in time_str:
            time_str += ' +0000'
        data['time'] = datetime.strptime(time_str, TIME_FORMAT).isoformat()
    except Exception:
        data['time'] = data['time']

    try:
        status = int(data['status'])
        data['level'] = 'ERROR' if status >= 400 else 'INFO'
    except:
        data['level'] = 'UNKNOWN'

    request = data.get('request', '')
    parts = request.split()
    if len(parts) >= 3:
        data['method'] = parts[0]
        data['path'] = parts[1]
        data['protocol'] = parts[2]
    else:
        data['method'] = data['path'] = data['protocol'] = '-'

    data['size'] = data['size'] if data['size'] != '-' else '0'
    data['referer'] = data.get('referer', '-') or '-'
    data['ua'] = data.get('ua', '-') or '-'

    data['raw'] = line

    return data