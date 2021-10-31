import os
from _pytest import config
import pytest
import socket
import mysql.connector
from mysql.connector import errorcode
from mysql.connector.constants import ClientFlag
from dotenv import load_dotenv
import logging
from pathlib import Path


# pytest_plugins = ["docker_compose"]

LOGGER = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent

TEST_DB_NAME = os.environ.get("DB_NAME", "test_database")
TEST_DB_USERNAME = os.environ.get("DB_USERNAME", "testuser")
TEST_DB_PASSWORD = os.environ.get("DB_PASSWORD", "testuser")

class SSL_Settings:
    def __init__(self, ca_file, cert_file, key_file):
        self.ca_file = ca_file
        self.cert_file = cert_file
        self.key_file = key_file

class DB_Setttings:
    def __init__(self, hostname, port, manage_port, username, password, database):
        self.hostname = hostname
        self.port = port
        self.manage_port = manage_port
        self.database = database
        self.username = username
        self.password = password

class Node_Service:
    def __init__(self, db_settings, ssl_settings):
        self.db_settings = db_settings
        self.ssl_settings = ssl_settings

    def append_ssl_settings(self, config):
        """ append ssl settings to config object """
        config["client_flags"] = [ClientFlag.SSL]
        config["tls_versions"] = ["TLSv1.3"]
        config["ssl_ca"] = self.ssl_settings.ca_file
        config["ssl_cert"] = self.ssl_settings.cert_file
        config["ssl_key"] = self.ssl_settings.key_file
        config["ssl_disabled"] = False
        config["ssl_verify_cert"] = True
        # ssl = {
        #     "client_flags": [ClientFlag.SSL],
        #     "tls_versions": ["TLSv1.3"],
        #     "ssl_ca": self.ssl_settings.ca_file,
        #     "ssl_cert": self.ssl_settings.cert_file,
        #     "ssl_key": self.ssl_settings.key_file
        # }
        # config["ssl"] = ssl


    def service_settings(self):
        """ construct database connection settings config """
        config = {
            "host": self.db_settings.hostname,
            "port": self.db_settings.port,
            "user": self.db_settings.username,
            "password": self.db_settings.password,
            "database": self.db_settings.database,
            "raise_on_warnings": True,
            "connection_timeout": 600 
        }
        if self.ssl_settings:
            self.append_ssl_settings(config)
        return config

    def management_settings(self):
        """ construct management connection settings config """
        config = {
            "host": self.db_settings.hostname,
            "port": self.db_settings.manage_port,
            "username": "root",
            "password": "root",
            "database": "",
            "raise_on_warnings": True,
            "connection_timeout": 600 
        }
        if self.ssl_settings:
            self.append_ssl_settings(config)
        return config


def check_connection(connection_ip: str, connection_port: int) -> bool:
    """ Check TCP connection availability """
    LOGGER.debug(f"-> check_connection()::[addr: {connection_ip}, port: {connection_port}]")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((connection_ip, connection_port))
        s.shutdown(2)
        s.close()
        LOGGER.debug(f"\t Success TCP connect: {connection_ip}:{connection_port}")
        return True
    except Exception as e:
        LOGGER.debug(f"\t Failed TCP connect: {connection_ip}:{connection_port}")
        pytest.fail(f"Unable to connect to IP {connection_ip}.\n {e}")
        return False

@pytest.fixture(scope="session", autouse=True)
def load_env():
    """ load environment settings """
    load_dotenv()

@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    """ Ensure correct docker-compose.yml is used """
    return os.path.join(str(pytestconfig.rootdir), ".", "docker-compose.yml")


def wait_service_till_online(docker_ip, docker_services, service_name, svc_host, svc_port) -> str:
    """ Connect-disconnect to docker service by name """
    LOGGER.debug(f"-> wait_service_till_online()::[name: {service_name}, addr: {svc_host}, port: {svc_port}]")
    port = docker_services.port_for(service_name.lower(), svc_port)
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: check_connection(docker_ip, port)
    )
    node_urn = f"{svc_host}:{port}"
    return node_urn

