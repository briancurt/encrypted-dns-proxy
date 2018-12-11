#!/bin/bash

sudo ./proxy.py -c "/etc/ssl/certs/cacert.pem" &

dig @127.0.0.1 google.com
