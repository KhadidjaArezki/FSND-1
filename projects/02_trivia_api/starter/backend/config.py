from os import environ

environ['database_owner'] = 'postgres'
environ['database_password'] = '12345'
environ['host'] = 'localhost:5432'
environ['production_database_name'] = "trivia"
environ['test_database_name'] = "trivia_test"
environ['database_path'] = "postgresql://{}:{}@{}".format(
                            environ['database_owner'],
                            environ['database_password'],
                            environ['host'])

