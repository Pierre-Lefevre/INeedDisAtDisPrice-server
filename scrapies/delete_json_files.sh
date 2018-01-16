#!/bin/bash

declare -a stores=("auchan" "boulanger" "cdiscount" "darty" "fnac" "ldlc" "materiel_net" "rue_du_commerce")

for i in "${stores[@]}"
do
    find data/$i/img/* -type f -not -name '.gitignore' -delete
    find data/$i/json/* -type f -not -name '.gitignore' -delete
done
