import os
from os import environ

environ['database_file_name'] = "database.db"
environ['project_dir'] = os.path.dirname(os.path.abspath(__file__))
environ['database_path'] = "sqlite:///{}".format(
                                os.path.join(environ['project_dir'],
                                            environ['database_file_name']))