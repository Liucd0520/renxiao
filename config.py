from urllib.parse import quote_plus

username =  'root'
password = 'liucd123'
host = '172.31.24.111'
port = 3307
database = 'renxiao'

encoded_password = quote_plus(password)
mysql_uri = f'mysql+mysqlconnector://{username}:{encoded_password}@{host}:{port}/{database}'
