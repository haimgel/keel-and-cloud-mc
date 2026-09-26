#!/usr/bin/env python3
"""Minimal RCON client: rcon.py [-p PASSWORD_FILE] COMMAND...  (one command per argument)."""
import argparse, socket, struct, sys

def packet(req_id, kind, body):
    data = struct.pack('<ii', req_id, kind) + body.encode() + b'\x00\x00'
    return struct.pack('<i', len(data)) + data

def read(sock):
    size = struct.unpack('<i', sock.recv(4, socket.MSG_WAITALL))[0]
    data = sock.recv(size, socket.MSG_WAITALL)
    req_id, _ = struct.unpack('<ii', data[:8])
    return req_id, data[8:-2].decode(errors='replace')

class Rcon:
    def __init__(self, password, host='127.0.0.1', port=25575):
        self.sock = socket.create_connection((host, port), timeout=600)
        self.sock.sendall(packet(1, 3, password))
        if read(self.sock)[0] == -1:
            sys.exit('rcon: authentication failed')

    def run(self, command):
        self.sock.sendall(packet(2, 2, command))
        return read(self.sock)[1]

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-p', '--password-file', default='build/server/.rcon-pass')
    ap.add_argument('commands', nargs='+')
    a = ap.parse_args()
    r = Rcon(open(a.password_file).read().strip())
    for c in a.commands:
        print(r.run(c))
