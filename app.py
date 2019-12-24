from flask import Flask
from flask import jsonify
import requests
from flask import request


app = Flask(__name__)

@app.route('/heartbeat', methods=['GET','POST'])
def heartbeat():
    return "Account Management is up and running"


@app.route('/account/profile', methods=['GET','POST'])
def account_profile():
    
    # if request.method == "POST":
    
    print(request.values)
    email = request.values.get('email')
    passw = request.values.get('password')
    name = request.values.get('name')
    phonen = request.values.get('phoneNo')
    nationalc = request.values.get('nationalCode')
    address = request.values.get('address')
    postalc = request.values.get('postalCode')

    print(email)
    print(passw)

    params = {
    'email': email,
    'password': passw
    }
    response = requests.post(
      'http://localhost:2000/auth/v1/user/register',
            data=params
            )

    print(response)
    print(response.json()['message'])
    

    return jsonify(response.json())
