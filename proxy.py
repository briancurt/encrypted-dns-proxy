#!/usr/bin/env python3

from argparse import ArgumentParser
import binascii
import logging
import socket
import ssl
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_message(dns, query, ca_path):

    server = (dns, 853)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(80)

    ctx = ssl.create_default_context()
    ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    ctx.verify_mode = ssl.CERT_REQUIRED
    ctx.check_hostname = True
    ctx.load_verify_locations(ca_path)

    wrapped_socket = ctx.wrap_socket(sock, server_hostname=dns)
    wrapped_socket.connect(server)
    logger.info("Server peer certificate: %s", str(wrapped_socket.getpeercert()))

    tcp_msg = "\x00".encode() + chr(len(query)).encode() + query
    logger.info("Client request: %s", str(tcp_msg))
    wrapped_socket.send(tcp_msg)
    data = wrapped_socket.recv(1024)
    return data


def thread(data, address, socket, dns, ca_path):

    answer = send_message(dns, data, ca_path)
    if answer:
        logger.info("Server reply: %s", str(answer))
        rcode = binascii.hexlify(answer[:6]).decode("utf-8")
        rcode = rcode[11:]
        if int(rcode, 16) == 1:
            logger.error("Error processing the request, RCODE = %s", rcode)
        else:
            logger.info("Proxy OK, RCODE = %s", rcode)
            return_ans = answer[2:]
            socket.sendto(return_ans, address)
    else:
        logger.warn("Empty reply from server.")


def main():

    parser = ArgumentParser(description="Semi transparent DNS to DNS-over-TLS proxy.")
    parser.add_argument('-p', '--port', help="Port of the listening proxy [default: 53]", type=int, default=53, required=False)
    parser.add_argument('-a', '--address', help="Address of the proxy network interface to use [default: 0.0.0.0]", type=str, default='0.0.0.0', required=False)
    parser.add_argument('-d', '--dns', help="Domain name server with TLS support [default: 1.1.1.1]", type=str, default='1.1.1.1', required=False)
    parser.add_argument('-c', '--ca', help="Path to the root and intermediate certificates file [default: /etc/ssl/cert.pem]", type=str, default='/etc/ssl/cert.pem', required=False)
    args = parser.parse_args()
    port = args.port
    host = args.address
    dns = args.dns
    ca_path = args.ca
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((host, port))
        while True:
            data, address = sock.recvfrom(4096)
            threading.Thread(target=thread, args=(data, address, sock, dns, ca_path)).start()
    except Exception as e:
        logger.error(e)
    finally:
        sock.close()


if __name__ == '__main__':
    main()
