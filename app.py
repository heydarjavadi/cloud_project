from flask import Flask, jsonify, request,url_for, redirect
import requests

from suds.client import Client


import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

app = Flask(__name__)


MMERCHANT_ID = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'  # Required
ZARINPAL_WEBSERVICE = 'https://sandbox.zarinpal.com/pg/services/WebGate/wsdl'  # Required
amount = 1000  # Amount will be based on Toman  Required
description = u'zarinpal test'  # Required
email = 'user@userurl.ir'  # Optional
mobile = '09153456789'  # Optional


@app.route('/account/pay/', methods=['GET','POST'])
def send_request():
    if request.method == 'POST':

        orderID = request.values.get('orderID')

        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''

        print(auth_token)

        role = requests.get(
          'http://localhost:2000/auth/v1/user/role',
                params={},
                headers={'Authorization': 'Bearer '+auth_token},
                )

        print("pay role status_code : "+str(role.status_code))

        if role.status_code == 200 :
            print(role.json())
            email = role.json()['email']

            cursor = connection.cursor()
            command = "SELECT * FROM users_profile"
            cursor.execute(command+" WHERE email='"+str(email)+"'")
            data = cursor.fetchall()
            print(data)

            profileID = data[0][0]
            mobile = data[0][3]

            print(profileID)

            command = "SELECT * FROM users_transaction"
            cursor.execute(command+" WHERE profileID="+str(profileID) +" and orderID='"+orderID+"'")
            data = cursor.fetchall()
            print(data)
            cursor.close()

            amount = data[0][4]

            print(amount,mobile,email)

            client = Client(ZARINPAL_WEBSERVICE)
            result = client.service.PaymentRequest(MMERCHANT_ID,
                                                   amount,
                                                   description,
                                                   email,
                                                   mobile,
                                                   str(url_for('verify', _external=True)))
            if result.Status == 100:
                return redirect('https://sandbox.zarinpal.com/pg/StartPay/' + result.Authority)
            else:
                return 'Error'

        else :
            return jsonify(role.json())




@app.route('/account/pay/callback', methods=['GET'])
def verify():
    client = Client(ZARINPAL_WEBSERVICE)
    if request.args.get('Status') == 'OK':
        result = client.service.PaymentVerification(MMERCHANT_ID,
                                                    request.args['Authority'],
                                                    amount)
        if result.Status == 100:
            return 'Transaction success. RefID: ' + str(result.RefID)
        elif result.Status == 101:
            return 'Transaction submitted : ' + str(result.Status)
        else:
            return 'Transaction failed. Status: ' + str(result.Status)
    else:
        return 'Transaction failed or canceled by user'


try:
    connection = mysql.connector.connect(host='localhost',
                                     database='cloud',
                                     user='root',
                                     password=''
                                     )

except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)




@app.route('/account/heartbeat', methods=['GET','POST'])
def heartbeat():
    return "Account Management is up and running"

@app.route('/account/transaction', methods=['GET'])
def account_transaction():
    if request.method == "GET":
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''

        print(auth_token)

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
            cursor.execute(command+" WHERE email='"+str(email)+"'")
            data = cursor.fetchall()
            print(data)

            profileID = data[0][0]

            print(profileID)

            command = "SELECT * FROM users_transaction"
            cursor.execute(command+" WHERE profileID="+str(profileID))
            data = cursor.fetchall()
            print(data)

            cursor.close()
            return jsonify({'transactions':data})
        else :
            return jsonify(role.json())

@app.route('/account/wallet', methods=['GET'])
def account_wallet():
    if request.method == "GET":
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''

        print(auth_token)

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
            cursor.execute(command+" WHERE email='"+str(email)+"'")
            data = cursor.fetchall()
            print(data)

            profileID = data[0][0]

            print(profileID)

            command = "SELECT * FROM users_wallet"
            cursor.execute(command+" WHERE profileID="+str(profileID))
            data = cursor.fetchall()
            print(data)

            cursor.close()
            return jsonify({'value':data[0][2]})
        else :
            return jsonify(role.json())

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
            cursor.execute(command+" VALUES (null,'"+email+"', '"+name+"','"+phoneN+"','"+nationalC+"','"+address+"','"+postalC+"');")
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
            return(register.json())

        login = requests.post(
          'http://localhost:2000/auth/v1/user/login',
                data=params
                )
        print("login status_code : "+str(login.status_code))

        if login.status_code == 200 :
            print(login.json())
            token = login.json()['token']


        return jsonify(login.json())

    elif request.method == "GET":
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''

        print(auth_token)

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
            cursor.execute(command+" WHERE email='"+str(email)+"'")
            data = cursor.fetchall()
            print(data)
            cursor.close()
            return jsonify({'profile':data})
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
            upd = " SET name ='"+str(name)+"', phoneNO ='"+phoneN + "', nationalCode ='"+ nationalC + "', address ='"+str(address) + "', postalCode ='"+ postalC+"'"
            whr = " WHERE email = '" + email+"'"
            print(command + upd + whr)
            cursor.execute(command + upd + whr)
            connection.commit()

            command = "SELECT * FROM users_profile"
            cursor.execute(command+" WHERE email='"+str(email)+"'")
            data = cursor.fetchall()
            print(data)

            return jsonify({'profile':data})
        else :
            return jsonify(role.json())


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)