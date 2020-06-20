import os
import itertools

def run_gnuplot_file(filename, datafile=None):
	if datafile is not None:
		if os.path.getsize(datafile) == 0:
			return
	os.system(f'gnuplot < {filename} > /tmp/gnuplot.$$.log 2>&1')
	return

def dump_xy_dat(filename, x, y):
	with open(filename, 'w') as f:
		for i, j in itertools.zip_longest(x, y, fillvalue='nan'):
			f.write(f'{i}, {j}\n')
	return

def dump_xyz_dat(filename, x, y, z):
	with open(filename, 'w') as f:
		for i, j, k in itertools.zip_longest(x, y, z, fillvalue='nan'):
			f.write(f'{i}, {j}, {k}\n')

def dump_8_dat(filename, x1, x2, x3, x4, x5, x6, x7, x8):
	with open(filename, 'w') as f:
		for i, w in enumerate(itertools.zip_longest(x1, x2, x3, x4, x5, x6, x7, x8, fillvalue='nan')):
			f.write(f'{i}, {w[0]}, {w[1]}, {w[2]}, {w[3]}, {w[4]}, {w[5]}, {w[6]}, {w[7]}\n')

def dump_svg_ph(filename, svgfile, title, xlabel, ylabel, txt1):
	with open(filename, 'w') as f:
		f.write('set terminal svg size 600,600 font "Roboto,13" enhanced rounded\n')
		f.write(f"set output '{svgfile}'\n")
		f.write('set key  off\n')
		f.write(f"set title'{title}'\n")
		f.write(f"set xlabel '{xlabel}'\n")
		f.write(f"set ylabel '{ylabel}'\n")
		f.write(f"set label '{txt1}' at screen 0.2,0.7 font 'Roboto Italic, 20'\n")
		f.write('set label "2020 © R.Barbastefano, D.Carvalho, M.C.Lippi, D.Pastore" ')
		f.write('at screen 0.99,0.1 rotate by 90\n')
		f.write(f"plot -5 w p pt 0, 5 w p pt 0\n")
	run_gnuplot_file(filename)
	return


def dump_svg(filename, svgfile, title, xlabel, ylabel, datafile, col1,  label1,  opt=None, txt1=None, txt2=None, point=True, logx=False, logy=False):
	with open(filename, 'w') as f:
		f.write('set terminal svg size 600,600 font "Roboto,13" enhanced rounded\n')
		f.write(f"set output '{svgfile}'\n")
		if opt != None:
			f.write(f'set {opt}\n')
		if logx and logy:
			f.write(f'set logscale xy\n')
		elif logx:
			f.write(f'set logscale x\n')
		elif logy:
			f.write(f'set logscale y\n')
		f.write('set key  top left box\nset pointsize 0.6\n')
		f.write(f"set title'{title}'\n")
		f.write(f"set xlabel '{xlabel}'\n")
		f.write(f"set ylabel '{ylabel}'\n")
		if txt1 != None:
			f.write(f"set label '{txt1}' at screen 0.2,0.7 font 'Roboto Italic, 13'\n")
		if txt2 != None:
			f.write(f"set label '{txt2}' at screen 0.2,0.75 font 'Roboto Italic, 13'\n")
		f.write('set label "2020 © R.Barbastefano, D.Carvalho, M.C.Lippi, D.Pastore" ')
		f.write('at screen 0.99,0.1 rotate by 90\n')
		cnf = "p pt 6" if point else "linesp pt 7"
		f.write(f"plot '{datafile}' using 1:(${col1}) w {cnf} title '{label1}'\n")
	run_gnuplot_file(filename,datafile)
	return


def dump_svg2D(filename, svgfile, title, xlabel, ylabel, datafile, col1, col2, label1, label2, opt=None, txt1=None, txt2=None):
	with open(filename, 'w') as f:
		f.write('set terminal svg size 600,600 font "Roboto,13" enhanced rounded\n')
		f.write(f"set output '{svgfile}'\n")
		if opt != None:
			f.write(f'set {opt}\n')
		f.write('set key  top left box\nset pointsize 0.6\n')
		f.write(f"set title'{title}'\n")
		f.write(f"set xlabel '{xlabel}'\n")
		f.write(f"set ylabel '{ylabel}'\n")
		if txt1 != None:
			f.write(
				f"set label '{txt1}' at screen 0.2,0.7 font 'Roboto Italic, 13'\n")
		if txt2 != None:
			f.write(
				f"set label '{txt2}' at screen 0.2,0.75 font 'Roboto Italic, 13'\n")
		f.write('set label "2020 © R.Barbastefano, D.Carvalho, M.C.Lippi, D.Pastore" ')
		f.write('at screen 0.99,0.1 rotate by 90\n')
		f.write(
			f"plot '{datafile}' using 1:(${col1}) w p pt 6 title '{label1}', ")
		f.write(f"'' using 1:(${col2}) w linesp pt 7 title '{label2}'")
	run_gnuplot_file(filename,datafile)
	return

