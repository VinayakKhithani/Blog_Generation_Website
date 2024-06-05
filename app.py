from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import requests
import boto3
from botocore.exceptions import ClientError
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  


API_URL = 'https://6qchf9twe5.execute-api.us-east-1.amazonaws.com/dev/blog-generation'
cognito_client = boto3.client('cognito-idp', region_name='us-east-1')

user_pool_id = 'us-east-1_nuwg5N2BW'
client_id = '3hi8rv8hkr9h69nkken4d4vm14'

@app.route('/')
def home0():
    return render_template('index0.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        try:
            response = cognito_client.sign_up(
                ClientId=client_id,
                Username=username,
                Password=password,
                UserAttributes=[{'Name': 'email', 'Value':email}]
            )
            return redirect(url_for('confirm'))
        except ClientError as e:
            return render_template('register.html', error=e.response['Error']['Message'])
    return render_template('register.html')

@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    if request.method == 'POST':
        username = request.form['username']
        confirmation_code = request.form['confirmation_code']
        try:
            response = cognito_client.confirm_sign_up(
                ClientId=client_id,
                Username=username,
                ConfirmationCode=confirmation_code,
            )
            return redirect(url_for('login'))
        except ClientError as e:
            return render_template('confirm.html', error=e.response['Error']['Message'])
    return render_template('confirm.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            response = cognito_client.initiate_auth(
                ClientId=client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={'USERNAME': username, 'PASSWORD': password,}
            )
            id_token = response['AuthenticationResult']['IdToken']
            return render_template('index.html', id_token=id_token)
        except ClientError as e:
            return render_template('login.html', error=e.response['Error']['Message'])
    return render_template('login.html')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_blog', methods=['POST'])
def generate_blog():
    blog_topic = request.form['blogTopic']
    response = requests.post(API_URL, json={'blog_topic': blog_topic})

    if response.status_code == 200:
        response_data = response.json()
        blog_content = response_data.get('body')
        return render_template('index.html', blog=blog_content)
    else:
        return render_template('index.html', error="Failed to generate blog")

@app.route('/logout')
def logout():
    session.clear()  # Clear session data
    return redirect(url_for('home0'))

if __name__ == '__main__':
    app.run(debug=True)
