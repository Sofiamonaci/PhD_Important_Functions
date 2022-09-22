# About

This repository contains main .mat and .py scripts used throughout my PhD to process, manipulate, plot data, generate virtual scars, run automated pipleines etc etc. 

Under ./Scar_Generation, you can find all scripts to generate simplistic, virtual scars around a mesh of interest, and how to embed them into a torso and/or heart mesh

Under ./QRS_Parametrisation, you can find scripts to parametrise conduction velocities and conductivities according to a reference (clinical) QRS/ECG signal. You can either run lead field or phie recovery (you need to generate these simulation files yourself)

Under ./Lead_Field, you can find CARP and SLURM files to induce fast VT episodes within a LF-RE environment. These files can be used not only to induce VT in an efficient way (after a simplistic/virtual scar as above has been generated), but also as examples to run lead field - reaction eikonal simulations.

You can also visit my bitbucket Wiki and repository for more

https://bitbucket.org/Sofiamonaci/phd/src/master/
