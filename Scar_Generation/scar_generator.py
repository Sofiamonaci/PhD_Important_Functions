#!/usr/bin/env python

import gi
import os
import sys
import numpy as np
import pandas as pd
import argparse

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from ScarParameter_GUI import *
from Tag_Exit_Entrance import create_init
import math as m
import glob



def elliptic_cylinder(pts,rho,c1,u1,c,param,flag):


	# Functions input:
	# pts:    mesh points
	# rho:    rho coordinates (shape[0] == mesh points[0])
	# c1:     centroid dead tissue
	# u1:     fiber direction of centroid (or point of max activation of dead tissue)
	# c:      centroid isthmus
	# param:  [length,width,trans] --> length, width in mm, trans between 0-1
	# flag:   Type of scar --> 'Endocardial' or 'Epicardial'

	print('\n\nComputing elliptic cilynder for dead tissue ...\n\n')

	# Resolution rho
	d_rho = np.unique(rho)[1] - np.unique(rho)[0]

	# Find surface equal to transmurality of interest
	if 'Endo' in flag:
        	surf = pts[ abs(rho - param[2]) <=d_rho , :]
	else:
		surf = pts[ abs(rho - (1 - param[2])) <=d_rho , :]

        # projection centroid of dead tissue onto this surf
        proj = surf[np.linalg.norm(surf - c1, axis=1).argmin(),:]

	dist = min(np.linalg.norm(surf - c1, axis=1))

	# Define centre of elliptic cilynder	
#	o = np.mean([proj,c1],axis=0)

	o = c1

	# Define diagonal parameters matrix
	D = np.identity(3) * np.array([(1000*param[0]/2)**(-2),(1000*param[1]/2)**(-2),0])

	# Define orthogonal matrix with ellipse axis

	i = u1
#	i = u1 - c1
	j = c - c1
	k = proj - c1

	i = i/np.linalg.norm(i)
	j = j/np.linalg.norm(j)
	k = k/np.linalg.norm(k)

	Q_T     = np.array([i,j,k])
	Q   = np.transpose(Q_T)

	A = np.matmul(np.matmul(Q,D),Q_T)
	
	# Exclude points in the opposite wall
	# Centroid of rv/lv
        centroid = np.mean(pts, axis=0)
	n_short = c1 - centroid
        n_short = n_short/np.linalg.norm(n_short)

	ind = np.where(np.dot(pts - centroid,n_short)>=0)[0]

	equation = np.zeros((ind.shape[0],),)

	for x in range(ind.shape[0]):
		equation[x] = np.dot(np.dot(pts[ind[x],:] - o, A), np.transpose(pts[ind[x],:]-o))

	final_ind = ind[np.where(equation<=1)[0]]

	return final_ind


#UNCTIONS TO GENERATE A COMBINATION OF SCAR PARAMETERS
class Set_Parameters():
    def __init__(self, type_scar='Epicardial',flag=1):

        # if flag == 1 or 2, generate same scars across all segments
        self.channels = np.array([1,1,0])
	self.type = type_scar

	# Same scar parameters across LV
        if flag==1:
            print('\t\tGENERATING SAME SCAR ACROSS LV\n\n')       
            self.mesh="LV"
            self.segment = np.array(range(16)) + 1
            self.length = np.zeros((16,), dtype=float) + 40
            self.width = np.zeros((16,), dtype=float) + 9
            self.trans = np.zeros((16,), dtype=float) + 100
            self.type =  np.array([type_scar] * 17)
	
	# Same scar parameters across RV
	elif flag==2:
            print('\t\tGENERATING SAME SCAR ACROSS RV\n\n')
	    self.mesh="RV"
            self.segment = np.array([18,19,20,22,23,24,25])
            self.length = np.zeros((8,), dtype=float) + 25
            self.width = np.zeros((8,), dtype=float) + 8
            self.trans = np.zeros((8,), dtype=float) + 60
            self.type =  np.array([type_scar] * 8)
	
	# Same segments but different parameters
	elif flag==3:
	    print('\t\tGENERATING DIFFERENT SCAR IN THE SAME SEGMENT\n\n')	    
            self.mesh="LV"
	    self.segment = np.zeros((10,), dtype = int) + 12
	    self.width = np.array([6.5,16.5,21.5,11.5,11.5,11.5,11.5,11.5,11.5,11.5])
	    self.length = np.array([25,25,25,10,15,20,30,25,25,25])
	    self.trans = np.array([60,60,60,60,60,60,60,30,80,100])
	    self.type = np.array([type_scar] * 10)


