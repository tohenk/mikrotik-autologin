#!/usr/bin/env python3
'''
Created on Oct 22, 2011

@author: arefaey
@author: Toha <tohenk@yahoo.com>
'''

from hashlib import md5
from httplib2 import Http
from urllib.parse import urlencode
import re

http = Http()
encoding = 'latin-1'

def truncate_file(filename):
    f = open(filename, 'w+')
    for line in f.readlines():
        line = line.replace(line, '')
        f.writelines(line)
        f.flush()

def write_file(filename, content):
    f = open(filename, 'wb')
    f.write(content)
    f.flush()

def get_meta(filename, meta, type='http\\-equiv'):
    pattern = '<meta\\s+_KEY_="_VALUE_"\\s+content="(.*)">'
    pattern = pattern.replace('_KEY_', type)
    pattern = pattern.replace('_VALUE_', meta)
    r = re.compile(pattern)
    f = open(filename, 'r')
    for line in f.readlines():
        matches = r.findall(line)
        if len(matches):
            return matches[0]

def salt_password(filename, password):
    res = []
    pattern = '(\\\'(\\\\\\d{3})+\\\')+'
    r = re.compile(pattern)
    f = open(filename, 'r')
    for line in f.readlines():
        if line.find('hexMD5') != -1:
            matches = r.findall(line)
            for match in matches:
                salt = match[0][1:-1]
                s = ''
                while len(salt):
                    c = salt[0:4]
                    ch = chr(int(c[1:], 8))
                    s += ch
                    salt = salt[4:]
                res.append(s)
            break
    if len(res)==2:
        return res[0] + password + res[1]

def hex_md5(str):
    hashed = md5(str)
    return hashed.hexdigest()

def get_page(url, filename):
    success=False
    response, content = http.request(url)
    if response.status==200:
        truncate_file(filename)
        write_file(filename, content)
        success=True
    return success

def is_status_page(filename):
    refresh = get_meta(filename, 'refresh')
    if refresh[-6:]=='status':
        return True
    return False

def login(url, username, password):
    success=False
    payload = urlencode({'username':username, 'password':password, 'dst':'', 'popup':'true'})
    headers = {}
    headers.update({'Content-Type':'application/x-www-form-urlencoded'})
    headers.update({'Content-Length':str(len(payload))})
    response, _ = http.request(url, method='POST', body=payload, headers=headers)
    if response.status==200:
        write_file('login.html', _)
        if is_status_page('login.html'):
            success=True
        for k in response.keys():
            if k=='set-cookie':
                response['set-cookie']
    return success

def main():
    import sys
    from os import path

    args = sys.argv[1:]
    config = None
    url = None
    username = None
    password = None
    auto = False
    while True:
        if len(args):
            if args[0][0:2]=='--':
                arg = args.pop(0)
                arg = arg[2:]
                param = None
                pos = arg.find('=')
                if pos >= 0:
                    param = arg[pos + 1:]
                    arg = arg[0:pos]
                if arg=='config' and not param is None:
                    config = param
                if arg=='auto':
                    auto = True
                continue
        break
    if auto and config is None:
        config = 'login.json'

    if not config is None:
        if path.isfile(config):
            import json
            f = open(config, 'r')
            cfg = json.load(f)
            for k in cfg.keys():
                if k=='url':
                    url = cfg[k]
                if k=='user':
                    username = cfg[k]
                if k=='password':
                    password = cfg[k]
        else:
            print('Configuration not found: %s!\n' % config)
            exit()
    else:
        try:
            url = args[0]
            username = args[1]
            password = args[2]
        except Exception:
            print('''Usage:
mtlogin.py [options] url username password

Available options:
--config=file.json     Read url, username, and password from file.json
--auto                 If no config specified, use configuration login.json
                       if available''')
            exit()

    print('Log in to %s with user \'%s\' and password \'%s\'' % (url, username, password))
    print('Retrieving login page...')
    filename = 'login.html'
    if not get_page(url, filename):
        print('Unable to retrieve login page, please make sure URL is correctly typed!\n')
        exit()

    print('Salting password...')
    salted = salt_password(filename, password)
    if not salted:
        if is_status_page(filename):
            print('Already logged in!\n')
        else:
            print('Password did not salted correctly!\n')
        exit()
    password = hex_md5(salted.encode(encoding))

    print('Logging in...')
    print('Salted password: %s' % salted.encode(encoding))
    print('Hashed password: %s' % password)
    if login(url, username, password):
        print('Successfully logged in ;)\n')
    else:
        print('Login failed :(\n')

if __name__ == '__main__':
    main()