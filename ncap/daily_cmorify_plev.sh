#!/bin/bash

export PATH="/moes/home/cmip/miniconda2/bin:$PATH"

for yyyy in $@

do

echo $yyyy

enddt=$(($yyyy+10))

echo $enddt

bsub -q "cccr" -o daily_cmorify_plev_$yyyy.out ./Aday_pictrl_3d.py $yyyy $enddt

done


