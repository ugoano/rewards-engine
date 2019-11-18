VENV ?= ./.virtualenv

test:
	$(VENV)/bin/python3 -m unittest

install:
	python3 -m venv $(VENV) && \
	$(VENV)/bin/pip install -r requirements.txt

rabbit:
	docker-compose up rabbit

sales:
	$(VENV)/bin/python3 src/sales_service.py

rewards:
	$(VENV)/bin/python3 src/rewards_service.py
