#!/bin/bash


INIT="./generate_init.py"
FUNCTIONS="./functions.py"


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
	echo "Syntax: [-h --help|-vf --velocity|-n --node|-m --mesh|-Tm --Tmeasured|-d --dead_tissue|-bz --border_zone]"
	echo ""
	echo -e "-h   | --help			Help"
	echo -e "-vf  | --velocity		Velocity along fibers, starting point"
	echo -e "-n   | --node			Node or nodes.vtx for eikonal pacing"
	echo -e "-m   | --mesh			Meshname"
	echo -e "-Tm  | --Tmeasured		Measured QRSs or measured activation time"
	echo -e "-d   | --dead_tissue      	Tag of dead tissue, if existent (otherwise, enter 0)"
	echo -e "-lv  | --left_vent             Tag of LV, if existent (otherwise, enter -1)"
	echo -e "-rv  | --right_vent            Tag of RV, if existent (otherwise, enter -1)"
	echo -e "-bz  | --border_zone      	Tag of border zone, if existent (otherwise, enter 0)"
	echo -e ""
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
		-d=*|--dead_tissue=*)
                DEAD="${i#*=}"
                shift # past argument with no value
		;;
		-lv=*|--left_vent=*)
                LV="${i#*=}"
                shift # past argument with no value
                ;;
		-rv=*|--right_vent=*)
                RV="${i#*=}"
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

max_iter=100
i=1
tol=.025

while [ $i -lt $max_iter ]
do

	VS=`echo "$VF*.45" | bc`
	VN=$VS

	echo "Generating init file with ..."
	echo "Vf: $VF, Vs: $VS, Vn: $VN"
	echo "Node: $NODE"
	echo "Border zone: $BZ"
	echo "Dead tissue: $DEAD"
	echo ""
	$INIT --vf ${VF} --vs ${VS} --vn ${VN} --node ${NODE} --bz ${BZ} --lv ${LV} --rv ${RV} # remove or not border zone
	echo "Launching ek simulation ..."
	
	# if there is dead tissue

	if [ $DEAD -gt 0 ] ; then
		echo "Blocking dead tissue ...\n"
		if [ $RV -lt 0 ] ; then
			echo "No rv tag ...\n"
			ekbatch ${MESH} at $LV,${BZ} > output.txt
		else
			ekbatch ${MESH} at ${LV},${RV},${BZ} > output.txt
		fi
	else
		echo "No dead tissue ...\n"
		ekbatch ${MESH} at > output.txt
	fi

	echo "Reading at.dat, checking for inf values and computing activation time..."
	$FUNCTIONS check_inf at.dat
	Ts=$($FUNCTIONS calculate at.dat)
	Ts=`echo $Ts | awk '{print int($1+0.5)}'`

	echo "Tm: $TM	while Ts: $Ts"
	DIFF="$(($Ts-$TM))"

	if [ $DIFF -lt 0 ] ; then
		sign=-1
		DIFF="$(($DIFF * $sign))"
	fi

	if [ $DIFF -lt 15 ] ; then
		tol=0.005
	else
		if [ $DIFF -gt 30 ] ; then
			tol=0.1
		fi
	fi

	if [ $Ts -eq $TM ] 
	then
		echo "FINAL Vf: $VF, Vs: $VS, Vn: $VN"
		exit
	else

		if [ $Ts -lt $TM ]
		then
			VF=`echo "$VF - $VF*$tol" | bc`			
		else
			VF=`echo "$VF + $VF*$tol" | bc`
		fi
	fi


	let i=i+1
done