# INTERPOLATE NODE DATA TO ELEMENTS WITH APPROPRIATE ROUNDING
def interpolate_node2elem(mesh,dat,n,out):

    print('\nCreating elem file..')
    tags = np.unique(dat[dat>0])

    elem = np.zeros((n,), dtype=int)
    for l in tags:

        node_dat = dat*0
        node_dat[dat==l] = 1
        np.savetxt(out+'_elem.dat',node_dat)
        os.system("meshtool interpolate node2elem -omsh=%s -idat=%s_elem.dat -odat=%s_elem.dat >/dev/null"%(mesh,out,out))
        elem_dat = pd.read_csv(out+'_elem.dat',delimiter=' ',header=None).values.flatten()
        elem[elem_dat>0]=l

    print('Writing %s_elem.dat ...' % (out))
    np.savetxt(out+'_elem.dat',elem)
    
    return elem

# Find index of cartesian point
def find_ind(pts,query):

    ind = np.zeros((query.shape[0],), dtype=int)
    for i in range(len(ind)):
        d = np.linalg.norm(pts - query[i,:], axis=1)
        ind[i] = d.argmin()

    return ind

# CONVERTING UVC POINT(S) INTO CORRESPONDING CARTESIAN, RETURNING INDEX(INDICES) AS WELL
def convert_uvc_to_pts(uvc,query,pts):

    scaling = np.zeros((3,), dtype=int)
    scaling[0] = 3  # Z
    scaling[1] = 1  # Phi
    scaling[2] = 0.33  # Rho

    ind = np.zeros((query.shape[0],), dtype=int)
    new_query = np.zeros((query.shape), dtype=float)
    for i in range(query.shape[0]):
        d = np.sqrt((scaling * np.multiply(uvc - query[i, :], uvc - query[i, :])).sum(axis=1))
        new_query[i, :] = pts[d.argmin(), :]
        ind[i] = d.argmin()

    return new_query,ind

# DEFINING CLASS FOR GENERATION OF SCAR
class Scar:
    def __init__(self,pts,uvc):

        self.c_xyz = np.zeros((3,), dtype=float)
        self.dat = np.zeros((pts.shape[0], ), dtype=int)

        # Computing resolutions in uvc and mm
        z = np.unique(uvc[:,0])
        self.res_z = z[1] - z[0]

        self.res_mm = float(0.5)

        phi = np.unique(uvc[:,1])
        self.res_phi = phi[1] - phi[0]

        rho = np.unique(uvc[:,2])
        self.res_rho = rho[1] - rho[0]


# Define plane that passes through a point (centroid of dead tissue) and it is perpendicular to Centroid_isthmus - Centroid_deadtissue

    def define_plane_isthmus(self,pts,rho,c1,c2,l,u,flag="Endo"):


	# Centroid of rv/lv
	centroid = np.mean(pts, axis=0)

	# Define surface opposite to flag
	surf = pts[ rho==(1 - ('Epi' in flag)), :]

	# projection centroid of dead tissue onto this surf
	proj = surf[np.linalg.norm(surf - c1, axis=1).argmin(),:]
	
	print(proj)

	A = l - proj
	A = A/np.linalg.norm(A)

	B = u - proj
	B = B/np.linalg.norm(B)


	# Compute norm of plane
	n = np.cross(A,B)
	n = n/np.linalg.norm(n)

	# direction
	direction = np.dot(self.c_xyz - proj,n)

	if direction <= 0:
		n = -n

	n_short = np.mean([c1,c2], axis=0) - centroid
	n_short = n_short/np.linalg.norm(n_short)

	# plane points
	plane_ind = np.where(((np.dot(pts - c1,n)>=0) & (np.dot(pts - c2,n)<=0))  &  (np.dot(pts - centroid,n_short)>=0))[0]

	return pts[plane_ind,:], plane_ind


