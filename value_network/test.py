#!/usr/bin/env python3
# coding: utf-8

#from __future__ import print_function, division

import sys
import random

from train import parse_row
from model import ValueNetwork


model_file = sys.argv[1] # e.g. value_network_5items.h5
vn = ValueNetwork(model_file)

# The test dataset must follow the same format of the training data file,
# even though we ignore the labels while testing.
datafile = sys.argv[2]

samples = []
with open(datafile) as f:
    lines = f.read().splitlines()
    # Grab a random sample of the data.
    random.shuffle(lines)
    for line in lines[50:80]:
        _, (source_menu, source_freq, source_asso), (target_menu, target_freq, target_asso), exposed = parse_row(line)
        samples.append([source_menu, source_freq, source_asso, target_menu, target_freq, target_asso, exposed])

rewards = vn.predict_batch(samples)

for tup in rewards:
    serial, forage, recall = tup
    print(serial, forage, recall)
