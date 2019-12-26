from flask import Flask, jsonify, request
import requests

import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

try:
    connection = mysql.connector.connect(host='localhost',
                                     database='cloud',
                                     user='root',
                                     password='1234')

except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)


app = Flask(__name__)


@app.route('/heartbeat', methods=['GET','POST'])
def heartbeat():
    return "Account Management is up and running"


@app.route('/account/profile', methods=['GET','POST','PUT'])
def account_profile():
    
    if request.method == "POST":
    
        email = request.values.get('email')
        passw = request.values.get('password')
        name = request.values.get('name')
        phoneN = request.values.get('phoneNo')
        nationalC = request.values.get('nationalCode')
        address = request.values.get('address')
        postalC = request.values.get('postalCode')

        name = name if name else 'null'
        phoneN = phoneN if phoneN else 'null'
        nationalC = nationalC if nationalC else 'null'
        address = address if address else 'null'
        postalC = postalC if postalC else 'null'


        params = {
        'email': email,
        'password': passw
        }
        register = requests.post(
          'http://localhost:2000/auth/v1/user/register',
                data=params
                )


        if register.status_code == 200 or register.status_code == 201:

            cursor = connection.cursor()
            command = "INSERT INTO users_profile(id, email,name,phoneNo,nationalCode,address,postalCode)"
            cursor.execute(command+" VALUES (null,'"+email+"', '"+name+"',"+phoneN+","+nationalC+",'"+address+"',"+postalC+");")
            print(cursor.rowcount, "Record inserted successfully into cloud users_profile table")
            user_id = cursor.lastrowid
            connection.commit()
            cursor.close()

            cursor = connection.cursor()
            command = "INSERT INTO users_wallet(id, profileID,value)"
            cursor.execute(command+" VALUES (null,"+str(user_id)+",0)")
            print(cursor.rowcount, "Record inserted successfully into cloud users_wallet table")

            connection.commit()
            cursor.close()


            print('Success!')
        else :
            print("registeration failed")
            print(register.status_code)
            print(register.json()['message'])

        login = requests.post(
          'http://localhost:2000/auth/v1/user/login',
                data=params
                )
        print("login status_code : "+str(login.status_code))

        if login.status_code == 200 :
            print(login.json())
            token = login.json()['token']


        role = requests.get(
          'http://localhost:2000/auth/v1/user/role',
                params={},
                headers={'Content_Type':'application/json','Authorization': 'Bearer '+token},
                auth=('Authorization', 'Bearer '+token)
                )

        print("role status_code : "+str(role.status_code))
        print(role.content)
        print(role.request.headers)
        print(role.request.body)

        if role.status_code == 200 :
            print(role.json())
            email = role.json()['email']
        else : 
            print(role.json()['message'])



        return jsonify(login.json())

    elif request.method == "GET":
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''

        role = requests.get(
          'http://localhost:2000/auth/v1/user/role',
                params={},
                headers={'Authorization': 'Bearer '+auth_token},
                )
        if role.status_code == 200 :
            print(role.json())
            email = role.json()['email']

            cursor = connection.cursor()
            command = "SELECT * FROM users_profile"
            cursor.execute(command+" WHERE email="+str(email))
            data = cursor.fetchall()
            print(data)
            cursor.close()
            return jsonify(data.json())
        else :
            return jsonify(role.json())

    elif request.method == "PUT":

        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''

        role = requests.get(
          'http://localhost:2000/auth/v1/user/role',
                params={},
                headers={'Authorization': 'Bearer '+auth_token},
                )
        if role.status_code == 200 :
            print(role.json())
            email = role.json()['email']

            name = request.values.get('name')
            phoneN = request.values.get('phoneNo')
            nationalC = request.values.get('nationalCode')
            address = request.values.get('address')
            postalC = request.values.get('postalCode')


            cursor = connection.cursor()
            command = "UPDATE users_profile"
            upd = " SET name ="+str(name)+", phoneNO ="+phoneN + ", nationalCode ="+ nationalCode + ", address ="+str(address) + ", postalCode ="+ postalCode
            whr = "WHERE email = " + email
            cursor.execute(command + upd + whr)
            print(data)
            connection.commit()

            command = "SELECT * FROM users_profile"
            cursor.execute(command+" WHERE email="+str(email))
            data = cursor.fetchall()
            print(data)

            return jsonify(data.json())
        else :
            return jsonify(role.json())


