.PHONY: build clean start test docker-start docker-stop

CMD=bin/python setup.py start_octohaven --host=localhost --port=33900 \
	--spark-master=spark://sandbox:7077 \
	--spark-ui=http://localhost:8080 \
	--jar-folder test/ \
	--connection='jdbc:mysql://192.168.99.100:3306/octohaven?user=user&password=12345'

clean:
	bin/cleanup.sh

build: clean
	bin/static.sh
	npm install
	./node_modules/bower/bin/bower install

start:
	$(CMD)

test:
	$(CMD) --test

docker-start:
	bin/docker.sh start default octohaven-mysql-container

docker-stop:
	bin/docker.sh stop default octohaven-mysql-container
