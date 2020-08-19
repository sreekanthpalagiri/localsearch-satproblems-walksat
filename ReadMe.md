Student ID: R00184198
Name: Sreekanth Palagiri

Please pip install below libraries used:
random, collections, time, statistics, matplotlib, os, sys

GWSAT
----------------------------------------------------------------------------------
Python File:  Palagiri_R00184198_GWSAT.py
Description: Main Executable for gwsat 

Please execute using:
		python Palagiri_R00184198_GWSAT.py uf50-01.cnf 100 10 1000 0.4

uf50-01.cnf is the file name. File should be present in data folder.
100 - No. of executions
10 - No. of restarts
1000 - No. of iterations
0.4 - wp

Program will ask for user input for generation of RTD plot, Please select Y or N
	
Program will execute and display in command prompt/editor the current execution number, try and iteration satisfying solution reached 
and solution achived. Program on completion will display plot and RTD descriptive values used in the report. 

For any new instance file, please put the file in data folder and update instance file name parameter 


WALKSAT/SKC with Tabu
----------------------------------------------------------------------------------
Python File: Palagiri_R00184198_WalkSAT.py
Description: Main Executable for gwsat 

Please execute using:
		python Palagiri_R00184198_WalkSAT.py uf50-01.cnf 100 1000 10 0.4 5

uf50-01.cnf is the file name. File should be present in data folder.
100 - No. of executions
1000 - No. of iterations
10 - No. of restarts
0.4 - wp
5 - tabu size

Program will ask for user input for generation of RTD plot, Please select Y or N
	
Program will execute and display in command prompt/editor the current execution number, try and iteration satisfying solution reached 
and solution achived. Program on completion will display plot and RTD descriptive values used in the report. 

For any new instance file, please put the file in data folder and update instance file name parameter.

"# localsearch-satproblems-walksat" 
