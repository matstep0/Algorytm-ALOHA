#! /bin/bash
#jako pierwszy argument liczbe testow
#jako drugi argumenty do simulate
comm=$2
for((i=0;i<$1;i++));do
out=$(($out+$(./simulate.py $2 | grep -Po "'success': \d*" | cut -c12-)))
done
echo $(echo $out/$1 | bc -l)  
