#!/usr/bin/env zsh
export PATH="$HOME/miniconda3/bin:$GUROBI_HOME/bin:$HOME/PyCity-RWTH-cluster/bin:$PATH"
 
### Job name
#BSUB -J OPTGA
 
### File / path where STDOUT & STDERR will be written
###    %J is the job ID, %I is the array ID
#BSUB -o OUTPUT.%J.txt
 
### Request the time you need for execution in minutes
### The format for the parameter is: [hour:]minute,
### that means for 80 minutes you could also use this: 1:20
#BSUB -W 119:50
### # W 119:50
 
### Request memory you need for your job in TOTAL in MB
#BSUB -M 254000
### # M 131072
### # M 65536
### # M 1024
### # M 4096
 
### Request the number of compute slots you want to use
#BSUB -n 32
### n 96
 
### Stack size in MB (per process)
#BSUB -S 512
 
### System choice
#BSUB -m smp-l-bull
#### m mpi-l-bull 
 
### Use esub for OpenMP/shared memeory jobs
#BSUB -a openmp
 
### Project id
#BSUB -P rwth0227
### P rwth0171

### Send email
#BSUB -N
#BSUB -u jschiefelbein@eonerc.rwth-aachen.de

### Activate source
source activate pycity

### Change to the work directory
cd pycity_resilience/ga/

### Execute your application
#python -m scoop opt_ga.py
python -m scoop -vv -n 32 opt_ga.py
#python opt_ga.py