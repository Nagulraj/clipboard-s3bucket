from datetime import datetime
from flask import Flask, render_template, flash, url_for, session, redirect
import os
import sys
from flask import request
from random import randint
from werkzeug.utils import secure_filename
import logging
import boto3
from botocore.exceptions import ClientError
# from flask.ext.session import Session
from dotenv import load_dotenv
import datetime

app = Flask(__name__)
load_dotenv()
# sess = Session()

UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER")
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'log'])
BUCKET = os.environ.get("BUCKET")
LINK = os.environ.get("LINK")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def home():
    
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_file', methods=['POST'])
def upload_file():
    
    # check if the post request has the file part
    if 'file' not in request.files:        
        result = {
            'result' : 0,    
        }
        return render_template('result.html', result=result)
    
    file = request.files['file']
    print("file")
    
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':        
        result = {
            'result' : 0,    
        }

        return render_template('result.html', result=result)
    
    if file and allowed_file(file.filename):
        file_name = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        file.save(filepath)

        print('filepath : ', filepath)
        
        result = {
            'image_location' : filepath
        }

        
        object_name = "screen_shot_"+str(datetime.datetime.now())+".jpeg"
        
        

        # Upload the file
        s3_client = boto3.client('s3')
        try:
            response = s3_client.upload_file(filepath, BUCKET, object_name)
            link = LINK + object_name
        except ClientError as e:
            logging.error(e)
        #     return False
        # return True

        os.remove(filepath)
        return render_template('result.html', result = result, filepath = filepath ,link = link)
    
    #return content
    return render_template('result.html')

if __name__ == '__main__':
    host = os.environ.get('IP', '127.0.0.1')
    port = int(os.environ.get('PORT', 6021))
    
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    # sess.init_app(app)
    
    app.run(host= host, port = port, use_reloader = False)
   