# parsers/generic.py
import re
from datetime import datetime

LEVELS = ['ERROR', 'WARN', 'INFO', 'DEBUG', 'CRITICAL', 'FATAL']

def parse_generic_log(line):
    line = line.strip()
    level = 'INFO'
    for lvl in LEVELS:
        if lvl in line.upper():
            level = lvl
            break
    return {
        'raw': line,
        'level': level,
        'time': extract_time(line) or 'N/A'
    }

def extract_time(line):
    time_patterns = [
        r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
        r'\d{2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2}',
    ]
    for pat in time_patterns:
        m = re.search(pat, line)
        if m:
            return m.group()
    return None