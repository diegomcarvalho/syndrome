REGIONS=~/cluster/syndrome/log/processed.log

rm -f metaparam.dat
echo "ct, chi-square, chi-reduced, akaike, population, func_call" >> metaparam.csv
for i in `cat $REGIONS | sort`; 
do 
	lynx --dump ${i}-6.html | fgrep -f ~/cluster/syndrome/param.fgrep > /tmp/${i}.brt
	VAL_CHI=`fgrep chi-square /tmp/${i}.brt| head -1 |awk '{print $2}'`
	VAL_REDUCED=`fgrep reduced /tmp/${i}.brt| awk '{print $3}'`
	VAL_AKAIKE=`fgrep Akaike /tmp/${i}.brt | awk '{print $4}'`
	VAL_POP=`fgrep pop /tmp/${i}.brt | awk '{print $2}'`
	VAL_FUNC=`fgrep function /tmp/${i}.brt| head -1 |awk '{print $4}'`
	rm -f /tmp/${i}.brt
	echo "$i, $VAL_CHI, $VAL_REDUCED, $VAL_AKAIKE, $VAL_POP, $VAL_FUNC" >> metaparam.csv
done
