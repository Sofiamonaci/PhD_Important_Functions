#!/bin/bash

## To run this second part, make sure you have all files and folder necessary for lead-field + eikonal simulations !!!
# And remember to adjust resolution an ECGm (measured ECG file of interest)

INIT="./generate_init.py"
FUNCTIONS="./functions.py"
PARAM_PY="./generate_param.py"
COMPUTE_QRS_d="./qrs_correlation.py"

# ENTER PATH of TUNECV
TuneCV="/home/sm18/Software/CARP/carputils/bin/tuneCV"

#########################################################################
# Help                                                                  #
#########################################################################

helpFunction()
{
	#Display Help
	echo ""
	echo ""
	echo "Function to parametrize simulated activation time duration to measured QRS"
	echo "" 
	echo "Syntax: [-h --help|-vf --velocity|-n --node|-m --mesh|-Tm --Tmeasured|-bz --border_zone]"
	echo ""
	echo -e "-h  | --help		Help"
	echo -e "-vf | --velocity	Velocity along fibers, starting point"
	echo -e "-n  | --node		Node or nodes.vtx for eikonal pacing"
	echo -e "-m  | --mesh		Meshname"
	echo -e "-Tm | --Tmeasured	Measured QRS duration"
	echo -e "-ni | --iter           Number of iterations to perform"
	echo -e "-bz | --border_zone    Tag of border zone, if existent (otherwise, enter 0)"
	echo -e " "
	exit 1
}


##########################################################################
##########################################################################
# Main program                                                           #
##########################################################################
##########################################################################

for i in "$@"
do
	case $i in
    		-h|--help)
    		helpFunction
    		exit # past argument=value
    		;;
    		-vf=*|--velocity=*)
    		VF="${i#*=}"
    		shift # past argument=value
    		;;
    		-n=*|--node=*)
    		NODE="${i#*=}"
   		shift # past argument=value
    		;;
    		-m=*|--mesh=*)
    		MESH="${i#*=}"
    		shift # past argument with no value
    		;;
    		-Tm=*|--Tmeasured=*)
    		TM="${i#*=}"
    		shift # past argument with no value
    		;;
		-ni=*|--iter=*)
                max_iter="${i#*=}"
                shift # past argument with no value
                ;;
		-bz=*|--border_zone=*)
                BZ="${i#*=}"
                shift # past argument with no value
                ;;
    		*)
    		echo "Unknown Option!"
    		helpFunction
    		exit
    		;;
	esac
done

i=1

echo "Writing stim.vtx "

cat > stim.vtx <<EOF
1
extra
$NODE
EOF


while [ $i -lt $max_iter ]
do

	vf=`echo "$VF" | bc -l | sed 's/0*\././g'`
	VS=`echo "$vf*.45" | bc`
	VN=$VS

	# tune gi and ge
	echo "Tuning gi and ge with $VF and $VS"

	$TuneCV --resolution=800 --length=1 --model=TT2 --dt=25 --velocity=$VF --sourceModel=monodomain --maxit=50 --lumping=false --tol=0.001 --converge=true --ts=1 --ID=tune_myo > output.txt

	mv results.* tune$VF.dat
	rm -r tune_myo*/
	rm *log
	rm -r meshes/

	$TuneCV --resolution=800 --length=1 --model=TT2 --dt=25 --velocity=$VS --sourceModel=monodomain --maxit=50 --lumping=false --tol=0.001 --converge=true --ts=1 --ID=tune_myo >> output.txt
	
	mv results.* tune$VS.dat
        rm -r tune_myo*/
        rm *log
        rm -r meshes/

	# Read tuned conductivities
        echo "Prepare extra parameter file ..."
	rm extra_param.par
	rm extra_lead_field.par

	if [ $BZ -gt 0 ] ; then
		echo "Copying eikonal_scar.par ..."
		cp eikonal_scar.par extra_param.par # modify tag of scar tissue in eikonal_scar.par
	else
		echo "Copying eikonal.par and lead_field.par .."
		cp eikonal.par extra_param.par
		cp lead_field.par extra_lead_field.par
	fi
	
	# Adding new conductivities and velocities to eikonal.par
	$PARAM_PY --vf=$VF --vs=$VS --gl=tune$VF.dat --gt=tune$VS.dat --bz=$BZ		
	# Adding new conductivities to lead_field.par
	$PARAM_PY --vf=0 --vs=0 --gl=tune$VF.dat --gt=tune$VS.dat --bz=$BZ --out=extra_lead_field.par
	
	# Run lead field + eikonal
	echo "Run lead field ..."
	rm -r ./lead_field/
	echo "Enter torso mesh: "
	./run_lead_field.sh ../Torso_final_reg
	
	echo "Run lead field + eikonal ..."
	./run_RE_LF.sh $MESH eikonal_${VF}_vf_sim

	# Run python function to compute simulated QRSs (first V1 lead) and compare it with measured Tm --> it returns new VF value and flag (whether to exit or not)

	echo "################################################"
	echo "###############################################"

	echo "Computing simulation QRS ..."
	$COMPUTE_QRS_d --Tm=$TM --Ts=./lead_field/eikonal_${VF}_vf_sim.dat --vf=$VF --ECGm='../../VT/ecg/_De-identified 01_ve_ecg.csv'

	FLAG=$($FUNCTIONS read flag.dat)
	VF=$($FUNCTIONS read vf.dat)

	#if [ $FLAG -eq 1 ]
	#then
	#	echo "QRSs matched at Vf: $VF and Vs: $VS"
	#	exit
	#fi
	
	let i=i+1
done
