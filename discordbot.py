import requests
import openai
from datetime import datetime, timedelta, date
import pytz
import streamlit as st


# Generate a summary 
def generate_summary(text, prompt_input):
    try:
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": (f"{prompt_input}:\n\n{text}\n\n")}
    ],
        max_tokens = 1500,
        temperature = 0.2    
)
        summary = response['choices'][0]['message']['content']
        return summary

    except openai.error.APIError as e:
        st.text(f"Error generating summary: {e}")

# Retrieve messages from Discord 
def retrieve_messages(start_date, end_date, auth, channel_id):
    try:
        # Define the API endpoint and headers
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        headers = {"Authorization": auth}

        # Define the query parameters
        start_timestamp = int(datetime.combine(start_date, datetime.min.time(), tzinfo=pytz.UTC).timestamp())
        end_timestamp = int(datetime.combine(end_date, datetime.min.time(), tzinfo=pytz.UTC).timestamp()) + 86399
        params = {
            "start": start_timestamp,
            "end": end_timestamp
        }

        # Make the request to retrieve the messages
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        # Parse the JSON response and return the messages
        messages = response.json()
        return messages
    except requests.exceptions.RequestException as e:
        st.text(f"Error retrieving messages: {e}")



#st.title("Alpha Discord Summarizer")
st.markdown("<h1 style='text-align: center;'>Alpha Discord Summarizer</h1>", unsafe_allow_html=True)

gif_url = "https://assets-global.website-files.com/60118ca18674407b85935203/629917e0522f329567a38d70_blokcchaindata%20%20gif%20under%204.gif"
st.markdown(f'<div style="display: flex; align-items: center;"><img src="{gif_url}" style="width: 100%; margin-right: 50px;"></div>', unsafe_allow_html=True)


start_date = st.date_input("**Select the start date**:")
end_date = st.date_input("**Select the end date**:")
prompt_input = st.text_input("**Enter your prompt_input**:")
auth = st.text_input("**Enter your Discord authorization token**:")
# API key
openaiKey = st.text_input("**Enter your openai.api_key**:")

openai.api_key = openaiKey

channel_id = st.text_input("**Enter the Discord channel ID**:")
if st.button("**Generate Summary**"):
    with st.spinner('Fetching messages...'):
        messages = retrieve_messages(start_date, end_date, auth, channel_id)
    if messages is not None and len(messages) > 0:
        combined_message = []
        for message in reversed(messages):
            timestamp = datetime.fromisoformat(message['timestamp']).replace(tzinfo=pytz.UTC).date()
            if start_date <= timestamp <= end_date:
                text = message['content']
                combined_message.append(text.strip())
        if combined_message:
            fetched_messages = "<br>".join(combined_message)
            st.subheader("Fetched Messages:")
            st.write(fetched_messages, unsafe_allow_html=True)
            with st.spinner('Generating summary...'):
                summary = generate_summary(fetched_messages, prompt_input)
            if summary is not None:
                st.subheader("Summary:")
                st.write(summary, unsafe_allow_html=True)
            else:
                st.text("No summaries generated.")
        else:
            st.text("No messages found.")
    else:
        st.text("No messages found.")


