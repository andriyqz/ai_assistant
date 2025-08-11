import re
import json


def get_config() -> dict:
    with open('config.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def parse_commands(text):
    commands = []
    lines = text.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line or not line.startswith('/'):
            continue
        commands.append(line)

    return commands

def strip_outer_quotes(text):
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ['"', "'", '“', '”', '‘', '’']:
        return text[1:-1]
    return text
