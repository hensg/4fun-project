.PHONY: setup-venv
setup-venv:
	test -f venv/bin/activate || virtualenv -p $(shell which python3) venv
	. venv/bin/activate; pip install -r requirements.txt
	@echo
	@echo
	@echo 'You must activate virtualenv in your terminal: "source venv/bin/activate"'

run-api:
	gunicorn --workers=4 --reload 'api.api:get_app()'

lint:
	venv/bin/python3.6 -m pylint api/

test:
	venv/bin/python3.6 -m pytest --cov=api/ api-tests/ -v
