run: test.mdl lex.py main.py matrix.py mdl.py display.py draw.py vector.py yacc.py script.py parser.py
	rm -f animation/*
	python2 main.py test.mdl
	animate -delay 10 animation/test*
clean:
	rm *pyc *out parsetab.py
clear:
	rm *pyc *out parsetab.py *ppm
