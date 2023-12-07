from flask import Flask, render_template, jsonify, request, redirect, session, url_for
import sqlite3
import json
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import subprocess

app = Flask(__name__)
# authentication configuration
app.secret_key = 'your_secret_key' #change this to your secret key for security within the OS
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app) #bind the login manager to the application

# hardcode the password - don't keep this
# todo: get the passwords from a file or a database
# todo: passwords should be hashed
users = {
    "admin":"12345"
}

# create the user mixin to work with our application
class User(UserMixin):
    def __init__(self, username):
        self.id = username

# define how a user gets loaded in the application
# for example if the first, last names needed loading from the DB it would be there
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST': # there was a form submitted
        username = request.form.get('username') #POST data 
        formPassword = request.form.get('password')
        #handle the "next" parameter which gets the user back to the correct page
        next = request.args.get('next') #GET data (data in the URL)
        #todo: replace with a hashed password verification from a database
        DBPassword = users.get(username)
        if DBPassword == formPassword: # replace with hashed password verification eventually
            #authentication is successful - login the user
            user = User(username)
            login_user(user)
            return redirect(next) # redirect the user to the resource they were requesting

    return render_template('login.html')


DB_FILE = "../historian_data.db"

CONFIG_FILE = "../config.json"
#load the configuration data
with open(CONFIG_FILE, 'r') as config_file:
    config_data = json.load(config_file)

# return a view file
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# return simple text
@app.route('/configure', methods=['GET'])
@login_required
def configure():
    return render_template('configure.html', config=config_data)

@app.route('/restart', methods=['GET'])
def restart():
    service_name = "IoT_Controller.service"
    try:
        subprocess.run(['sudo', 'systemctl', 'restart', service_name], check=True)
        return f"Service {service_name} restarted successfully."
    except subprocess.CalledProcessError as e:
        return f"Error restarting service {service_name}: {e}"


@app.template_filter('jsonstring')
def reverse_filter(obj):
    return json.dumps(obj)

@app.route('/add_configuration',methods=['POST'])
def add_configuration():
    topic = request.form.getlist('topic[]')
    comparison = request.form.getlist('comparison[]')
    value = request.form.getlist('value[]')
    result_topic = request.form.getlist('result_topic[]')
    result_value = request.form.getlist('result_value[]')

    conditions = [{"topic":topic[index], "comparison":comparison[index], "value":value[index]} for index in range(len(topic))]
    results = [{"topic":result_topic[index], "value":result_value[index]} for index in range(len(result_topic))]

    input = {"conditions":conditions,"results":results}

    config_data.append(input)

    #rewrite the configuration file
    with open(CONFIG_FILE, 'w') as config_file:
        json.dump(config_data, config_file, indent=4)

    return redirect('/configure')

@app.route('/edit_configuration',methods=['POST'])
def edit_configuration():
    rule_to_edit = int(request.form.get('rule_to_edit'))
    topic = request.form.getlist('topic[]')
    comparison = request.form.getlist('comparison[]')
    value = request.form.getlist('value[]')
    result_topic = request.form.getlist('result_topic[]')
    result_value = request.form.getlist('result_value[]')

    conditions = [{"topic":topic[index], "comparison":comparison[index], "value":value[index]} for index in range(len(topic))]
    results = [{"topic":result_topic[index], "value":result_value[index]} for index in range(len(result_topic))]

    input = {"conditions":conditions,"results":results}

    config_data[rule_to_edit] = input

    #rewrite the configuration file
    with open(CONFIG_FILE, 'w') as config_file:
        json.dump(config_data, config_file, indent=4)

    return redirect('/configure')

@app.route('/delete_configuration',methods=['POST'])
def delete_configuration():
    index = int(request.form.get('rule_to_delete'))

    if 0 <= index and index < len(config_data):
        del config_data[index]

        #rewrite the configuration file
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump(config_data, config_file, indent=4)

    return redirect('/configure')

#get historian data to the web "user"
@app.route('/historian', methods=['GET'])
def historian():
    topic = request.args.get('topic',"#")
    timestamp = request.args.get('timestamp',"1970-01-01 00:00:00")

    topic = topic.replace('#','%')

    SQL = "SELECT timestamp, topic, payload FROM historian_data WHERE timestamp >= ? and topic LIKE ?"

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(SQL,(timestamp,topic))

    results = cursor.fetchall()

    result_data = [{"topic":row[1], "payload":row[2], "timestamp":row[0]} for row in results]

    return jsonify(result_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
