YESTERDAY=$(date --date=yesterday +%Y%m%d)
SITEROOT=/storage/covid/carvalho
BACKUP=$(SITEROOT)/$(YESTERDAY)

start:
	bash start.sh

stop:
	bash stop.sh

run:
	python3 syndrome.py

$(BACKUP):
	echo Creating $(BACKUP)
	mkdir -p $(BACKUP)
	mv $(SITEROOT)/index.html $(SITEROOT)/edo.html $(SITEROOT)/socnet.html $(SITEROOT)/web $(SITEROOT)/$(YESTERDAY)

build: $(BACKUP) 
	cp -r web $(SITEROOT)
	python3 createindex.py > $(SITEROOT)/index.html
	python3 createindex-id.py 6 > $(SITEROOT)/edo.html
	python3 createindex-id.py 8 > $(SITEROOT)/socnet.html
	echo Done

clean:
	rm -f gpdata/*.gp gpdata/dat/*.dat log/*.dat report/*.html svg/*.svg 
	rm -f web/*.html web/svg/*.svg web/report/*.html
	rm -f timeline.json __pycache__ 