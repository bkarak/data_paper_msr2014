pdf:
	#cd data && make
	pdflatex evol.tex
	bibtex evol
	pdflatex evol.tex
	pdflatex evol.tex

clean:
	-rm -f *.aux
	-rm -f *.bbl *.ent *.blg *.log *.out *.dvi *~ *.spl
	-rm -f evol.pdf

count-words:
	@echo "Counting Words"
	-wc -w *.tex *.bib | tee new-wc.out | diff old-wc.out -
	-mv new-wc.out old-wc.out
