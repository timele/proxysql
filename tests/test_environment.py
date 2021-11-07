import pytest
import os
from time import sleep
from tests.conftest import (
    check_connection, connect_disconnect_mysql, check_proxysql_tables, 
    get_proxysql_mysql_servers_value, get_proxysql_runtime_mysql_servers_value
)
import logging
from pathlib import Path, WindowsPath

LOGGER = logging.getLogger(__name__)


def test_fr_3331(proxysql_service, mysql_0_service, mysql_1_service, mysql_2_service):
    LOGGER.info("\t- Winding up services ...")
    """ Test that docker nodes are UP """
    assert proxysql_service.db_settings.hostname == os.environ.get("PROXYSQL_HOST", "172.34.1.1")
    assert proxysql_service.db_settings.port == int(os.environ.get("PROXYSQL_PORT", 6033))
    assert proxysql_service.db_settings.manage_port == int(os.environ.get("PROXYSQL_MANAGE_PORT", 6032))
    
    assert Path(proxysql_service.ssl_settings.ca_file).is_file()
    assert Path(proxysql_service.ssl_settings.cert_file).is_file()
    assert Path(proxysql_service.ssl_settings.key_file).is_file()

    assert mysql_0_service.db_settings.hostname == os.environ.get("MYSQL_0_HOST", "172.34.1.2")
    assert mysql_0_service.db_settings.port == int(os.environ.get("MYSQL_0_PORT", 3306))

    assert mysql_1_service.db_settings.hostname == os.environ.get("MYSQL_1_HOST", "172.34.1.3")
    assert mysql_1_service.db_settings.port == int(os.environ.get("MYSQL_1_PORT", 3307))

    assert mysql_2_service.db_settings.hostname == os.environ.get("MYSQL_2_HOST", "172.34.1.4")
    assert mysql_2_service.db_settings.port == int(os.environ.get("MYSQL_2_PORT", 3308))

    LOGGER.info("\t- Docker services are accessible by TCP.")

    """ Test TCP connections to nodes """
    sleep(30) #### need to wait for mysql servers to come online
    assert check_connection(mysql_0_service.db_settings.hostname, mysql_0_service.db_settings.port)
    assert check_connection(mysql_1_service.db_settings.hostname, mysql_1_service.db_settings.port)
    assert check_connection(mysql_2_service.db_settings.hostname, mysql_2_service.db_settings.port)
    assert check_connection(proxysql_service.db_settings.hostname, proxysql_service.db_settings.port)
    LOGGER.info("\t- Services are accessible by TCP.")

    """ Test that nodes are reachable """
    sleep(30) #### need to wait for mysql servers to come online
    assert connect_disconnect_mysql(mysql_0_service)
    assert connect_disconnect_mysql(mysql_1_service)
    assert connect_disconnect_mysql(mysql_2_service)
    assert connect_disconnect_mysql(proxysql_service)

    LOGGER.info("\t- Nodes are acessible with MySQL client.")

    """ Check proxysql::mysql_servers and proxysql::runtime_mysql_servers has 3 columns: """
    assert check_proxysql_tables(proxysql_service)

    """ Check settings usage - mysql_servers """
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.2", "ssl_ca") == "/etc/certs/ca.pem"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.2", "ssl_cert") == "/etc/certs/client-cert.pem"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.2", "ssl_key") == "/etc/certs/client-key.pem"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.2", "hostgroup_id") == "0"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.2", "use_ssl") == "1"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.2", "max_connections") == "5"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.2", "status") == "ONLINE"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.2", "weight") == "1"

    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.3", "ssl_ca") == "/etc/certs/ca.pem"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.3", "ssl_cert") == "/etc/certs/client-cert.pem"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.3", "ssl_key") == "/etc/certs/client-key.pem"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.3", "hostgroup_id") == "0"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.3", "use_ssl") == "1"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.3", "max_connections") == "10"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.3", "status") == "ONLINE"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.3", "weight") == "2"

    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.4", "ssl_ca") == "/etc/certs/ca.pem"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.4", "ssl_cert") == "/etc/certs/client-cert.pem"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.4", "ssl_key") == "/etc/certs/client-key.pem"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.4", "hostgroup_id") == "0"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.4", "status") == "ONLINE"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.4", "use_ssl") == "1"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.4", "max_connections") == "15"
    assert get_proxysql_mysql_servers_value(proxysql_service, "172.34.1.4", "weight") == "3"

    """ Check settings usage - runtime_servers """
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.2", "ssl_ca") == "/etc/certs/ca.pem"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.2", "ssl_cert") == "/etc/certs/client-cert.pem"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.2", "ssl_key") == "/etc/certs/client-key.pem"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.2", "hostgroup_id") == "0"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.2", "use_ssl") == "1"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.2", "max_connections") == "5"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.2", "status") == "ONLINE"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.2", "weight") == "0"

    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.3", "ssl_ca") == "/etc/certs/ca.pem"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.3", "ssl_cert") == "/etc/certs/client-cert.pem"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.3", "ssl_key") == "/etc/certs/client-key.pem"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.3", "hostgroup_id") == "0"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.3", "use_ssl") == "1"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.3", "max_connections") == "10"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.3", "status") == "ONLINE"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.3", "weight") == "0"

    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.4", "ssl_ca") == "/etc/certs/ca.pem"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.4", "ssl_cert") == "/etc/certs/client-cert.pem"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.4", "ssl_key") == "/etc/certs/client-key.pem"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.4", "hostgroup_id") == "0"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.4", "use_ssl") == "1"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.4", "max_connections") == "15"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.4", "status") == "ONLINE"
    assert get_proxysql_runtime_mysql_servers_value(proxysql_service, "172.34.1.4", "weight") == "0"

    """ Check proxysql -> mysql connection is using SSL """
    # assert proxysql_mysql_uses_ssl(mysql_0_service, "172.34.1.1")
    # assert proxysql_mysql_uses_ssl(mysql_1_service, "172.34.1.1")
    # assert proxysql_mysql_uses_ssl(mysql_1_service, "172.34.1.1")

if __name__ == "__main__":
    pytest.main()
