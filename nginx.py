# parsers/nginx.py
import re
from datetime import datetime

NGINX_PATTERN = re.compile(
    r'(?P<ip>[\d\.]+) - - \[(?P<time>[^\]]+)\] "(?P<request>[^"]*)" '
    r'(?P<status>\d+) (?P<size>\d+) "(?P<referer>[^"]*)" "(?P<ua>[^"]*)"'
)

def parse_nginx_log(line):
    match = NGINX_PATTERN.match(line.strip())
    if not match:
        return {'raw': line.strip(), 'level': 'UNKNOWN'}
    
    data = match.groupdict()
    try:
        data['time'] = datetime.strptime(data['time'], '%d/%b/%Y:%H:%M:%S %z').isoformat()
    except:
        data['time'] = data['time']
    
    data['level'] = 'ERROR' if int(data['status']) >= 400 else 'INFO'
    data['raw'] = line.strip()
    return data