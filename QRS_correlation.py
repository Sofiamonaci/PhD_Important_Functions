#!/usr/bin/env python

import sys
import numpy as np
import argparse
import os
import matplotlib.pyplot as plt
import matlab.engine

def compute_ecg(sig):

	ecg = np.zeros((sig.shape[0],12))
	wct = (sig[:,6] + sig[:,7] + sig [:,8])/3
	# pre-cordial
	for i in range(6):
		ecg[:,i] = sig[:,i] - wct 
	# Limb
	ecg[:,6] = sig[:,7] - sig[:,6]
	ecg[:,7] = sig[:,8] - sig[:,6]	
	ecg[:,8] = sig[:,8] - sig[:,7]
	# aVR, aVL, aVF
	ecg[:,9] = sig[:,6] - 0.5*(sig[:,7] - sig[:,8])
	ecg[:,10] = sig[:,7] - 0.5*(sig[:,6] - sig[:,8])
	ecg[:,11] = sig[:,8] - 0.5*(sig[:,7] - sig[:,6])

	return ecg

def main(args):

	tol = 0.001

	print('Reading {} from simulation ...'.format(args.Ts))
	sig = np.loadtxt(args.Ts, dtype=float)
	# Compute ECG for V1
	wct = (sig[:,6] + sig[:,7] + sig [:,8])/3 
	v1 = sig[:,0] - wct

	print('Printing ecg file from eikonal simulation: ')
	print(args.Ts[:-3]+"csv")
	ecg = compute_ecg(sig)	
	np.savetxt(args.Ts[:-3]+"csv",ecg, delimiter=',')

	# Compute QRSs duration
	eng = matlab.engine.start_matlab()	
	eng.addpath('/media/sm18/Seagate Backup Plus Drive/PhD/CNN_init/MatlabProcessingCNNtools')
	eng.addpath('/media/sm18/Seagate Backup Plus Drive/PhD/Clinical_Data/MatlabProcessingTools')
	Ts = eng.QRS_align_parametrisation(args.ECGm,args.Ts[:-3]+'csv',args.vf)
#	Ts = eng.new_QRSd_from_VCG(args.Ts[:-3]+"csv")
	print('Ts is: {}'.format(Ts))

	if abs(args.Tm-Ts)>=30:
		tol=0.03
	elif abs(args.Tm-Ts)>15:
		tol = 0.01
	elif abs(args.Tm-Ts)<15:
		tol=0.001

    	# Computing new VF or not
	if abs(args.Tm-Ts)<7:
		flag = 1
		vf = args.vf
	elif Ts<args.Tm:
		flag = 0
		vf = args.vf - tol*args.vf
	else:
		flag = 0
		vf = args.vf + tol*args.vf

	print(flag)	
	with open('flag.dat','w') as file:
		file.write(str(flag))
	with open('vf.dat','w') as file:      
                file.write(str(vf))
    	print('DONE')




if __name__ == '__main__':

    	parser = argparse.ArgumentParser()
    	parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    	parser.add_argument('--vf', type=float,
                        default=0.4,
                        help='Value of vf (velocity along fibers') 
    	parser.add_argument('--Tm', type=float,
                        default=180,
                        help='Measured QRS duration')
	parser.add_argument('--ECGm', type=str,
                        default='AAI3_ecg_measured.dat',
                        help='Measured ECG signal')
   	parser.add_argument('--Ts', type=str,
                        default='./lead_field/eikonal_sim.dat',
                        help='Electrograms from lead filed (1-6 are precordial and 7,8,9 are RA,LA,LL')
    	args = parser.parse_args()

    	main(args)

