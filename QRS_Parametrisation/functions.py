#!/usr/bin/env python

import sys
import numpy as np
import argparse
import os


def read_dat(filename):
	dat = np.loadtxt(filename, dtype=float)
	print(dat)
	return dat

def calculate_max_at(filename):
	dat = np.loadtxt(filename, dtype=float)
	print(max(dat))
	return max(dat)

def check_inf(filename):
	dat = np.loadtxt(filename, dtype=float)
	u_dat = np.unique(dat)
	if not np.where(max(dat)>400)[0]:
		print("Removing inf values ...\n")
		max_dat = u_dat[-2]
		dat[dat>400] = max_dat
	print("Saving new dat file ...\n")
	np.savetxt(filename,dat)
	return dat

if __name__ == "__main__":

	cmd = sys.argv[1]
	
	if 'read' in cmd:
		read_dat(sys.argv[2])
	elif 'calculate' in cmd:
		calculate_max_at(sys.argv[2])
	elif 'check_inf' in cmd:
		check_inf(sys.argv[2])