# COMPUTING DEAD TISSUE BY LOADING ACTIVATION MAP FROM EKBATCH
    def ekbatch_ellipse(self,pts,at,rho,param,c,flag="Endo"):


	dt = np.unique(at)
	dt = dt[1] - dt[0]

    	# Compute distance of all points of mesh with centroid of dead tissue 
    	dist = np.linalg.norm(pts - c, axis=1)/1000

    	# Find activation points for points <= width/2  and >= height/2
    	at_width = max(at[dist<=param[1]/2])
    	at_length = min(at[dist>=param[0]/2])

	# printing boundaries of dead tissue
	print('\nBoundaries of dead tissue are: %.3f (along "width") and %.3f (along "length)": \n' %(at_width,at_length))

    	# Find transmurality
    	if "Endo" in flag:
        	trans = np.where(rho<=param[2])[0]
    	else:
        	trans = np.where(rho>=(1-param[2]))[0]

    	pts = pts[trans,:]
    	at = at[trans]

#	if at_width<=at_length:

	# scaling for bz around dead tissue
	scaling = 2.5
	dead_ind = np.where((at<=at_width) & (np.linalg.norm(pts - c,axis=1)/1000 <= param[0]/2))[0]
	bz_ind = np.where((at<=(at_width + scaling*dt)) & (np.linalg.norm(pts - c,axis=1)/1000 <= param[0]/2))[0]		
    	dead_pts = pts[dead_ind,:]
	bz_pts = pts[bz_ind,:]

    	return dead_pts, trans[dead_ind],bz_pts, trans[bz_ind]

# GENERATING CHANNEL
    def define_channel(self,pts,dat,u,l,param,uvc,plane_ind):
	# ind_dead1, ind_dead2


	res = np.unique(dat)
	res = res[1] - res[0]

	dat = dat[plane_ind]
	ind = np.where((dat>=l)*(dat<=u))[0]

	scaling = 15
	exit_ind = np.where((dat>=(u-scaling*res))*(dat<=u))[0]
	entrance_ind = np.where((dat>=l)*(dat<=(l+scaling*res)))[0]
	exit = pts[plane_ind[exit_ind],:]
	entrance = pts[plane_ind[entrance_ind],:]


        channel = pts[plane_ind[ind],:]


	if self.c_uvc[2]==0:
		ind_channel = np.where((uvc[plane_ind[ind],2]<=param[2]))[0]
		channel = channel[ind_channel,:]


		exit_ind = plane_ind[exit_ind[np.where(uvc[plane_ind[exit_ind],2]<=param[2])[0]]]
		entrance_ind = plane_ind[entrance_ind[np.where(uvc[plane_ind[entrance_ind],2]<=param[2])[0]]]
	else:
		ind_channel = np.where((uvc[plane_ind[ind],2]>=(1 - param[2])))[0]
		channel = channel[ind_channel,:]

		exit_ind = plane_ind[exit_ind[np.where(uvc[plane_ind[exit_ind],2]>=(1-param[2]))[0]]]
       	        entrance_ind = plane_ind[entrance_ind[np.where(uvc[plane_ind[entrance_ind],2]>=(1-param[2]))[0]]]


	print('Exit tags n: %d'%(exit_ind.shape[0]))
	print('Entrance tags n: %d'%(entrance_ind.shape[0]))


	return channel, plane_ind[ind[ind_channel]], exit_ind, entrance_ind


