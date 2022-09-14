#!/usr/bin/env python

import sys
import numpy as np
import argparse
import os

def main(args):

	print('Vf: {}, Vs: {}, Vn: {}'.format(args.vf,args.vs,args.vs))
	
	# Conductivities can be either given as .dat files or single numbers/array
	if "dat" in args.gl:
		print('Reading .dat conductivities file: {}'.format(args.gl))    
		g_l = np.loadtxt(args.gl, dtype=float)
	else:
		g_l = args.gl

	if "dat" in args.gt:
                print('Reading .dat conductivities file: {}'.format(args.gt))                
                g_t = np.loadtxt(args.gt, dtype=float)
        else:
                g_t = args.gt




    	print('Writing {} file'.format(args.out))
   	f = open(args.out,'a')
        if not args.vf==0:
            f.write('ekregion[0].vel_f = {}\nekregion[0].vel_s = {}\nekregion[0].vel_n = {}\n'.format(args.vf,args.vs,args.vs))
    	
        
        f.write('gregion[0].g_il = {}\ngregion[0].g_it = {}\ngregion[0].g_in = {}\n'.format(g_l[1],g_t[1],g_t[1]))
	f.write('gregion[0].g_el = {}\ngregion[0].g_et = {}\ngregion[0].g_en = {}\n'.format(g_l[2],g_t[2],g_t[2]))

	if not args.bz == 0:
		print('BORDER ZONE = %d' %(args.bz))
                if not args.vf == 0:
                    f.write('ekregion[1].vel_f = {}\nekregion[1].vel_s = {}\nekregion[1].vel_n = {}\n'.format(args.vs/2,args.vs/2,args.vs/2))
        	f.write('gregion[1].g_il = {}\ngregion[1].g_it = {}\ngregion[1].g_in = {}\n'.format(g_t[1],g_t[1],g_t[1]))
        	f.write('gregion[1].g_el = {}\ngregion[1].g_et = {}\ngregion[1].g_en = {}\n'.format(g_t[2],g_t[2],g_t[2]))

	f.close()

    	print('DONE')




if __name__ == '__main__':

    	parser = argparse.ArgumentParser()
    	parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    	parser.add_argument('--vf', type=float,
                        default=0.4,
                        help='Value of vf (velocity along fibers') 
    	parser.add_argument('--vs', type=float,
                        default=0.4,
                        help='Value of vs (velocity transverse fibers')
   	parser.add_argument('--gl', 
                        help='Value(s) or file of g_il and g_el')
    	parser.add_argument('--gt', 
                        help='Value(s) or file of g_it and g_et')
	parser.add_argument('--out', type=str,
                        default='extra_param.par',
                        help='.par output file')
	parser.add_argument('--bz', type=float,
                        default=20,
                        help='Tag of border zone, if existent (otherwise, enter 0)')
    	args = parser.parse_args()

    	main(args)

