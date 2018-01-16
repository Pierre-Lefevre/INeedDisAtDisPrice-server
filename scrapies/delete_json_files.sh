#!/bin/bash

declare -a stores=("auchan" "boulanger" "cdiscount" "darty" "fnac" "ldlc" "materiel_net" "rue_du_commerce")

for i in "${stores[@]}"
do
    rm -f data/$i/img/*
    rm -f data/$i/json/*
done
