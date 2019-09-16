#!/urs/bin/python
# coding=UTF-8
import random
import time
import socket
import struct
import os
import sys

"""
Função que extrai informações do whois(comando linux) dos ip de cada salto do traceroute.
Args(): ip = String / Int
"""


def get_info(ip):
    # Executa o comando whois e filta a saída com o comando grep usando pipelines
    command = 'whois -H ' + ip + "| grep 'owner\|inetnum\|aut-num\|person\|e-mail'"
    process = os.popen(command)
    # print(command)
    result = str(process.read())
    return result


"""
Criando um socket de recebimento
Returns: A socket instance
Raises: IOError
"""


def create_receiver(port):
    # create socket to tcp/icmp public
    icmp = socket.socket(family=socket.AF_INET, type=socket.SOCK_RAW, proto=socket.IPPROTO_ICMP)

    timeout = struct.pack("ll", 5, 0)
    icmp.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)  # define socket's params

    try:
        icmp.bind(('', port))
    except socket.error as e:
        raise IOError(f"Unable to bind receiver socket: {e}")
    return icmp


"""
Criando um socket de envio
Returns: A socket instance

"""


def create_sender(ttl):
    udp = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
    udp.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)  # define socket's params for IP and TTL

    return udp


def tracer(host, jumps):
    port = random.choice(range(10000, 33535))  # choice port for open server
    ttl = 1  # TTL start
    jumps = int(jumps)  # number trace's jumps

    try:
        host = socket.gethostbyname(host)
    except socket.error as e:
        raise IOError(f'Unable to resolve {host} : {e}')

    print(f"Traceroute to {host}:{port} with {jumps} jumps")

    while True:
        receiver = create_receiver(port)
        sender = create_sender(ttl)

        receiver.bind(("", port))
        sender.sendto(b"", (host, port))

        start_time = time.time()
        end_time = time.time()
        addr_present = None
        host_present = None

        try:
            _, addr_present = receiver.recvfrom(512)  # Recebendo o pacote
            end_time = time.time()
            addr_present = addr_present[0]  # O primeiro campo da lista é o IP

            try:
                # Pega um nome do IP de salto.
                host_present = socket.gethostbyaddr(addr_present)[0]
            except socket.error:
                host_present = addr_present

        except socket.error:
            pass
        finally:
            receiver.close()
            sender.close()

        if addr_present is not None:

            time_delay = round((end_time - start_time) * 1000, 2)  # Calculando o tempo de atraso.
            print(f'ttl:{ttl:<8} host: {host_present}\tIP:({addr_present})\ttimedelay: {time_delay}ms')
            print(get_info(addr_present))
        else:
            print('*' * 4)

        ttl += 1
        if addr_present == host or ttl > jumps:
            print("Análise feita com SUCESSO")
            break


def main():
    print('-' * 40)
    print("Iniciando o footprint do alvo")
    print('-' * 40)

    endpoint = input("Digite o site do alvo: ")
    jumps = input("Digite a quantidade saltos: ")

    tracer(endpoint, jumps)


# Verifica se foi executado ou importando como modulo
# Se for executado via cli o atributo __name__= __ main__ e executa o scrip
if __name__ == '__main__':
    main()