# COMPUTING DEAD TISSUES CENTROIDS ACCORDING TO DESIRED WIDTH OF ISTHMUS
    def centroid_deadtissue(self,pts,z,rho,width):

        # Initialise centroids dead tissue
        new_centroids = np.zeros((2,3), dtype=float)
        # Find distance between centroid and points at same z of centroid        

	# Find centroid using z = activation map from apex
	dt = np.unique(z)
	dt = dt[1] - dt[0]
	ind_z = np.where((abs(z-z[self.ind])<=dt)*(abs(rho-self.c_uvc[2])<=self.res_rho))[0]
        
	dist = np.linalg.norm(pts[ind_z,:] - self.c_xyz, axis=1)/1000
        ind_width = np.where(dist>=width)[0]

        # First centroid
        c_1 = dist[ind_width].argmin()
        ind_new = ind_width[c_1]
        new_centroids[0,:] = pts[ind_z[ind_new],:]
        n_c1 = (new_centroids[0,:]-self.c_xyz)/np.linalg.norm(new_centroids[0,:]-self.c_xyz)

        ind_width = np.delete(ind_width,c_1)
        # Second centroid
        n_c2 = (pts[ind_z[ind_width],:] - self.c_xyz)/np.linalg.norm((pts[ind_z[ind_width],:] - self.c_xyz))
        opposite = np.where((np.multiply(n_c2,n_c1).sum(axis=1))<0)[0]

        c_2 = dist[ind_width[opposite]].argmin()
        new_centroids[1,:] = pts[ind_z[ind_width[opposite[c_2]]],:]

        return new_centroids, np.append(ind_z[ind_new],ind_z[ind_width[opposite[c_2]]])


# COMPUTING CENTROID ISTHMUS IN UVc
    def uvc_centroid(self,pts,uvc):

        dist = np.linalg.norm(pts - self.c_xyz, axis=1)
        self.c_uvc = uvc[dist==min(dist),:]
        print('UVC centroid: (%.3f,%.3f,%.3f)' % (self.c_uvc[0,0],self.c_uvc[0,1],self.c_uvc[0,2]))

# COMPUTING CENTROID ISTHMUS IN CARTESIAN
    def geom_centroid(self, pts, seg, aha, rho, flag):

        # Select endo or epicardial surfaces
        rho = rho[aha==seg]
        pts = pts[aha==seg]
	ind = np.where(aha==seg)[0]

        if "Endo" in flag:
            surf_pts = pts[rho[:,]==0,:]
	    surf_ind = np.where(rho==0)[0]
            self.c_xyz = np.mean(surf_pts, axis=0)
        else:
            surf_pts = pts[rho[:,]==1,:]
            surf_ind = np.where(rho==1)[0]
            self.c_xyz = np.mean(surf_pts, axis=0)

        # Find actual point
        dist = np.linalg.norm(surf_pts - self.c_xyz, axis=1)
        self.c_xyz = surf_pts[dist==min(dist),:]
	self.ind = ind[surf_ind[dist.argmin()]]

        print('')
        print('Centre of mid isthmus: (%.3f,%.3f,%.3f)' % (self.c_xyz[0,0],self.c_xyz[0,1],self.c_xyz[0,2]))
        print('')

######################## MAIN FUNCTION #############################
####################################################################

## GENERATING SCAR ACCORDING TO INPUT PARAMETERS AND MESH OF INTEREST
def main(args):

####################################################################
########################## READ ####################################

    print('\n\n')
    print('Reading %s.pts ...' % (args.mesh))
    pts = pd.read_csv(args.mesh+'.pts', delimiter=' ', header=None, skiprows=1).values

    pts = pd.read_csv(args.mesh+'.pts', delimiter=' ', header=None, skiprows=1).values

    print('Reading %s.elem ...' % (args.mesh))
    elem = pd.read_csv(args.mesh+'.elem', delimiter=' ', header=None, skiprows=1, usecols=[1,2,3,4]).values

    print('Shape elements: ')
    print(elem.shape)

    print('Reading %s.lon ...' % (args.mesh))
    lon = pd.read_csv(args.mesh+'.lon', delimiter=' ', header=None, skiprows=1).values
    
    print('Shape lon: ')
    print(lon.shape)

    print('Reading %s ...' % (args.aha))
    aha = pd.read_csv(args.aha, delimiter=' ', header=None).values.flatten()

    print('Reading %s/files ...\n\n' % (args.uvc))
    z = pd.read_csv(args.uvc + '/COORDS_Z.dat', delimiter=' ', header=None).values.flatten()
    phi = pd.read_csv(args.uvc + '/COORDS_PHI.dat', delimiter=' ', header=None).values.flatten()
    rho = pd.read_csv(args.uvc + '/COORDS_RHO.dat', delimiter=' ', header=None).values.flatten()
    v = pd.read_csv(args.uvc + '/COORDS_V.dat', delimiter=' ', header=None).values.flatten()


