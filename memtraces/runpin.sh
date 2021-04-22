#!/bin/bash

./runcpu --config=try1 --action=build 505.mcf_r
pin -t /afs/pitt.edu/home/t/m/tmd62/private/pin/source/tools/ManualExamples/obj-intel64/pinatrace.so -- ./runcpu --config=try1 --action=run 505.mcf_r

cp pinatrace.out /afs/cs.pitt.edu/usr0/tmd62/public/memtraces/505.mcf_r.mt

