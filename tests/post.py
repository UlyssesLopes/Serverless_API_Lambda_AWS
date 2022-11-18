import requests
from werkzeug.security import generate_password_hash

password = '12345'

hashed_password = generate_password_hash(password, method='sha256')

BASE = 'https://6hm7rylwz7.execute-api.us-east-1.amazonaws.com/prod/user'
BASE_COUNT = 'https://6hm7rylwz7.execute-api.us-east-1.amazonaws.com/prod/users'

response_count = requests.get(BASE_COUNT)
key_count = response_count.json()
my_first_key = key_count['solutionID']
my_key = my_first_key['Count']
count_str = str(my_key)

new_user = {
    "solutionID": count_str,
    "nome": "Ulysses Lopes",
    "email": "ulysses.lopes@wyntech.inf.br",
    "password": hashed_password
}

response = requests.post(BASE, json=new_user)
print(response.json())



