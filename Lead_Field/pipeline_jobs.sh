#!/bin/bash

# BASH SCRIPT TO INDUCE FAST VT ON A TORSO MESH
#
# Run lead field and reaction eikonal first and then run lead_field + phie_recovery to get ECG and EGMs

echo "Removing LF and Sim folders ..."
rm -r /scratch/sm18/Scar/LF
rm -r /scratch/sm18/Scar/Sim

echo "Removing old *.out and *.err files ..."
rm *.err
rm *.out
rm init_*dat

# Taking reference node from LAST line in LF_electrodes.vtx
# change number 19 according to how many points you are computing the
# lead fields on (in my case 9 ECGs + 8 EGMs, but there is header to skip, and reference node last)

REF=$(sed '19q;d' "/scratch/sm18/Scar/LF_electrodes.vtx")

# Running reaction-eikonal no diffusion
echo "Running RE- ..."
JOB1=$(sbatch run_RE.pbs)

# Computing lead fields on torso mesh
echo "Running lead field after RE- ..."
JOB2=$(sbatch --dependency=afterok:${JOB1##* } lead_field.pbs $REF)

# Running LF-RE
echo "Running LF as dependency of previous jobs"
JOB3=$(sbatch --dependency=afterok:${JOB1##* }:${JOB2##* } run_LF_RE.pbs $REF)

echo "Job1: ${JOB1##* }"
echo "Job2: ${JOB2##* }"
echo "Job3: ${JOB3##* }"

echo "Reference ground node for LF computations: $REF"
