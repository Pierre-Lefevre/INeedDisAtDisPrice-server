#!/bin/bash

mongo iNeedDisAtDisPrice --eval "db.dropDatabase()"

declare -a stores=("auchan" "boulanger" "cdiscount" "darty" "fnac" "ldlc" "materiel_net" "rue_du_commerce")

shopt -s nullglob
for i in "${stores[@]}"
do
	cd data/$i/json
	for filename in *.json; do
	    echo $filename
	    mongoimport --db iNeedDisAtDisPrice --collection products --file $filename
	done
	cd ../../..
done
