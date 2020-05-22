import os

def run_gnuplot_file(filename, datafile=None):
	if datafile is not None:
		if os.path.getsize(datafile) == 0:
			return
	os.system(f'gnuplot < {filename} > /tmp/gnuplot.$$.log 2>&1')
	return

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