def get_db_settings(service_name):
    LOGGER.debug("-> get_db_settings()")
    """ Fetch database connection settings """
    svc_host = os.environ.get(f"{service_name}_HOST")
    svc_port = int(os.environ.get(f"{service_name}_PORT"))
    svc_manage_port = int(os.environ.get(f"{service_name}_MANAGE_PORT", 0))
    svc_database = os.environ.get("DB_NAME", "test_database")
    svc_username = os.environ.get("DB_PASSWORD", "testuser")
    svc_password = os.environ.get("DB_USERNAME", "testuser")
    db_settings = DB_Setttings(svc_host, svc_port, svc_manage_port, svc_username, svc_password, svc_database)
    return db_settings

def get_absolute_path(arg_path):
    return str(Path(arg_path).resolve())

def get_ssl_settings(service_name):
    """ Fetch database ssl connection settings """
    LOGGER.debug(f"-> get_ssl_settings()::[name: {service_name}]")
    ssl_ca_file = get_absolute_path(os.environ.get(f"{service_name}_SSL_CA_FILE"))
    ssl_cert_file = get_absolute_path(os.environ.get(f"{service_name}_SSL_CRT_FILE"))
    ssl_key_file = get_absolute_path(os.environ.get(f"{service_name}_SSL_KEY_FILE"))
    ssl_settings = SSL_Settings(ssl_ca_file, ssl_cert_file, ssl_key_file)
    return ssl_settings

def configure_service(docker_ip, docker_services, service_name):
    """ Configures the services in accordance to name from env """
    LOGGER.debug(f"-> configure_service()::[name: {service_name}]")
    db_settings = get_db_settings(service_name)
    ssl_settings = get_ssl_settings(service_name)
    node_service = Node_Service(db_settings, ssl_settings)
    wait_service_till_online(docker_ip, docker_services, service_name, db_settings.hostname, db_settings.port)
    return node_service

@pytest.fixture(scope="session")
def proxysql_service(docker_ip, docker_services):
    """ Ensure ProxySQL is up and running """
    return configure_service(docker_ip, docker_services, service_name="PROXYSQL")

@pytest.fixture(scope="session")
def mysql_0_service(docker_ip, docker_services):
    """ Ensure MySQL host group node 0 is up and running """
    return configure_service(docker_ip, docker_services, service_name="MYSQL_0")

@pytest.fixture(scope="session")
def mysql_1_service(docker_ip, docker_services):
    """ Ensure MySQL host group node 1 is up and running """
    return configure_service(docker_ip, docker_services, service_name="MYSQL_1")

@pytest.fixture(scope="session")
def mysql_2_service(docker_ip, docker_services):
    """ Ensure MySQL host group node 2 is up and running """
    return configure_service(docker_ip, docker_services, service_name="MYSQL_2")

def mysql_connect(settings):
    """ Provide a connection to a mysql host """
    LOGGER.debug(f"-> mysql_connect()::[settings: {settings}]")
    try:
        cnx = mysql.connector.connect(**settings)
        return cnx
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            pytest.fail("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            pytest.fail("Database does not exist")
        else:
            pytest.fail(str(err))
        
def connect_disconnect_mysql(service: Node_Service):
    """ Swiftly connect to and disconnect from a mysql host """
    LOGGER.debug("-> connect_disconnect_mysql")
    cnx = mysql_connect(service.service_settings())
    if cnx:
        cnx.close()
        return True
    else:
        return False

def get_mysql_management_connection(service: Node_Service, with_ssl: bool):
    """ Connect to mysql server and return a connection """
    return mysql_connect(service.management_settings())

def get_mysql_service_connection(service: Node_Service, with_ssl: bool):
    """ Connect to mysql server and return a connection """
    return mysql_connect(service.service_settings())
