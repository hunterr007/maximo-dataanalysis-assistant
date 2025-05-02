import streamlit as st
import pandas as pd
import json
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load data
CSV_PATH = "data/maximo_data.csv"
LOGO_PATH = "data/Logo.jpg"
df = pd.read_csv(CSV_PATH)
df["DATE"] = pd.to_datetime(df["DATE"])

# Simulated Gemini class (you can replace this later)
class GeminiAPI:
    def __init__(self, api_key: str, model: str = "gemini-2.0"):
        self.api_key = api_key
        self.model = model

    def generate_response(self, prompt: str) -> str:
        return f"Simulated response from Gemini: {prompt[:100]}..."

gemini_api_key = os.getenv("GOOGLE_API_KEY")
gemini_model = GeminiAPI(api_key=gemini_api_key)

# Chart generation
def generate_chart(chart_type: str, labels: list, data: list, title: str) -> str:
    chart_config = {
        "type": chart_type,
        "data": {
            "labels": list(map(str, labels)),
            "datasets": [{
                "label": title,
                "data": list(data)
            }]
        },
        "options": {
            "title": {"display": True, "text": title},
            "plugins": {
                "legend": {"labels": {"color": "black", "font": {"size": 14}}}
            }
        }
    }
    url = "https://quickchart.io/chart"
    response = requests.get(url, params={"c": json.dumps(chart_config)})
    return response.url

# Classification and chart logic
def classify_and_generate(user_input):
    user_input = user_input.lower()

    if "labor hours" in user_input and "failure code" in user_input:
        data = df.groupby("FAILURECODE")["LABORHRS"].sum()
        return "bar", data.index.tolist(), data.values.tolist(), "Labor Hours by Failure Code"

    elif "labor hours" in user_input and "asset" in user_input:
        data = df.groupby("ASSETNUM")["LABORHRS"].sum()
        return "pie", data.index.tolist(), data.values.tolist(), "Labor Hours by Asset"

    elif "work orders" in user_input and "location" in user_input:
        data = df["LOCATION"].value_counts()
        return "bar", data.index.tolist(), data.values.tolist(), "Work Orders by Location"

    elif "failure code" in user_input and "downtime" in user_input:
        data = df.groupby("FAILURECODE")["LABORHRS"].sum()
        return "treemap", data.index.tolist(), data.values.tolist(), "Downtime by Failure Code"

    elif "trend" in user_input or "over time" in user_input:
        trend = df.groupby(df["DATE"].dt.to_period("M"))["LABORHRS"].sum().sort_index()
        labels = trend.index.astype(str).tolist()
        values = trend.values.tolist()
        return "line", labels, values, "Labor Hour Trend Over Time"

    elif "average labor hours" in user_input:
        avg = df["LABORHRS"].mean()
        return "metric", None, round(avg, 2), "Average Labor Hours per Work Order"

    elif "more than 5 labor hours" in user_input:
        filtered_df = df[df["LABORHRS"] > 5]
        return "table", None, filtered_df, "Work Orders with > 5 Labor Hours"

    elif "labor hours" in user_input and "location" in user_input:
        data = df.groupby("LOCATION")["LABORHRS"].sum()
        return "area", data.index.tolist(), data.values.tolist(), "Labor Hours by Location"

    return None, None, None, None

# Streamlit UI
st.set_page_config(page_title="Maximo Chart Assistant", layout="wide")
st.image(LOGO_PATH, width=150)
st.title("📊 Maximo Data Analysis Assistant")

user_input = st.text_input("Ask a Maximo-related question:")

if user_input:
    # Simulated Gemini call
    columns_str = ", ".join(df.columns.tolist())
    sample_df = df.head(5).copy()
    if "DATE" in sample_df.columns:
        sample_df["DATE"] = sample_df["DATE"].astype(str)
    data_sample = sample_df.to_dict(orient="records")
    prompt = f"The dataset has columns: {columns_str}\n\nSample data: {json.dumps(data_sample, indent=2)}\n\nQuestion: {user_input}"
    response = gemini_model.generate_response(prompt)
    st.subheader("Assistant Response")
    #st.info(response)

    # Output chart/table/metric
    chart_type, labels, values, title = classify_and_generate(user_input)

    if chart_type in ["bar", "pie", "line", "area", "treemap"]:
        chart_url = generate_chart(chart_type, labels, values, title)
        st.image(chart_url, caption=title)

    elif chart_type == "table":
        st.subheader(title)
        st.dataframe(values)

    elif chart_type == "metric":
        st.metric(label=title, value=values)

    else:
        st.warning("No chart or result could be generated for this question.")
