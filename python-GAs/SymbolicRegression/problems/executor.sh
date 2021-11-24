nm=$1
tp=$2
REP=4
mainfold="./$nm"
mkdir -p $mainfold
mkdir -p "$mainfold/results"
for i in $(seq 0 $REP); do
  mkdir -p "$mainfold/pop_$i"
  echo "$nm [$tp $i]"
  python ../approxGP.py $nm $tp $i
done
