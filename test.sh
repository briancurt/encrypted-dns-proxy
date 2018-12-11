#!/bin/bash

./proxy.py &

dig @127.0.0.1 google.com
