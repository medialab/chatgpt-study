#!/bin/bash

SLICE=$1

xsv slice -s $1 -l 1000 data.csv > input/slice_${1}.csv