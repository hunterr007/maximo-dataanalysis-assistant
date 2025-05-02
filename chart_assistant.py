import pandas as pd
import json
import os
from dotenv import load_dotenv
import requests

# Load environment variables (e.g., API keys)
load_dotenv()

# Load your Maximo data (adjust the path as needed)
CSV_PATH = "data/maximo_data.csv"
df = pd.read_csv(CSV_PATH)

# QuickChart Tool to generate charts
def generate_chart(chart_type: str, labels: list, data: list, title: str) -> str:
    chart_config = {
        "type": chart_type,
        "data": {
            "labels": labels,
            "datasets": [{
                "label": title,
                "data": data
            }]
        },
        "options": {
            "title": {"display": True, "text": title},
            "plugins": {
                "legend": {
                    "labels": {
                        "color": "black",
                        "font": {"size": 14}
                    }
                }
            }
        }
    }
    response = requests.get("https://quickchart.io/chart", params={"c": json.dumps(chart_config)})
    return response.url

# Define a function to interact with Gemini API
class GeminiAPI:
    def __init__(self, api_key: str, model: str = "gemini-2.0"):
        self.api_key = api_key
        self.model = model

    def generate_response(self, prompt: str) -> str:
        # Placeholder for actual Gemini API interaction
        # You should replace this with your actual API call
        return f"Simulated response from Gemini model: {prompt}"

# Instantiate the Gemini API interaction
gemini_api_key = os.getenv("GOOGLE_API_KEY")
gemini_model = GeminiAPI(api_key=gemini_api_key)

# Main program loop for interacting with the assistant
if __name__ == "__main__":
    print("Maximo Chart Generator - Type 'exit' to quit.")
    
    while True:
        user_input = input("\nAsk a question: ")
        
        if user_input.lower() in ['exit', 'quit']:
            break
        
        # Format the prompt dynamically with the dataset and user input
        columns_str = ", ".join(df.columns.tolist())
        sample_data = df.head(10).to_dict(orient="records")
        data_str = json.dumps(sample_data, indent=2)

        prompt_template = """
        You are a Maximo data assistant.
        The dataset you're working with has the following columns:
        {columns_str}

        Data:
        {data_str}

        Please answer the following question:
        {question}
        """
        
        prompt = prompt_template.format(columns_str=columns_str, data_str=data_str, question=user_input)
        
        # Print the generated prompt (for debugging purposes)
        #print("Final Prompt:")
        #print(prompt)

        # Get the response from Gemini API
        response = gemini_model.generate_response(prompt)

        # Display the model's response
        #print("Response:")
        #print(response)

        # Check if the user asked for a graph (you can customize this logic)
        if "labor hours" in user_input.lower() and "failure code" in user_input.lower():
            # Example: Generating chart for total labor hours spent on each failure code
            failure_codes = df['FAILURECODE'].value_counts()
            labels = failure_codes.index.tolist()
            data = failure_codes.values.tolist()
            chart_url = generate_chart("bar", labels, data, "Labor Hours by Failure Code")
            print(f"Generated Chart URL: {chart_url}")

        # Add other conditions for different types of questions that may require charts
        elif "labor hours" in user_input.lower() and "asset" in user_input.lower():
            # Example: Generating chart for labor hours spent on each asset
            asset_hours = df.groupby('ASSETNUM')['LABORHRS'].sum()  # Use 'ASSETNUM' instead of 'ASSET'
            labels = asset_hours.index.tolist()
            data = asset_hours.values.tolist()
            chart_url = generate_chart("pie", labels, data, "Labor Hours by Asset")
            print(f"Generated Chart URL: {chart_url}")

        # More chart generation logic can be added here based on your needs
