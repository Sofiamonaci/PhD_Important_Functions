#!/bin/bash

# Pipeline to go from scar nodal files to myocardial mesh (and generate activation map, voltage files and corresponding voltage state file), to phie_recovery and lead fields for ECG and EGM 
#
#
# Sofia Monaci
# 26/07/2021


## Generate scar nodal files in the home desktop and transfer all .dat file into /scratch/sm18/VT/Scars ##

if [ -z "$1" ] # || [ "$1" -eq "-h" ] || [ "$1" -eq "help" ]
then
	echo -e "\nPipeline to generate myocardial and torso meshes from scar nodal file .dat generated in the home desktop and launch corresponding simulations for VT induction\n"
	echo -e "\tPlease provide  name of file of interest e.g Epicardial_scar_2"
	echo -e "\tPlease provide extension name for myo and Torso (e.g. final, reg_female"
	echo ""
else

	FILE=$1
	EXT=$2
	EXT1="NK"
	UVC="/media/sm18/Seagate Backup Plus Drive/PhD/Scripts/UVC/torso_"${EXT1}"_uvc/UVC/COORDS_RHO.dat"
	MESH="../"
	SCAR="./"
	
	echo -e "\n\tNodal file ${FILE} in ${SCAR}"
	echo "---------------------------------------------------"
	echo -e "\n\nGenerating elem/myo "


	rm *surf

	# Generating myo
	Scar_elem_to_mesh.py --value 28 --edat "$SCAR"/${FILE}_elem --mesh "$MESH"/myo_${EXT} --out "$SCAR" --rho "$UVC"

	echo "---------------------------------------------------"
	echo -e "Extracting myocardium\n"

	# Extracting myocardium
	meshtool extract myocard -msh="$SCAR"/${FILE}_myo -submsh="$SCAR"/myocard_scar >> out.txt 


	echo "---------------------------------------------------"
	echo -e "Generating torso\n"	
	# Generating torso
	meshtool insert submesh -submsh="$SCAR"/${FILE}_myo -msh="$MESH"/Torso_${EXT} -outmsh="$SCAR"/Torso_scar  -ofmt=carp_bin >> out.txt 


	echo "---------------------------------------------------"
	echo -e "Generating lead field .vtx file\n"
	# Generate lead field .vtx file
	meshtool query idxlist -msh="$SCAR"/Torso_scar -coord="$SCAR"/LF_electrodes.csv >> out.txt
	mv "$SCAR"/LF_electrodes.csv.out.txt "$SCAR"/LF_electrodes.vtx


	echo "---------------------------------------------------"
	echo -e "Running ekbatch\n"
#	# Run ekbatch for exit and entrance .init
	ekbatch "$SCAR"/${FILE}_myo "$SCAR"/VT_exit 26,27,29,31
	ekbatch "$SCAR"/${FILE}_myo "$SCAR"/VT_entrance 26,27,29,30 

	echo "---------------------------------------------------"
	echo -e "Extracting ekbatch results onto myocardium (exit)"
	# Extract activation maps
	meshtool extract data -submsh="$SCAR"/myocard_scar -msh_data="$SCAR"/VT_exit.dat -submsh_data="$SCAR"/VT_exit.dat >> out.txt

	echo "---------------------------------------------------"
	echo -e "Extracting ekbatch results onto myocardium (entrance)\n"
	meshtool extract data -submsh="$SCAR"/myocard_scar -msh_data="$SCAR"/VT_entrance.dat -submsh_data="$SCAR"/VT_entrance.dat >> out.txt


	echo "---------------------------------------------------"
	echo "Transfer everything on HPC TOM2"
	# Transfer everything on HPC
	mv "$SCAR"/${FILE}_myo.pts "$SCAR"/myo_scar.pts >> out.txt 
	mv "$SCAR"/${FILE}_myo.elem "$SCAR"/myo_scar.elem >> out.txt 
	mv "$SCAR"/${FILE}_myo.lon "$SCAR"/myo_scar.lon >> out.txt 

	n_elem=$(head -n 1 "$MESH"/Torso_${EXT}.elem)
	n_nodes=$(head -n 1 "$MESH"/Torso_${EXT}.pts)
	new_header="18 # mesh extra $n_elem $n_nodes" 
        sed -i "1 s/^.*$/$new_header/" "$SCAR"/LF_electrodes.vtx

	scp "$SCAR"/myo_scar.* "$SCAR"/Torso_scar.b* "$SCAR"/VT_*.dat sm18@tom2-login.hpc.isd.kcl.ac.uk:/scratch/sm18/Scar


fi
