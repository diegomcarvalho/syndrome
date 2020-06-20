set terminal svg size 800,300 font "Roboto,13" enhanced rounded
set output 'svg/Venezuela-17.svg'
set key  top left box
set pointsize 0.6
set title'SIMDRQME Compartment Model for Venezuela on 2020-06-17'
set xlabel 'days'
set ylabel 'perc. of pop.'
set label "2020 © R.Barbastefano, D.Carvalho, M.C.Lippi, D.Pastore" at screen 0.99,0.1 rotate by 90
plot 'gpdata/dat/Venezuela-16.dat' using 1:4 w lines title 'E', '' using 1:5 w lines title 'A', '' using 1:6 w lines title 'I', '' using 1:7 w lines title 'D', '' using 1:9 w lines title 'M'
