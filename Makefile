.PHONY: conda_env install clean

CONDA ?= conda
INSTDIR ?= .

conda_env:
	mkdir -p $(INSTDIR)
	$(CONDA) env create --quiet --file conda_env.yml --prefix $(INSTDIR)/conda_env

install: conda_env
	$(INSTDIR)/conda_env/bin/pip install -r requirements.txt

clean:
	rm -rf $(INSTDIR)/conda_env
