#!/urs/bin/python
# coding=UTF-8

import random
import time
import socket
import struct
import sys
import signal


def signal_handler(sig, frame):
    print('\nSee you, bye! \U0001f600 \U0001F618 \U0001F44B')
    sys.exit(0)


def main():
    print('-' * 60)
    print("Init the footprint to target | Press Ctrl+C to exit")
    print('-' * 60)

    endpoint = input("Inset target site: ")
    jumps = int(input("Insert jumps quantity: "))

    signal.signal(signal.SIGINT, signal_handler)
    tracer(endpoint, jumps)
    signal.pause()


def tracer(host, jumps=30):
    port = random.choice(range(33434, 33535))  # choice port for open server
    ttl = 1  # TTL start
    timeout = struct.pack("ll", 5, 0)  # time wait the package 5s

    try:
        destine = socket.gethostbyname(host)  # get host request destine
    except socket.error as e:
        raise IOError(f'\U0001F912 \U0001F915 Unable to resolve {host}:{e}')

    print(f"Traceroute to {destine} ({host}:{port}) with {jumps} jumps \U0001F9D0")

    while True:
        receiver = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)  # server received information for package
        receiver.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)  # define socket's params (timeout wait package)

        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # server send package
        sender.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)  # define socket's params for IP and TTL

        try:
            receiver.bind(('', port))  # init received server
            sender.sendto(b"", (host, port))  # send package in bytes by send server

            start_time = time.time()  # get start time for calculation delay
            finished = False  # verify receive package for finish
            tries = 3  # packet send and receive attempt numbers
            addr_present = None  # ip in address stoped packege
            host_present = None  # host of ip

            sys.stdout.write(f'ttl:{ttl:<8} ')

            while not finished and tries > 0:  # while the attempts are not over
                try:
                    _, addr_present = receiver.recvfrom(512)  # Receive package in addr_present [index 1]
                    finished = True  # indicates the receipt the package
                    end_time = time.time()  # get end time for calculation delay
                    addr_present = addr_present[0]  # first of ip list [last package passed]

                    try:
                        host_present = socket.gethostbyaddr(addr_present)[0]  # get host by ip address
                    except socket.error:
                        host_present = addr_present

                except socket.error as e:
                    tries = tries - 1
                    sys.stdout.write("\U0001F62A ")

            receiver.close()  # close receive server
            sender.close()  # close send server

            if not finished:
                pass

            if addr_present is not None:
                time_delay = round((end_time - start_time) * 1000, 2)  # calculation the time delay
                sys.stdout.write(f'host: {host_present:<45} ')
                sys.stdout.write(f'IP: {addr_present:<17} ')
                sys.stdout.write(f'timedelay: {time_delay}ms ')
                print()
                # print(f'host: {host_present}\t\t\tIP:({addr_present})\ttimedelay: {time_delay}ms')
            else:
                print('\U0001F62A' * 4)

            ttl += 1
            if addr_present == destine or ttl > jumps:  # packege has arrived in destine or jumps is finished
                print("Successful analysis")
                break
        except (socket.gaierror or socket.error) as e:
            print("Something went wrong with sending or receiving information \U0001F912 \U0001F915")
            print(f"Error message: {str(e)}")


if __name__ == '__main__':
    main()
