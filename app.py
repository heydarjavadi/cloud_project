from flask import Flask, jsonify, request
import requests
# from flask_mysqldb import MySQL

from flaskext.mysql import MySQL


app = Flask(__name__)


# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = '1234'
# app.config['MYSQL_DB'] = 'cloud'

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
app.config['MYSQL_DATABASE_DB'] = 'cloud'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

# mysql = MySQL(app)

mysql = MySQL()
mysql.init_app(app)

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
    phoneN = request.values.get('phoneNo')
    nationalC = request.values.get('nationalCode')
    address = request.values.get('address')
    postalC = request.values.get('postalCode')

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

    cur = mysql.get_db().cursor()

    if response.status_code == 200:
    	print('Success!')
    	command = "INSERT INTO users_profile(id, email,name,phoneNo,nationalCode,address,postalCode)"
    	cur.execute(command+" VALUES (null, %s,%s,%d,%d,%s,%d)", (email, name,phoneN,nationalC,address,postalC))
    else :
    	print("fail")
    	print(response.status_code)


    print(response.json()['message'])
    
    mysql.get_db.commit()
    cur.close()
    

    return jsonify(response.json())
