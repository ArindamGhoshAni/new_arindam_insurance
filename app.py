from importlib.resources import path
from unittest import result
from flask  import   Flask , send_file ,render_template, abort, request
from importlib_metadata import files
import numpy as np
import jsonify
import pickle
import pymongo
from pymongo import MongoClient
from pymongo import collection
from matplotlib.style import context
import os
import sys
from insurance.logger import logging
from insurance.exception import InsurancePredictor
from insurance.constant import  get_current_time_stamp
from insurance.logger import get_log_dataframe


ROOT_DIR = os.getcwd()
LOG_FOLDER_NAME = "insurance_logs"
LOG_DIR = os.path.join(ROOT_DIR, LOG_FOLDER_NAME)

app = Flask(__name__)

#pic folder 
picFolder = os.path.join('static','pics')
app.config['UPLOAD_FOLDER'] = picFolder


#DB Connection
client = MongoClient("mongodb+srv://Arin:Arindam@insurance.lx7vz.mongodb.net/?retryWrites=true&w=majority")
db = client["storedata"]
collection = db["user"]

#Pickle file
model = pickle.load(open('insurance_predict_model.pkl', 'rb'))

@app.route('/',methods=['GET'])
def home():
    try:
        raise Exception("Testing")
    except Exception as e:
        insurance = InsurancePredictor(e,sys)
        logging.info(insurance.error_message)
        logging.info("Log test")
    return render_template('home.html')



@app.route('/index',methods=['GET'])
def hello():
    return render_template('index.html')
    
@app.route('/predict',methods=['POST'])
def predict():
    if request.method == 'POST':
        age = int(request.form['a'])
        sex = request.form['sex']
        bmi = float(request.form['c'])
        child = int(request.form['d'])
        smoker = request.form['smoker']
        region = request.form['region']
        prediction = model.predict([[age , sex, bmi, child, smoker, region]])
        output=round(prediction[0],2)
        collection.insert_one({"age" : age, "sex": sex,"bmi":bmi,"child":child,"smoker":smoker,"region":region,"Predicted Price":output})
        return render_template('index.html',prediction_text="    Predicted premium : {}".format(output))
    else:
        return render_template('index.html')


@app.route(f'/logs', defaults={'req_path': f'{LOG_FOLDER_NAME}'})
@app.route(f'/{LOG_FOLDER_NAME}/<path:req_path>')
def render_log_dir(req_path):
    os.makedirs(LOG_FOLDER_NAME, exist_ok=True)
    # Joining the base and the requested path
    logging.info(f"req_path: {req_path}")
    abs_path = os.path.join(req_path)
    print(abs_path)
    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        log_df = get_log_dataframe(abs_path)
        context = {"log":log_df.to_html(classes="table-striped", index=False)}
        return render_template('log.html', context=context)

    # Show directory contents
    files = {os.path.join(abs_path, file): file for file in os.listdir(abs_path)}

    result = {
        "files": files,
        "parent_folder": os.path.dirname(abs_path),
        "parent_label": abs_path
    }
    return render_template('log_files.html', result=result)
    
@app.route('/download',methods=['GET'])
def download_log():
    p = "LOG_FOLDER_NAME"
    return send_file(p,as_attachment =True)

if __name__ == '__main__':
    app.run(debug=True)