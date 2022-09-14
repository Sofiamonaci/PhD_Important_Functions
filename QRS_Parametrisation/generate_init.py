#!/usr/bin/python

import sys
import numpy as np
import argparse
import os

def main(args):

	print('Vf: {}, Vs: {}, Vn: {}'.format(args.vf,args.vs,args.vn))
    
    # Check if args.node is single node or vtx file
   	if "vtx" in args.node:
		nodes = np.loadtxt(args.node, dtype=int, skiprows=2)
       		n_size = len(nodes)
    	else:
        	nodes = [int(args.node),]
        	n_size = 1
        
    	print('Node(s) of interest: {}'.format(n_size))

    	print('Writing .init file')
   	f = open(args.infile + '.init','w')
    	f.write('vf:{} vs:{} vn:{} vPS:1\n'.format(args.vf,args.vs,args.vn))
    	f.write('retro_delay:1 antero_delay:1\n')
    	f.write('{} 2\n'.format(n_size))
   	[f.write('{} 0.0000\n'.format(nodes[i])) for i in range(n_size)]
	if args.rv>=0:
    		f.write('{} {} {} {}\n'.format(args.rv,args.vf,args.vs,args.vn))
    	if args.lv>=0:
		f.write('{} {} {} {}\n'.format(args.lv,args.vf,args.vs,args.vn))

	# If there is border zone, just give it 50% of args.vs
	if not args.bz == 0:
		print('BORDER ZONE = %d\n\n' %(args.bz))
		f.write('{} {} {} {}\n'.format(args.bz,args.vs/2,args.vs/2,args.vs/2))
    	f.close()

    	print('DONE')




if __name__ == '__main__':

    	parser = argparse.ArgumentParser()
    	parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    	parser.add_argument('--infile', type=str,
                        default='at',
                        help='name without extension of init file')
        parser.add_argument('--vf', type=float,
                        default=0.4,
                        help='Value of vf (velocity along fibers') 
    	parser.add_argument('--vs', type=float,
                        default=0.4,
                        help='Value of vs (velocity transverse fibers')
   	parser.add_argument('--vn', type=float,
                        default=0.4,
                        help='Value of vn (sheet velocity normal fibers')
    	parser.add_argument('--node', 
                        default=1000,
                        help='Node index/indices of initial stimulus at time 0')
	parser.add_argument('--bz', type=int,
			default = 20,
			help='presence/tag of border zone. 0 (no), any other value (yes)')
	parser.add_argument('--lv', type=int,
                        default = 4,
                        help='LV tag')
	parser.add_argument('--rv', type=int,
                        default = 2,
                        help='RV tag')
    	args = parser.parse_args()

    	main(args)

