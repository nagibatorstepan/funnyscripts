for f in supa*.json;
do
   echo $f
   awk 'NR == 2 || NR % 7 == 5' $f >> smallinfo.json
done
