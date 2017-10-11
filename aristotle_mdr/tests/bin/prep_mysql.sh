echo "preparing mysql"

mysql -e 'create database aristotle_test_db;' -u root
mysql -e 'SET GLOBAL wait_timeout = 36000;'
mysql -e 'SET GLOBAL max_allowed_packet = 134209536;'
