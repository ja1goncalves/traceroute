#!/usr/bin/python
# coding=UTF-8

import random
import socket
import pygeoip
import struct


def locator(ip):
    way_geo_lite_city = '/home/airton/build/geoip/GeoLiteCity.dat'
    base_data = pygeoip.GeoIP(way_geo_lite_city)
    location = base_data.record_by_name(ip)  # get location by IP

    if location is not None:
        if location.get('country_name') is not None:
            print("\t" + "Country: " + location.get('country_name'))
        if location.get('city') is not None:
            print("\t" + "City: " + location.get('city'))
        if location.get('latitude') is not None:
            print("\t" + "Latitude: " + str(location.get('latitude')))
        if location.get('longitude') is not None:
            print("\t" + "Longitude: " + str(location.get('longitude')))


def main(endpoint, jumps):
    endpoint = socket.gethostbyname(endpoint)
    port = random.choice(range(10000, 33535))
    jumps = int(jumps)

    icmp = socket.getprotobyname('icmp')  # get o proto ICMP
    udp = socket.getprotobyname('udp')  # get o proto UDP

    ttl = 1  # TTL start
    timeout = struct.pack("ll", 5, 0)

    print("-" * 100)
    print("INIT ROUTE\n")
    print("-" * 100)

    while True:
        receiver = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        receiver.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)

        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
        sender.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

        receiver.bind(("", port))
        sender.sendto(b"", (endpoint, port))

        address_present = None
        present_name = None

        try:
            _, address_present = receiver.recvfrom(512)  # 512 is length buffer to receive
            address_present = address_present[0]

            try:
                present_name = socket.gethostbyaddr(address_present)[0]  # get address to ip receive
            except socket.error:
                present_name = address_present
        except socket.error:
            print("-" * 100)
            print("END ROUTE FOR ERROR BY CONNECTION OR TIMEOUT\n")
            print("-" * 100)
            break
        finally:
            sender.close()
            receiver.close()

        if address_present is not None:
            print(str(ttl) + "\t" + present_name + " (" + address_present + ")")
            locator(address_present)  # show localization by address received

        else:
            print("*")

        ttl += 1

        if address_present == endpoint or ttl > jumps:
            print("-" * 100)
            print("END TO ROUTE WITH SUCCESS\n")
            print("-" * 100)
            break


if __name__ == "__main__":

    print("-" * 100)
    print("WELCOME TO GEOIP!\n")
    print("-" * 100)

    endpoint = input("Enter the website address you want to route to: ")
    jumps = input("Enter the maximum number of hops you want to take: ")

    main(endpoint, jumps)
