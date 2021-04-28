#!/usr/bin/env python
"""
    Version: 1.2

    Original Author: Kirth Gersen
    Author: Jesse Kretschmer
    Python Version: 2 or 3

"""

import argparse
import json
import logging
import sys
import csv

DATA = {}
LOG = logging.getLogger('iperf2csv')
LOG.addHandler(logging.StreamHandler())
LOG.handlers[-1].setFormatter(logging.Formatter(
    "%(asctime)s;%(levelname)s;%(message)s", "%Y-%m-%d %H:%M:%S"))
LOG.setLevel(logging.WARNING)

def get_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--help', action='help', help='Show this help message and exit')
    parser.add_argument("-h", "--headers", action="store_true", help="Include column headers")
    parser.add_argument("-d", "--debug", action="store_true", help="Debug messages")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose messsage")
    parser.add_argument("json", nargs="?", help="Specify json file to parse")
    return parser.parse_args()

def main():
    """main program"""

    csv.register_dialect('iperf3log', delimiter=',', quoting=csv.QUOTE_MINIMAL)
    csvwriter = csv.writer(sys.stdout, 'iperf3log')

    args = get_args()
    if args.verbose:
        LOG.setLevel(logging.INFO)
    if args.debug:
        LOG.setLevel(logging.DEBUG)

    if args.headers:
        csvwriter.writerow(
            ["date", "ip", "localport", "remoteport", "duration", "protocol", "num_streams", "cookie", "sent",
             "sent_mbps", "rcvd", "rcvd_mbps", "totalsent", "totalreceived"])

    if args.json:
        source_file = open(args.json, 'rb')
    else:
        source_file = sys.stdin
    try:
        obj = json.load(source_file)
    except ValueError:
        LOG.error("Malformed json")
    process(obj, csvwriter)

def process(obj, csvwriter):
    try:
        # caveat: assumes multiple streams are all from same IP so we take the 1st one
        # todo: handle errors and missing elements
        ip = (obj["start"]["connected"][0]["remote_host"]).encode('ascii', 'ignore')
        local_port = obj["start"]["connected"][0]["local_port"]
        remote_port = obj["start"]["connected"][0]["remote_port"]

        sent = obj["end"]["sum_sent"]["bytes"]
        rcvd = obj["end"]["sum_received"]["bytes"]
        sent_speed = obj["end"]["sum_sent"]["bits_per_second"] / 1000 / 1000
        rcvd_speed = obj["end"]["sum_received"]["bits_per_second"] / 1000 / 1000


        reverse = obj["start"]["test_start"]["reverse"]
        time = (obj["start"]["timestamp"]["time"]).encode('ascii', 'ignore')
        cookie = (obj["start"]["cookie"]).encode('ascii', 'ignore')
        protocol = (obj["start"]["test_start"]["protocol"]).encode('ascii', 'ignore')
        duration = obj["start"]["test_start"]["duration"]
        num_streams = obj["start"]["test_start"]["num_streams"]
        if reverse not in [0, 1]:
            sys.exit("unknown reverse")

        s = 0
        r = 0
        if ip in DATA:
            (s, r) = DATA[ip]

        if reverse == 0:
            r += rcvd
            sent = 0
            sent_speed = 0
        else:
            s += sent
            rcvd = 0
            rcvd_speed = 0

        DATA[ip] = (s, r)
        row = [time, ip, local_port, remote_port, duration, protocol, num_streams, cookie, sent, sent_speed, rcvd, rcvd_speed, s, r]
        row = [_.decode() if isinstance(_, (bytes)) else _ for _ in row]
        csvwriter.writerow(row)
        return True
    except:
        LOG.exception("error or bogus test")
        return False

if __name__ == '__main__':
    main()
