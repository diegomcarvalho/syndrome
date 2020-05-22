all: opt.cpython-37m-darwin.so alg

opt.cpython-37m-darwin.so: opt.pyx
	cythonize -3 -a -i opt.pyx

alg:
	cd algo; make

clean:
	rm -fr opt.cpython-37m-darwin.so opt.c opt.html __pycache__
	cd algo; make clean