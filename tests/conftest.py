# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.

from base64 import b64encode
from textwrap import dedent

from starlette.config import environ

environ['QUEUE_SERVICE'] = 'http://QUEUE_SERVICE'
environ['METADATA_SERVICE'] = 'http://METADATA_SERVICE'
environ['AUTH_SERVICE'] = 'http://AUTH_SERVICE/v1'
environ['REDIS_HOST'] = '127.0.0.1'
environ['REDIS_PORT'] = '6379'
environ['REDIS_DB'] = '0'
environ['REDIS_PASSWORD'] = ''
environ['RDS_HOST'] = 'host'
environ['RDS_PORT'] = '5059'
environ['RDS_USERNAME'] = 'user'
environ['RDS_PASSWORD'] = 'pass'
environ['RDS_NAME'] = 'test'
environ['RDS_SCHEMA'] = 'public'
environ['RDS_TABLE_NAME'] = 'archive_preview'
environ['RDS_ECHO_SQL_QUERIES'] = 'false'
environ['RSA_PUBLIC_KEY'] = b64encode(
    dedent(
        '''\
        -----BEGIN PUBLIC KEY-----
        MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA3W8G98lcmkQ5XsEBoAPH
        8ihU+1m+kHxGEzV7eMxOWNmJkmKR/Du38vRsSUW12NSqZoWZmmmSEF01A1kD1t14
        Qe01p9VTBAK8zVULvAAOoCsuEXHRM5gn6I8HJsO2OI3nn0f6MXnFkhcD6HZ0fWLX
        dAosKvduhQzD+7y+bIk3uXOg1Sq120F1O6v1GYBxEr7NExZ7I6IbJXKC0VhdjI9B
        6qMEjvsUTHHUhscZuX4U7FFDyF3Q2/1qfO6sz6AkyKJ4BvYAJpsIll9NldDBcOWh
        gtuEXsyagw4YUh094qIMhUP46NMoab+wLqz9Uebm4dkavfRNQ7+08Wj+rvVhPs0C
        ewIDAQAB
        -----END PUBLIC KEY-----
        '''
    ).encode()
).decode()

pytest_plugins = [
    'tests.fixtures.app',
    'tests.fixtures.db',
    'tests.fixtures.fake',
    'tests.fixtures.redis',
    'tests.fixtures.cache',
    'tests.fixtures.services.metadata',
    'tests.fixtures.services.queue',
    'tests.fixtures.components.task_dispatch',
    'tests.fixtures.components.resource_operations',
    'tests.fixtures.components.task_stream',
]
