# We're using Ubuntu 14:04 because ProxySQL compilation needs one of the latest
# g++ compilers. Also, it's a long term release.
FROM ubuntu:20.04
ENV TZ=Asia/Bishkek
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update && apt-get install -y\
	automake\
	cmake\
	make\
	g++\
	gcc\
	bzip2\ 
	libgnutls28-dev\
	patch\
	git\
	libmysqlclient-dev\
	libssl-dev\
	libtool

# RUN cd /opt; git clone https://github.com/akopytov/sysbench.git
# RUN cd /opt/sysbench; ./autogen.sh; ./configure --bindir=/usr/bin; make; make install

# RUN mkdir /opt/proxysql
# RUN chmod 755 /opt/proxysql
# COPY ./proxysql /opt/
RUN ldconfig
ARG PROXYSQL_CONF_FILE
ADD ${PROXYSQL_CONF_FILE} /etc/proxysql.cnf
RUN mkdir -p /var/lib/proxysql
ADD ./proxysql/compile_and_start_proxysql.sh /tmp/
RUN chmod +x /tmp/compile_and_start_proxysql.sh

CMD ["/tmp/compile_and_start_proxysql.sh"]
