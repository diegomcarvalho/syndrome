set terminal svg size 800,300 font "Roboto,13" enhanced rounded
set output 'svg/Brazil-16.svg'
set key  top left box
set pointsize 0.6
set title'SIMDRQME Compartment Model for Brazil on 2020-06-20'
set xlabel 'days'
set ylabel 'perc. of pop.'
set label "2020 © R.Barbastefano, D.Carvalho, M.C.Lippi, D.Pastore" at screen 0.99,0.1 rotate by 90
plot 'gpdata/dat/Brazil-16.dat' using 1:2 w lines title 'S', '' using 1:3 w lines title 'Q', '' using 1:8 w lines title 'R'