#####################################################################
###################### INITIALISE SCAR PARAMETERS ###################
    print('--------------------------------------------------')
    print('GUI Commands')
    #scar = Parameters()
    scar = Set_Parameters(type_scar=args.scar,flag=args.flag)
    #scar.connect("destroy", Gtk.main_quit)
    #scar.show_all()
    #Gtk.main()
    #print('')
    #print('')
    #print('Final Parameters ....')
    #print('Segment: '+ str(scar.segment))
    #print('Type: '+scar.type)
    #print('Exit: '+ str(scar.channels[0]))
    #print('Entrance: '+ str(scar.channels[1]))
    #print('Dead end: '+ str(scar.channels[2]))
    #print('Length: '+ str(scar.length))
    #print('Width: '+ str(scar.width))
    #print('Transmurality '+ str(scar.trans))
    #print('Mesh to consider: ' + scar.mesh)
    #print('--------------------------------------------------')

######################################################################

    if "RV" in scar.mesh:
        tag_v = 1
        print('Considering RV segments ...')
    else:
        tag_v = -1
        print('Considering LV segments ...')

    # CONSIDERING LV OR RV MESH
    uvc = np.zeros((len(v[v==tag_v]),3), dtype=float)
    uvc[:,0] = z[v==tag_v]
    uvc[:,1] = phi[v==tag_v]
    uvc[:,2] = rho[v==tag_v]

    pts = pts[v==tag_v,:]
    aha = aha[v==tag_v]

    ind_submsh = np.where(v==tag_v)
    ind_submsh = np.asarray(ind_submsh[0])

    if all(scar.channels == [1,1,0]):

        # Loop over all segments
#        for i,_ in enumerate(scar.segment):
	for i in range(6,16):

            print('Final Parameters ....')
            print('Segment: ' + str(scar.segment[i]))
            print('Type: ' + scar.type[i])
            print('Exit: ' + str(scar.channels[0]))
            print('Entrance: ' + str(scar.channels[1]))
            print('Dead end: ' + str(scar.channels[2]))
            print('Length: ' + str(scar.length[i]))
            print('Width: ' + str(scar.width[i]))
            print('Transmurality ' + str(scar.trans[i]))
            print('Mesh to consider: ' + scar.mesh)
            print('--------------------------------------------------')

            param = np.array([scar.length[i],scar.width[i], scar.trans[i]/100])

            # Define scar
            Scar_1 = Scar(pts,uvc)


########################################################################################################
######################################### COMPUTE CENTROIDS ############################################

            # Compute geometrical centroid for surface "scar.type" of "scar.segment" of interest
            Scar_1.geom_centroid(pts,scar.segment[i],aha,uvc[:,2],scar.type[i])

            # Compute its corresponding uvc coordinates
	    Scar_1.c_uvc = uvc[Scar_1.ind,:]
	    print('UVC centroid: ')
	    print(Scar_1.c_uvc)

	    if not os.path.exists(args.out+"/apex.dat"):
                create_init(args.out+"/apex.init",538959,np.asarray([0.97,0.14,0.14]))
                command = "ekbatch " + args.mesh + " " + args.out + "/apex 2,4 >/dev/null"
                os.system(command)

            at3 = pd.read_csv(args.out + "/apex.dat", header=None, delimiter=' ').values.flatten()


            # Compute centroids of dead tissue
	
            c_dead, ind_c = Scar_1.centroid_deadtissue(pts,uvc[:,0],uvc[:,2],scar.width[i]) 

            print('Cartesian centroid for dead tissue 1: (%.3f,%.3f,%.0f) with index %d' %(c_dead[0,0],c_dead[0,1],c_dead[0,2],ind_submsh[ind_c[0]]))
            print('Cartesian centroid for dead tissue 2 : (%.3f,%.3f,%.0f) with index: %d' % (c_dead[1, 0], c_dead[1, 1], c_dead[1, 2], ind_submsh[ind_c[1]]))


	    
########################################################################################################
##################################### COMPUTE DEAD TISSUES ############################################

            # Create init and launch ekbatch for dead tissue 1 and 2
            create_init(args.out+"/at.init",ind_c[0],np.array([0.97,0.14,0.14])) 
            create_init(args.out+"/at2.init",ind_c[1], np.asarray([0.97,0.14,0.14])) 

            print('\n\n\nComputing dead tissue\n\n\n')
