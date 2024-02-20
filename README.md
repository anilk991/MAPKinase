# MAPKinase
Network modeling and analysis of MAP Kinase pathway to assess role of genes in tumor development


## Requirements
1. Python 2
2. BooleanNet Library
3. Matplotlib Library


## How to use:
The baseline.py accepts only one command line arguement: --end_state, it has to be one of Proliferation, Apoptosis, or Growth_Arrest.

In simulations.py and simulations_Bladder_Cancer.py scripts accept two command line arguements: 1.) --end_state and 2.) --type. The second arguement refers to the type of perutbations to be considered, whether constitutive activity (CA) or knockout (KO).

