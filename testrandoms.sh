# $1 is iterations, $2 is file, $3 is number
i="0"
echo "digraph G{" > $2
while [ $i -lt $1 ]
do
echo "\"$(($(od -N 4 -t uL -An /dev/urandom | tr -d " ") % $3))\" -> \"$(($(od -N 4 -t uL -An /dev/urandom | tr -d " ") % $3))\";" >> $2
i=$[$i+1]
done
echo "}" >> $2