#            command = "ekbatch " + args.mesh + " " + args.out + "/at,"+args.out+"/at2 2,4 >/dev/null"
#            os.system(command)

#            at_dead1 = pd.read_csv(args.out+"/at.dat", header=None, delimiter=' ').values.flatten()


#            dead1,ind_dead1,bz1,ind_bz1 = Scar_1.ekbatch_ellipse(pts,at_dead1[ind_submsh],uvc[:,2],param,c_dead[0,:],flag=scar.type[i])

#            at_dead2 = pd.read_csv(args.out + "/at2.dat", header=None, delimiter=' ').values.flatten()
#            dead2,ind_dead2,bz2,ind_bz2 = Scar_1.ekbatch_ellipse(pts,at_dead2[ind_submsh],uvc[:,2],param,c_dead[1,:],flag=scar.type[i])



	    # Find fiber direction of dead tissue centroid
	    c1_lon = lon[(elem[:,0]==ind_submsh[ind_c[0]]) + (elem[:,1]==ind_submsh[ind_c[0]]) + (elem[:,2]==ind_submsh[ind_c[0]]) + (elem[:,3]==ind_submsh[ind_c[0]]),:]


	    c1_lon = np.mean(c1_lon, axis=0)
	    c1_lon = c1_lon/np.linalg.norm(c1_lon)

	    print('Fiber direction on centroid dead tissue 1: (%.3f,%.3f,%.3f)' %(c1_lon[0],c1_lon[1],c1_lon[2]))

	    c2_lon = lon[(elem[:,0]==ind_submsh[ind_c[1]]) + (elem[:,1]==ind_submsh[ind_c[1]]) + (elem[:,2]==ind_submsh[ind_c[1]]) + (elem[:,3]==ind_submsh[ind_c[1]]),:]


            c2_lon = np.mean(c2_lon, axis=0)
            c2_lon = c2_lon/np.linalg.norm(c2_lon)

	    print('Fiber direction on centroid dead tissue 2: (%.3f,%.3f,%.3f)' %(c2_lon[0],c2_lon[1],c2_lon[2]))

	    # Find minimum and maximum points of dead tissue 1

#	    l_dead1 = pts[ind_dead1[uvc[ind_dead1,0].argmin()],:] # at3[ind_submsh[ind_dead1]]
#            u_dead1 = pts[ind_dead1[uvc[ind_dead1,0].argmax()],:]


	    # Find minimum and maximum points of dead tissue 2
#	    l_dead2 = pts[ind_dead2[uvc[ind_dead2,0].argmin()],:]
#            u_dead2 = pts[ind_dead2[uvc[ind_dead2,0].argmax()],:]


	    new_ind_dead1 = elliptic_cylinder(pts,uvc[:,2],c_dead[0,:],c1_lon,Scar_1.c_xyz[0,:],param,scar.type[i])

	    new_ind_dead2 = elliptic_cylinder(pts,uvc[:,2],c_dead[1,:],c2_lon,Scar_1.c_xyz[0,:],param,scar.type[i])

	    dead1 = pts[new_ind_dead1,:]
	    dead2 = pts[new_ind_dead2,:]

	    ind_surf1 = np.where(uvc[new_ind_dead1,2]==(1 - ('Endo' in scar.type[i])))[0]
	    ind_surf2 = np.where(uvc[new_ind_dead2,2]==(1 - ('Endo' in scar.type[i])))[0]

	    surf1 = dead1[np.where(uvc[new_ind_dead1,2]==(1 - ('Endo' in scar.type[i])))[0],:]
	    surf2 = dead2[np.where(uvc[new_ind_dead2,2]==(1 - ('Endo' in scar.type[i])))[0],:]

	    l_dead1 = uvc[new_ind_dead1[ind_surf1],0].argmin()
            u_dead1 = uvc[new_ind_dead1[ind_surf1],0].argmax()

            l_dead2 = uvc[new_ind_dead2[ind_surf2],0].argmin()
            u_dead2 = uvc[new_ind_dead2[ind_surf2],0].argmax()

	     # Plane passing through the centroid of dead tissue (~ orthogonal to transmural coordinate
	    _,plane_ind1 = Scar_1.define_plane_isthmus(pts,uvc[:,2],c_dead[0,:],c_dead[1,:],surf1[l_dead1,:],surf1[u_dead1,:],flag=scar.type[i])

	    _,plane_ind2 = Scar_1.define_plane_isthmus(pts,uvc[:,2],c_dead[1,:],c_dead[0,:],surf2[l_dead2,:],surf2[u_dead2,:],flag=scar.type[i])

	    plane_ind = np.intersect1d(plane_ind1,plane_ind2)

