#!/urs/bin/python
# coding=UTF-8

import random
import time
import socket
import struct
import sys


def main():
    print('-' * 40)
    print("Iniciando o footprint do alvo")
    print('-' * 40)

    endpoint = input("Digite o site do alvo: ")
    jumps = int(input("Digite a quantidade saltos: "))

    tracer(endpoint, jumps)


def tracer(host, jumps=30):
    port = random.choice(range(33434, 33535))  # choice port for open server
    ttl = 1  # TTL start
    timeout = struct.pack("ll", 5, 0)

    try:
        destine = socket.gethostbyname(host)
    except socket.error as e:
        raise IOError(f'Unable to resolve {host}:{e}')

    print(f"Traceroute to {host}:{port} with {jumps} jumps")

    while True:
        receiver = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        receiver.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)  # define socket's params

        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sender.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)  # define socket's params for IP and TTL

        receiver.bind(('', port))
        sender.sendto(b"", (host, port))

        start_time = time.time()
        finished = False
        tries = 3
        addr_present = None
        host_present = None

        while not finished and tries > 0:
            try:
                _, addr_present = receiver.recvfrom(512)  # Receive package
                finished = True
                end_time = time.time()
                addr_present = addr_present[0]  # first of ip list

                try:
                    host_present = socket.gethostbyaddr(addr_present)[0]
                except socket.error:
                    host_present = addr_present

            except socket.error as e:
                tries = tries - 1
                sys.stdout.write("* ")

        receiver.close()
        sender.close()

        if not finished:
            pass

        if addr_present is not None:
            time_delay = round((end_time - start_time) * 1000, 2)
            print(f'ttl:{ttl:<8} host: {host_present}\tIP:({addr_present})\ttimedelay: {time_delay}ms')
        else:
            print('*' * 4)

        ttl += 1
        if addr_present == destine or ttl > jumps:
            print("Análise feita com SUCESSO")
            break


if __name__ == '__main__':
    main()
