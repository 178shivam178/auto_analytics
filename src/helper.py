from bson.binary import Binary
from PIL import Image
from io import BytesIO
import base64
import warnings
warnings.filterwarnings("ignore")


def base64_to_image(base64_string):
    byte_data = base64.b64decode(base64_string)
    return Image.open(BytesIO(byte_data))


def convert_binary_to_string(doc):
    for key, value in doc.items():
        if isinstance(value, Binary):
            doc[key] = str(value)
    return doc


def sanitize_database_name(database_name):
    return database_name.replace(' ', '')


def preprocess_dataframe(df, max_columns=50, missing_threshold=30, random_state=None):
    if df.shape[1] > max_columns:
        if df.isnull().values.any():
            missing_percentage = (df.isnull().sum() / len(df)) * 100
            columns_to_drop = missing_percentage[missing_percentage > missing_threshold].index
            df = df.drop(columns=columns_to_drop, axis=1)
        processed_df = df.sample(n=max_columns, axis=1, random_state=random_state)
    else:
        processed_df = df
    return processed_df