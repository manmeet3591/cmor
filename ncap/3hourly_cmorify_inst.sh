#!/bin/bash

export PATH="/moes/home/cmip/miniconda2/bin:$PATH"
#export PYTHONPATH=/moes/home/cmip/cmor/local/lib/python2.7/site-packages:$PYTHONPATH


for yyyy in $@

do

echo $yyyy

enddt=$(($yyyy+5))

echo $enddt

bsub -q "cccr" -o 3hourly_cmorify_inst_$yyyy.out ./A3hourly_pictrl_inst.py $yyyy $enddt

done


