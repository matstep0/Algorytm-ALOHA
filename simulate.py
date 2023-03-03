#!/usr/bin/env python3

import argparse
import logging
import sys

import api
import simulator
import algorithm

algo_base = api.Algorithm

algos = [ (name, cls) for name, cls in algorithm.__dict__.items() if
        isinstance(cls, type) and
        issubclass(cls, algo_base) and
        cls != algo_base
    ]

parser = argparse.ArgumentParser(description='MAC Simulator.')
parser.add_argument('-v', '--verbose', action='store_true', default=False, help='show more info')
parser.add_argument('-d', '--debug', action='store_true', default=False, help='show debug info')
parser.add_argument('--clients', type=int, default=5, help='number of clients')
parser.add_argument('--frames', type=float, default=0.1, help='expected number of frames per second for each client')
parser.add_argument('--ticks', type=int, default=100, help='simulator ticks per second')
parser.add_argument('--length', type=float, default=1.0, help='maximum length of a frame')
parser.add_argument('--time', type=float, default=100.0, help='simulation time in seconds')
parser.add_argument('algorithm', type=str, help='algorithm to simulate (' + ','.join([name for name, cls in algos]) + ')')
args = parser.parse_args()

log_level=logging.WARNING
if args.verbose:
    log_level=logging.INFO
if args.debug:
    log_level=logging.DEBUG
logging.basicConfig(level=log_level)

algo = None
for name, cls in algos:
    if name.lower().startswith(args.algorithm.lower()):
        algo = cls
if algo is None:
    parser.print_help()
    sys.exit(1)

length = int(args.ticks * args.length)
time = int(args.ticks * args.time)

prob = 1.0 - (1.0 - args.frames) ** (1.0 / args.ticks)

sim = simulator.Simulator()
for i in range(args.clients):
    sim.add_client(algorithm=algo, max_length=length, frame_probability = prob)

for i in range(int(args.ticks * args.time)):
    sim.tick()

print(sim.stats)
