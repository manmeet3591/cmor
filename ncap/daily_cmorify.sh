#!/bin/bash

#export PATH="/moes/home/cmip/miniconda2/bin:$PATH"
#export PYTHONPATH=/moes/home/cmip/cmor/local/lib/python2.7/site-packages:$PYTHONPATH
#yyyy=$@
#cat << EOF > cmor_${yyyy}_$(( $yyyy + 10 )).sh
#export PATH=/iitm4/cccr/cmip6/Manmeet/anaconda3/envs/CMOR/bin/:$PATH
#source activate CMOR
for ((i=1850;i<2010;i=i+10))
   do 
      ./Aday_hist_2d.py ${i} $(($i+10))
   done

./Aday_hist_2d.py 2010 2015
#yyyy=$yyyy 
#./Amon_hist_2d.py ${yyyy}-01  $(( $yyyy + 10 ))-01 
#EOF
#bsub -q "cccr-res" -W 10:00 -J "cmor_${yyyy}_$(( $yyyy + 10 ))" -o "cmor.out" < cmor_${yyyy}_$(( $yyyy + 10 )).sh
#
##for yyyy in $@
##
##do
##
##echo $yyyy
##
##enddt=$(($yyyy+10))
##
##echo $enddt
##
##bsub -q "cccr" -o monthly_cmorify_$yyyy.out ./Amon_pictrl_2d.py $yyyy $enddt
##
##done
#source activate CMOR
#python Amon_hist_2d.py ${yyyy}-01 ${enddt}-01
#
