.PHONY: setup-venv
setup-venv:
	test -f venv/bin/activate || virtualenv -p $(shell which python3) venv
	. venv/bin/activate; pip install -r requirements.txt
	@echo
	@echo
	@echo 'You must activate virtualenv in your terminal: "source venv/bin/activate"'
