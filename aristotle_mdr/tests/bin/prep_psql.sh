echo "preparing postgres"

psql -c 'create database aristotle_test_db;' -U postgres
