# Bizzaro Francesco
# March 2020
#
# Shell script to automate the executions
# of the python script.

tp=$1
REP=100
mainfold="./motions"
mkdir -p "$mainfold/results"
for i in $(seq 0 $REP); do
  mkdir -p "$mainfold/pop_$i"
  echo "$nm [$tp $i]"
  echo "$motions $tp $i"
  python locomotion.py motions $tp $i
done
