import seaborn as sns
from src.helper import *
import streamlit as st
import sys, os
import pandas as pd
from streamlit_option_menu import option_menu
import pymongo
import warnings
warnings.filterwarnings("ignore")
from logg import logger
from exceptions import anyException
from constant import *
from lida import Manager, TextGenerationConfig, llm

def csv_analytics_app():
    try:
        os.environ["OPENAI_API_KEY"] = open_ai
        logger.info("Successfully Set up the Open AI key")
        lida = Manager(text_gen=llm("openai", api_key=None))
        textgen_config = TextGenerationConfig(n=1, temperature=0.5, model=MODEL, use_cache=True)
        goal_op = []
        st.title("CSV Auto Analytics")
        uploaded_file= st.sidebar.file_uploader("Upload your CSV", type="csv")
        logger.info("Successfully uploaded the csv file")
        if uploaded_file is not None and st.sidebar.button('Submit'):
            df = pd.read_csv(uploaded_file)
            logger.info("Successfully reading the content from csv file")
            preprocess_df = preprocess_dataframe(df)
            logger.info("Successfully preprocessed the dataframe")
            summary = lida.summarize(preprocess_df, summary_method="default", textgen_config=textgen_config)
            logger.info("Successfully summarizing the dataframe")
            goals = lida.goals(summary, n=10, textgen_config=textgen_config)
            logger.info("Successfully created the goals")
            if goals:
                for goal in goals:
                    goal_op.append(goal)
                for i in goal_op:
                    sns.set(rc={"figure.figsize": (15, 10)})
                    library = "seaborn"
                    textgen_config = TextGenerationConfig(n=1, temperature=0.2, use_cache=True)
                    charts = lida.visualize(summary=summary, goal=i, textgen_config=textgen_config, library=library)
                    if charts:
                        img_base64_string = charts[0].raster
                        img = base64_to_image(img_base64_string)
                        st.write(i.rationale)
                        logger.info("Successfully write the content of the chart")
                        st.image(img, use_column_width=True)
                        logger.info("Successfully wrote the chart")
    except Exception as e:
        logger.exception("An error occurred in the csv_analytics_app function.")
        raise anyException(e, sys)


def excel_analytics_app():
    try:
        os.environ["OPENAI_API_KEY"] = open_ai
        logger.info("Successfully Set up the Open AI key")
        lida = Manager(text_gen=llm("openai", api_key=None))
        textgen_config = TextGenerationConfig(n=1, temperature=0.5, model=MODEL, use_cache=True)
        goal_op = []
        st.title("Excel Auto Analytics")
        uploaded_file = st.sidebar.file_uploader("Upload your excel", type="xlsx")
        logger.info("Successfully uploaded the excel file")
        if uploaded_file is not None and st.sidebar.button('Submit'):
            df = pd.read_excel(uploaded_file)
            logger.info("Successfully reading the content from excel file")
            preprocess_df = preprocess_dataframe(df)
            logger.info("Successfully preprocessed the dataframe")
            summary = lida.summarize(preprocess_df, summary_method="default", textgen_config=textgen_config)
            logger.info("Successfully summarizing the dataframe")
            goals = lida.goals(summary, n=10, textgen_config=textgen_config)
            logger.info("Successfully created the goals")
            if goals:
                for goal in goals:
                    goal_op.append(goal)
                for i in goal_op:
                    sns.set(rc={"figure.figsize": (15, 10)})
                    library = "seaborn"
                    textgen_config = TextGenerationConfig(n=1, temperature=0.2, use_cache=True)
                    charts = lida.visualize(summary=summary, goal=i, textgen_config=textgen_config, library=library)
                    if charts:
                        img_base64_string = charts[0].raster
                        img = base64_to_image(img_base64_string)
                        st.write(i.rationale)
                        logger.info("Successfully write the content of the chart")
                        st.image(img, use_column_width=True)
                        logger.info("Successfully wrote the chart")
    except Exception as e:
        logger.exception("An error occurred in the excel_analytics_app function.")
        raise anyException(e, sys)


def db_analytics_app():
    try:
        st.title("DB's Auto Analytics")
        os.environ["OPENAI_API_KEY"] = open_ai
        logger.info("Successfully Set up the Open AI key")
        mongo_uri = st.sidebar.text_input("MongoDB URI")
        mongo_db = st.sidebar.text_input("MongoDB database name")
        mongo_collection = st.sidebar.text_input("MongoDB collection name")
        mongo_db = sanitize_database_name(mongo_db)
        if st.sidebar.button("Submit"):
            if not mongo_db:
                st.warning("Please enter a valid MongoDB database name.")
                return
            try:
                client = pymongo.MongoClient(mongo_uri)
                logger.info("Successfully connected mongo db")
                db = client[mongo_db]
                collection = db[mongo_collection]
                data_from_mongo = list(collection.find())
                logger.info(f"Successfully collected {db} {collection}")
                data_from_mongo = [convert_binary_to_string(doc) for doc in data_from_mongo]
                lida = Manager(text_gen=llm("openai", api_key=None))
                textgen_config = TextGenerationConfig(n=1, temperature=0.5, model=MODEL, use_cache=True)
                goal_op = []
                df = pd.DataFrame(data_from_mongo)
                preprocess_df = preprocess_dataframe(df)
                logger.info("Successfully preprocessed the dataframe")
                summary = lida.summarize(preprocess_df, summary_method="default", textgen_config=textgen_config)
                logger.info("Successfully summarizing the dataframe")
                goals = lida.goals(summary, n=10, textgen_config=textgen_config)
                logger.info("Successfully created the goals")
                if goals:
                    for goal in goals:
                        goal_op.append(goal)
                    for i in goal_op:
                        sns.set(rc={"figure.figsize": (15, 10)})
                        library = "seaborn"
                        textgen_config = TextGenerationConfig(n=1, temperature=0.2, use_cache=True)
                        charts = lida.visualize(summary=summary, goal=i, textgen_config=textgen_config, library=library)
                        if charts:
                            img_base64_string = charts[0].raster
                            img = base64_to_image(img_base64_string)
                            st.write(i.rationale)
                            logger.info("Successfully write the content of the chart")
                            st.image(img, use_column_width=True)
                            logger.info("Successfully wrote the chart")
            except pymongo.errors.ConnectionFailure as e:
                st.error(f"Error connecting to MongoDB: {e}")
            except Exception as e:
                st.error(f"Error processing data: {e}")
    except Exception as e:
        logger.exception("An error occurred in the excel_analytics_app function.")
        raise anyException(e, sys)



st.set_page_config(page_title="Analytics", layout="wide")
with st.sidebar:
    selected = option_menu(
        menu_title="Menu",
        options=["CSV_Auto_analytics", "Excel_Auto_analytics", "DB_Auto_analytics"],
        icons = ['bar-chart-fill', 'bar-chart-fill', 'bar-chart-fill'],
        default_index=1,)
if selected == "CSV_Auto_analytics":
    csv_analytics_app()
if selected == "Excel_Auto_analytics":
    excel_analytics_app()
if selected == "DB_Auto_analytics":
    db_analytics_app()