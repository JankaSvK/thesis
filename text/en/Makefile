export TEXINPUTS=../tex//:

all: thesis.pdf

options.txt: ../../program/Main.py
	python3 ../../program/Main.py -h > options.txt

# LaTeX must be run multiple times to get references right
thesis.pdf: thesis.tex $(wildcard *.tex) bibliography.bib thesis.xmpdata options.txt distances.txt experiments/hsv.txt experiments/trackers.txt
	pdflatex $<
	bibtex thesis
	pdflatex $<
	pdflatex $<

clean:
	rm -f *.log *.dvi *.aux *.toc *.lof *.lot *.out *.bbl *.blg *.xmpi
	rm -f thesis.pdf