import tempfile

def dump_svg8D(svgfile1, svgfile2, datafile,
				title, xlabel, ylabel,
				label, opt=None, txt1=None, txt2=None, pop=None):

	filename = 'f1.gp'
	# col: 2 3 4 5 6 7 8 9
	# lab: 0 1 2 3 4 5 6 7
	# day, S,Q,E,A,I,D,R,M
	# 1st: S, Q, R
	# 2nd: E,A,I,D,M
	with open(filename, 'w') as f:
		f.write('set terminal svg size 800,300 font "Roboto,13" enhanced rounded\n')
		f.write(f"set output '{svgfile1}'\n")
		if opt != None:
			f.write(f'set {opt}\n')
		f.write('set key  top left box\nset pointsize 0.6\n')
		f.write(f"set title'{title}'\n")
		f.write(f"set xlabel '{xlabel}'\n")
		f.write(f"set ylabel '{ylabel}'\n")
		if pop is not None:
			pop = int(pop)
			f.write(f'set ytics nomirror')
			f.write(f'set y2tics 0, {pop//5}')
		if txt1 is not None:
			f.write(
				f"set label '{txt1}' at screen 0.2,0.7 font 'Roboto Italic, 13'\n")
		if txt2 is not None:
			f.write(
				f"set label '{txt2}' at screen 0.2,0.75 font 'Roboto Italic, 13'\n")
		f.write('set label "2020 © R.Barbastefano, D.Carvalho, M.C.Lippi, D.Pastore" ')
		f.write('at screen 0.99,0.1 rotate by 90\n')
		f.write(f"plot '{datafile}' using 1:2 w lines title '{label[0]}', ")
		f.write(f"'' using 1:3 w lines title '{label[1]}', ")
		f.write(f"'' using 1:8 w lines title '{label[6]}'\n")
	os.system(f'gnuplot < {filename} > /tmp/gnuplot.$$.log 2>&1')

	filename = 'f2.gp'
	# col: 2 3 4 5 6 7 8 9
	# lab: 0 1 2 3 4 5 6 7
	# day, S,Q,E,A,I,D,R,M
	# 1st: S, Q, R
	# 2nd: E,A,I,D,M
	with open(filename, 'w') as f:
		f.write('set terminal svg size 800,300 font "Roboto,13" enhanced rounded\n')
		f.write(f"set output '{svgfile2}'\n")
		if opt != None:
			f.write(f'set {opt}\n')
		f.write('set key  top left box\nset pointsize 0.6\n')
		f.write(f"set title'{title}'\n")
		f.write(f"set xlabel '{xlabel}'\n")
		f.write(f"set ylabel '{ylabel}'\n")
		if txt1 != None:
			f.write(
				f"set label '{txt1}' at screen 0.2,0.7 font 'Roboto Italic, 13'\n")
		if txt2 != None:
			f.write(
				f"set label '{txt2}' at screen 0.2,0.75 font 'Roboto Italic, 13'\n")
		f.write('set label "2020 © R.Barbastefano, D.Carvalho, M.C.Lippi, D.Pastore" ')
		f.write('at screen 0.99,0.1 rotate by 90\n')
		f.write(f"plot '{datafile}' using 1:4 w lines title '{label[2]}', ")
		f.write(f"'' using 1:5 w lines title '{label[3]}', ")
		f.write(f"'' using 1:6 w lines title '{label[4]}', ")
		f.write(f"'' using 1:7 w lines title '{label[5]}', ")
		f.write(f"'' using 1:9 w lines title '{label[7]}'\n")
	os.system(f'gnuplot < {filename} > /tmp/gnuplot.$$.log 2>&1')

	return

from IPython.display import SVG, display
def show_svg(file):
    display(SVG(file))