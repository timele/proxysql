#!/bin/bash

if [ ! -d /opt/proxysql ]; then
	mkdir -p /opt/proxysql
	cp -R /tmp/proxysql/* /opt/proxysql
	cd /opt/proxysql
	make clean && make > /tmp/proxysql_compile.log
fi

cd /opt/proxysql/src
make clean && make > /tmp/proxysql_compile.log
# TODO(andrei): re-enable the commented line when figuring out interactive mode
# gdbserver 0.0.0.0:2345 ./proxysql --initial -f -c /etc/proxysql.cnf
./proxysql --initial -f -c /etc/proxysql.cnf