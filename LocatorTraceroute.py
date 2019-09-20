#!/usr/bin/python
# coding=UTF-8

import random
import socket
import sys
import time
import geoip2.webservice
import pygeoip
import struct


def locator(ip):
    # base_data = pygeoip.GeoIP('./data/GeoIPCity.dat')
    # location = base_data.record_by_addr(ip)  get location by IP

    reader = geoip2.webservice.Client(42, 'license_key')
    response = reader.insights(ip)

    if response is not None:
        if hasattr(response, 'country') is not None:
            print("\t" + "Country: " + response.country.name)
        if hasattr(response, 'city') is not None:
            print("\t" + "City: " + str(response.city.name))
        if hasattr(response, 'location') is not None:
            print("\t" + "Latitude: " + str(response.location.latitude))
            print("\t" + "Longitude: " + str(response.location.longitude))
        if hasattr(response, 'subdivisions') is not None:
            print("\t" + "Longitude: " + str(response.subdivisions.most_specific.iso_code))
        if hasattr(response, 'postal') is not None:
            print("\t" + "Longitude: " + str(response.postal.code))

    reader.close()


def main(host, jumps):
    port = random.choice(range(33434, 33535))  # choice port for open server
    ttl = 1  # TTL start
    timeout = struct.pack("ll", 5, 0)  # time wait the package 5s

    try:
        destine = socket.gethostbyname(host)  # get host request destine
    except socket.error as e:
        raise IOError('Unable to resolve {}:{}'.format(host, e))

    print("Traceroute to {} ({}:{}) with {} jumps".format(destine, host, port, jumps))

    while True:
        receiver = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                 socket.IPPROTO_ICMP)  # server received information for package
        receiver.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO,
                            timeout)  # define socket's params (timeout wait package)

        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # server send package
        sender.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)  # define socket's params for IP and TTL

        receiver.bind(('', port))  # init received server
        sender.sendto(b"", (host, port))  # send package in bytes by send server

        start_time = time.time()  # get start time for calculation delay
        finished = False  # verify receive package for finish
        tries = 3  # packet send and receive attempt numbers
        addr_present = None  # ip in address stoped packege
        host_present = None  # host of ip

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
                sys.stdout.write("* ")

        receiver.close()  # close receive server
        sender.close()  # close send server

        if not finished:
            pass

        if addr_present is not None:
            time_delay = round((end_time - start_time) * 1000, 2)  # calculation the time delay
            print('ttl:'+str(ttl)+' host: '+host_present+'\t\tIP:('+addr_present+')\ttimedelay: '+str(time_delay)+'ms')
            locator(addr_present)
        else:
            print('*' * 4)

        ttl += 1
        if addr_present == destine or ttl > jumps:  # packege has arrived in destine or jumps is finished
            print("Análise feita com SUCESSO")
            break


if __name__ == "__main__":

    print("-" * 100)
    print("WELCOME TO GEOIP!\n")
    print("-" * 100)

    endpoint = input("Enter the website address you want to route to: ")
    jumps = input("Enter the maximum number of hops you want to take: ")

    main(endpoint, jumps)
