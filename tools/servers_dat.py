#!/usr/bin/env python3
"""Writes pack/servers.dat, the default multiplayer server list (uncompressed NBT).
   tools/servers_dat.py "Keel & Cloud=keel-mc.g8n.me" [...]
Then run `packwiz refresh` and check `preserve = true` is still on the servers.dat entry in index.toml."""
import os, struct, sys

def string(value):
    b = value.encode()
    return struct.pack('>H', len(b)) + b

def server(name, ip):
    return (b'\x08' + string('name') + string(name) +
            b'\x08' + string('ip') + string(ip) +
            b'\x01' + string('hidden') + b'\x00' + b'\x00')

entries = [arg.split('=', 1) for arg in sys.argv[1:]] or [('Keel & Cloud', 'keel-mc.g8n.me')]
data = (b'\x0a' + string('') + b'\x09' + string('servers') + b'\x0a' + struct.pack('>i', len(entries)) +
        b''.join(server(n, ip) for n, ip in entries) + b'\x00')
out = os.path.join(os.path.dirname(__file__), '..', 'pack', 'servers.dat')
open(out, 'wb').write(data)
print(f'wrote {len(entries)} server(s) to pack/servers.dat')
