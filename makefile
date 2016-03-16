.PHONY: build clean start test docker

CMD=bin/python setup.py start_octohaven --host=localhost --port=33900 \
	--spark-master=spark://sandbox:7077 \
	--spark-ui=http://localhost:8080 \
	--jar-folder test/ \
	--connection='jdbc:mysql://192.168.99.100:3306/octohaven?user=user&password=12345'

clean:
	bin/cleanup.sh

build:
	bin/static.sh

start:
	$(CMD)

test:
	$(CMD) --test

docker:
	bin/docker.sh default octohaven-mysql-container
