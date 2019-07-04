#!/bin/bash

export PATH="/moes/home/cmip/miniconda2/bin:$PATH"

for yyyy in $@

do

echo $yyyy

enddt=$(($yyyy+1))

echo $enddt

bsub -q "cccr" -o 6hourly_cmorify_modellev_$yyyy.out ./A6hourly_inst_pictrl_modellev.py $yyyy $enddt

done


