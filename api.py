# app.py
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
import os
from src.helper import preprocess_dataframe, convert_binary_to_string, sanitize_database_name
from lida import Manager, TextGenerationConfig, llm
import base64
import seaborn as sns
import pymongo
import uuid

open_ai:str = "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"
MODEL:str ="gpt-4-1106-preview"

os.environ["OPENAI_API_KEY"] = open_ai
lida = Manager(text_gen=llm("openai", api_key=None))
textgen_config = TextGenerationConfig(n=1, temperature=0.5, model=MODEL, use_cache=True)

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def connect_to_mongodb(uri, db_name, collection_name):
    client = pymongo.MongoClient(uri)
    db = client[sanitize_database_name(db_name)]
    collection = db[collection_name]
    return collection

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        filename = secure_filename(f.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        f.save(file_path)

        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif filename.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            return jsonify({'error': 'Unsupported file format'})

        preprocess_df = preprocess_dataframe(df)
        summary = lida.summarize(preprocess_df, summary_method="default", textgen_config=textgen_config)
        goals = lida.goals(summary, n=10, textgen_config=textgen_config)
        
        charts_data = []
        for goal in goals:
            sns.set(rc={"figure.figsize": (15, 10)})
            library = "seaborn"
            charts = lida.visualize(summary=summary, goal=goal, textgen_config=textgen_config, library=library)
            if charts:
                chart_filename = str(uuid.uuid4()) + '.png'
                chart_path = os.path.join(app.config['UPLOAD_FOLDER'], chart_filename)
                charts[0].savefig(chart_path)
                chart_path = chart_path.replace('\\', '/')
                charts_data.append({'goal': goal.rationale, 'chart_path': chart_path})

        return render_template('result.html', charts=charts_data)

@app.route('/mongodb', methods=['POST'])
def mongodb_analytics():
    if request.method == 'POST':
        uri = request.form['uri']
        db_name = request.form['db']
        collection_name = request.form['collection']

        try:
            collection = connect_to_mongodb(uri, db_name, collection_name)
            data_from_mongo = list(collection.find())
            data_from_mongo = [convert_binary_to_string(doc) for doc in data_from_mongo]

            df = pd.DataFrame(data_from_mongo)
            preprocess_df = preprocess_dataframe(df)
            summary = lida.summarize(preprocess_df, summary_method="default", textgen_config=textgen_config)
            goals = lida.goals(summary, n=10, textgen_config=textgen_config)
            
            charts_data = []
            for goal in goals:
                sns.set(rc={"figure.figsize": (15, 10)})
                library = "seaborn"
                charts = lida.visualize(summary=summary, goal=goal, textgen_config=textgen_config, library=library)
                if charts:
                    chart_filename = str(uuid.uuid4()) + '.png'
                    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], chart_filename)
                    charts[0].savefig(chart_path)
                    charts_data.append({'goal': goal.rationale, 'chart_path': chart_path})
            return render_template('result.html', charts=charts_data)
        except Exception as e:
            return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
