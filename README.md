# MikroTik Hotspot Autologin

A simple tool to automatically login to MikroTik Hotspot using http protocol.

## License

The mikrotik-autologin uses the Apache 2 license. See LICENSE for details.

## Usage Notes

To login to Mikrotik Hotspot, provides url, username and password as shown below:
```
$ python3 mtlogin.py url username password
```

To use configuration from `login.json`, issue:
```
$ python3 mtlogin.py --auto
```

To use configuration elsewhere, issue:
```
$ python3 mtlogin.py --config=path/to/config.json
```

## Dependencies

Dependencies can be installed using pip.
```
$ pip install httplib2
```