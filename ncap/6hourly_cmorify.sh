#!/bin/bash


export PATH="/moes/home/cmip/miniconda2/bin:$PATH"
#export PYTHONPATH=/moes/home/cmip/cmor/local/lib/python2.7/site-packages:$PYTHONPATH


for yyyy in $@

do

echo $yyyy

enddt=$(($yyyy+5))

echo $enddt

bsub -q "cccr" -o 6hourly_cmorify_mean_$yyyy.out ./A6hourly_pictrl_4lev.py $yyyy $enddt

done


