### FR-3331:

This feature request can be implemented as:
1. extended table mysql_servers to add 3 more columns; 
2. extended table runtime_mysql_servers to add 3 more columns;
3. Class MySrvC() needs to be extended to include the new fields;
4. loading configuration from config file needs to be modified;
5. commands like LOAD MYSQL SERVERS TO RUNTIME and SAVE MYSQL SERVERS FROM RUNTIME needs to support the new columns;
6. When connecting to a backend, the relevant key/cert need to be used;