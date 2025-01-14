/**
 * @file reg_test_3493-USE_with_comment-t.cpp
 * @brief This test verifies that a 'USE' statement is properly tracked by
 *   ProxySQL, even when executed with a leading comment.
 * @details For being sure that the feature is properly supported the
 *   test performs the following actions:
 *
 *   1. Open a MYSQL connection to ProxySQL.
 *   2. Drops and creates a new database called 'reg_test_3493_use_comment'.
 *   3. Checks the currently selected database in **a new backend database
 *      connection** by means of the connection annotation
 *      "create_new_connection=1". This way it's ensured that ProxySQL is
 *      properly keeping track of the database selected in the issued 'USE'
 *      statement.
 */

#include <cstring>
#include <vector>
#include <utility>
#include <string>
#include <stdio.h>

#include <mysql.h>

#include "tap.h"
#include "command_line.h"
#include "utils.h"
#include "json.hpp"

using nlohmann::json;

void parse_result_json_column(MYSQL_RES *result, json& j) {
	if(!result) return;
	MYSQL_ROW row;

	while ((row = mysql_fetch_row(result))) {
		j = json::parse(row[0]);
	}
}

std::vector<std::pair<std::string,std::string>> db_query;

int main(int argc, char** argv) {
	CommandLine cl;

	if (cl.getEnv()) {
		diag("Failed to get the required environmental variables.");
		return -1;
	}

	MYSQL* proxysql_mysql = mysql_init(NULL);

	db_query.push_back(std::make_pair("reg_test_3493_use_comment", "/* placeholder_comment */ USE reg_test_3493_use_comment"));
	db_query.push_back(std::make_pair("`reg_test_3493_use_comment-a1`", "USE /* placeholder_comment */ `reg_test_3493_use_comment-a1`"));
	db_query.push_back(std::make_pair("reg_test_3493_use_comment_1", "  USE /* placeholder_comment */   `reg_test_3493_use_comment_1`"));
	db_query.push_back(std::make_pair("reg_test_3493_use_comment_2", "USE/* placeholder_comment */ `reg_test_3493_use_comment_2`"));
	db_query.push_back(std::make_pair("reg_test_3493_use_comment_3", "USE /* placeholder_comment */`reg_test_3493_use_comment_3`"));
	db_query.push_back(std::make_pair("reg_test_3493_use_comment_4", "  USE /* placeholder_comment */   reg_test_3493_use_comment_4"));
	db_query.push_back(std::make_pair("reg_test_3493_use_comment_5", "USE/* placeholder_comment */ reg_test_3493_use_comment_5"));
	db_query.push_back(std::make_pair("reg_test_3493_use_comment_6", "USE /* placeholder_comment */reg_test_3493_use_comment_6"));
	db_query.push_back(std::make_pair("`reg_test_3493_use_comment-1`", "  USE /* placeholder_comment */   `reg_test_3493_use_comment-1`"));
	db_query.push_back(std::make_pair("`reg_test_3493_use_comment-2`", "USE/* placeholder_comment */ `reg_test_3493_use_comment-2`"));
	db_query.push_back(std::make_pair("`reg_test_3493_use_comment-3`", "USE /* placeholder_comment */`reg_test_3493_use_comment-3`"));
	db_query.push_back(std::make_pair("`reg_test_3493_use_comment-4`", "/* placeholder_comment */USE          `reg_test_3493_use_comment-4`"));
	db_query.push_back(std::make_pair("`reg_test_3493_use_comment-5`", "USE/* placeholder_comment */`reg_test_3493_use_comment-5`"));
	db_query.push_back(std::make_pair("`reg_test_3493_use_comment-6`", "/* comment */USE`reg_test_3493_use_comment-6`"));
	db_query.push_back(std::make_pair("`reg_test_3493_use_comment-7`", "USE`reg_test_3493_use_comment-7`"));

	plan(db_query.size());

	if (
		!mysql_real_connect(
			proxysql_mysql, cl.host, cl.username, cl.password, NULL, cl.port, NULL, 0
		)
	) {
		fprintf(
			stderr, "File %s, line %d, Error: %s\n", __FILE__, __LINE__,
			mysql_error(proxysql_mysql)
		);
		return EXIT_FAILURE;
	}

	// Prepare the DB for the test
	for (std::vector<std::pair<std::string,std::string>>::iterator it = db_query.begin(); it != db_query.end() ; it++) {
	//	MYSQL_QUERY(proxysql_mysql, "DROP DATABASE IF EXISTS reg_test_3493_use_comment");
	//	MYSQL_QUERY(proxysql_mysql, "CREATE DATABASE reg_test_3493_use_comment");
		std::string s = "";
		s = "DROP DATABASE IF EXISTS " + it->first;
		MYSQL_QUERY(proxysql_mysql, s.c_str());
		s = "CREATE DATABASE " + it->first;
		MYSQL_QUERY(proxysql_mysql, s.c_str());
	}

	for (std::vector<std::pair<std::string,std::string>>::iterator it = db_query.begin(); it != db_query.end() ; it++) {
		int i = 0;
		int err = mysql_query(proxysql_mysql, it->second.c_str());
		if (err) {
			diag(
				"'USE' command failed with error code '%d' and error '%s' for query: %s",
				err, mysql_error(proxysql_mysql), it->second.c_str()
			);
			return EXIT_FAILURE;
		}

		// Perform the 'SELECT DATABASE()' query in a new backend connection, to
		// verify that ProxySQL is properly tracking the previously performed 'USE'
		// statement.
		switch (i%5) {
			case 0:
				MYSQL_QUERY(proxysql_mysql, "/* ;create_new_connection=1 */ SELECT DATABASE()");
				break;
			case 1:
				MYSQL_QUERY(proxysql_mysql, "/* ;create_new_connection=1 */SELECT DATABASE()");
				break;
			case 2:
				MYSQL_QUERY(proxysql_mysql, "SELECT /* ;create_new_connection=1 */ DATABASE()");
				break;
			case 3:
				MYSQL_QUERY(proxysql_mysql, "SELECT/* ;create_new_connection=1 */ DATABASE()");
				break;
			case 4:
				MYSQL_QUERY(proxysql_mysql, "SELECT /* ;create_new_connection=1 */DATABASE()");
				break;
			default:
				assert(0);
		}
		i++;
		MYSQL_RES* result = mysql_store_result(proxysql_mysql);
		if (result == nullptr) {
			diag("Invalid 'MYSQL_RES' returned from 'SELECT DATABASE()'");
			return EXIT_FAILURE;
		}

		MYSQL_ROW row = mysql_fetch_row(result);
		if (row == nullptr) {
			diag("Invalid 'MYSQL_ROW' returned from 'SELECT DATABASE()'");
			return EXIT_FAILURE;
		}

		std::string database_name { row[0] };

		if (it->first[0] == '`') {
			database_name = "`" + database_name + "`";
		}
		ok(
			database_name == it->first,
			"Selected DB name should be equal to actual DB name: (Exp: '%s') == (Act: '%s')",
			it->first.c_str(),
			database_name.c_str()
		);
	}

	// Drop created database
	for (std::vector<std::pair<std::string,std::string>>::iterator it = db_query.begin(); it != db_query.end() ; it++) {
		std::string s = "";
		s = "DROP DATABASE IF EXISTS " + it->first;
		MYSQL_QUERY(proxysql_mysql, s.c_str());
	}
	mysql_close(proxysql_mysql);

	return exit_status();
}