############################################################################################################################################## COMPUTE ISTHMUS ##################################################

            # Create isthmus and mark entrance and exit
            print('\n\n\nGenerating isthmus\n\n\n')

	    if uvc[new_ind_dead1[ind_surf1[u_dead1]],0]>=uvc[new_ind_dead2[ind_surf2[u_dead2]],0]:
		u = uvc[new_ind_dead2[ind_surf2[u_dead2]],0]
	    else:
		u = uvc[new_ind_dead1[ind_surf1[u_dead1]],0]


	    if uvc[new_ind_dead1[ind_surf1[l_dead1]],0]>=uvc[new_ind_dead2[ind_surf2[l_dead2]],0]:
		l = uvc[new_ind_dead1[ind_surf1[l_dead1]],0]
	    else:
		l = uvc[new_ind_dead2[ind_surf2[l_dead2]],0]


#	    if (scar.segment[i]==8 and scar.segment[i]==14):

#	            channel,ind_channel,ind_exit,ind_entrance = Scar_1.define_channel(pts,at3[ind_submsh],new_ind_dead1,new_ind_dead2,param,uvc,plane_ind)

#	    else:

	    channel,ind_channel,ind_exit,ind_entrance = Scar_1.define_channel(pts,uvc[:,0],u,l,param,uvc,plane_ind) # new_ind_dead1, new_ind_dead2


########################################################################################################

            dat_scar = np.zeros((v.shape[0],), dtype=int) - 1
            dat_scar[ind_submsh[ind_channel]]=2
		
	    dat_scar[ind_submsh[ind_exit]]=3
            dat_scar[ind_submsh[ind_entrance]]=4

            dat_scar[ind_submsh[new_ind_dead1]]=1
            dat_scar[ind_submsh[new_ind_dead2]]=1

########################################################################################################
######################################### PRINT OUT FILE ###############################################

	    if args.flag < 3:
            	file_scar = args.out + scar.type[i] + "_scar_" + str(scar.segment[i])
            else:
		file_scar = args.out + scar.type[i] + "_scar_" + str(scar.segment[i]) + '_w' +str(param[1]) + 'mm_l' + str(param[0]) + 'mm_t' + str(scar.trans[i]) + 'percent'
		
            if os.path.exists(file_scar+".dat"):
                existing_file = np.asarray(glob.glob(file_scar + ".*.dat"))
                file_scar = file_scar + "." + str(existing_file.shape[0]+1)

            print('\n\nWriting out nodal information ...'+file_scar+".dat")
            np.savetxt(file_scar+".dat",dat_scar)

            print('DONE')

    else:
        sys.exit('Scar Generation only works with 1 exit, 1 entrance and 0 dead ends for now!')

####################################################################

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter
    parser.add_argument('--mesh', type=str, default="myo_final", help='Path to mesh points/elem')
    parser.add_argument('--aha', type=str, default="geom_17segs_myo.dat", help='17-segment aha file')
    parser.add_argument('--uvc', type=str, default="/media/sm18/Seagate Backup Plus Drive/PhD/Scripts/UVC/torso_female_uvc/UVC/", help='Path to uvc file')
    parser.add_argument('--out', type=str, default="./Scar_Generation/", help='Path to Output file')
    parser.add_argument('--flag', type=int, default=1, help= "Generate same scar across (1) or rv (2) or different scar in the same segment - to change manually (3)")
    parser.add_argument('--scar', type=str, default='Endo', help= "Type of scar: 'Endo' or 'Epi'")

    args = parser.parse_args()

    main(args)
