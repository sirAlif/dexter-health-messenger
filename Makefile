run:
	docker-compose up --build

stop:
	docker-compose down

run-client:
	PYTHONPATH=. python client/terminal_client.py