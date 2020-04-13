# Bizzaro Francesco
# March 2020
#
# Shell script to run the python script
# on all the problems on a folder.

tp=$1
hd=$2
cd "./problems/$2/"
for f in ./*.json; do
    ffr=${f##*/}
    nm=${ffr%%.json}
    ../executor.sh $nm $tp
done
cd ../..
