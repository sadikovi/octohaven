.PHONY: build clean start test docker-start docker-stop

# Current project directory
ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

# Command to run service, make sure that new parameters are in sync with sbin/start.sh
# !!! Note !!!
# Do not forget to change IP address in connection string on docker container one. If you are on
# OS X, then IP address is = "$(docker-machine ip $(docker-machine active))", if you are on Linux,
# then just use "localhost"
CMD:=$(ROOT_DIR)/bin/python setup.py start_octohaven \
	--host=localhost \
	--port=33900 \
	--spark-master=spark://sandbox:7077 \
	--spark-ui=http://localhost:8080 \
	--spark-submit=spark-submit \
	--jar-folder=test/ \
	--working-dir=work/ \
	--connection='jdbc:mysql://192.168.99.100:3306/octohaven?user=user&password=12345'

clean:
	# delete .pyc files from project folder
	find $(ROOT_DIR) -name "*.pyc" -type f -not -path "$(ROOT_DIR)/venv/*" | xargs rm -f
	# delete sass cache
	rm -rf "$(ROOT_DIR)/.sass-cache"
	# delete target directory
	rm -rf $(ROOT_DIR)/target
	# delete bower artifacts directory
	rm -rf $(ROOT_DIR)/bower_components
	# delete npm artifacts directory
	rm -rf $(ROOT_DIR)/node_modules
	# delete all javascript artefacts in static folder
	rm -f $(ROOT_DIR)/static/*.js
	# delete all css artefacts in static folder
	rm -f $(ROOT_DIR)/static/*.css
	# delete service logs
	rm -f $(ROOT_DIR)/octohaven-service.log*
	# delete work directory
	rm -rf $(ROOT_DIR)/work/job-*
	# clean up lib folder with dependencies
	find $(ROOT_DIR)/lib/* -not -name "__init__.py" | xargs rm -rf
	# delete .DS_Store files
	find $(ROOT_DIR) -name ".DS_Store" -type f | xargs rm -f
	# delete distribution files (directory and generated MANIFEST)
	rm -rf $(ROOT_DIR)/dist
	rm -f $(ROOT_DIR)/MANIFEST

build:
	# install python dependencies
	$(ROOT_DIR)/bin/pip install -r requirements.txt --upgrade --target $(ROOT_DIR)/lib/
	# install npm dependencies, e.g. bower
	npm install
	# install bower dependencies
	./node_modules/bower/bin/bower install --production
	# build static files, e.g. coffee and scss
	bin/make-static.sh

start:
	$(CMD)

test:
	$(CMD) --test

docker-start:
	# Start MySQL container, or launch new one. Note that settings should reflect ones defined in CMD
	# Script also checks for docker-machine on OSX
	. bin/docker.sh; docker_interface start default octohaven-test-mysql-container

docker-stop:
	. bin/docker.sh; docker_interface stop default octohaven-test-mysql-container
