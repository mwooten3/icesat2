#!/bin/bash


echo "Start: $(date)"

inDir=$1

for h5 in "$indir""/*.h5";
do
echo "$h5"
done

echo "Done: $(date)"
