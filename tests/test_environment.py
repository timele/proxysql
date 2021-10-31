import pytest
import os
from time import sleep
from tests.conftest import check_connection, connect_disconnect_mysql
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

    """ Test proxysql::mysql_servers has 3 columns: """

    # assert check_proxysql_table_mysql_servers(proxysql_service, with_ssl=False)
    """ Test proxysql::runtime_mysql_servers has 3 columns: """

    # assert check_proxysql_table_runtime_mysql_servers(proxysql_service, with_ssl=False)
    """ Test mysql connection proxysql -> mysql_0 is using TLS """
    # VERIFY_CLIENT/SERVER on both ends
    """ Test mysql connection proxysql -> mysql_1 is using TLS """

    """ Test mysql connection proxysql -> mysql_2 is using TLS """

