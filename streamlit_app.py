import openai
import requests
import streamlit as st
import urllib.request
from bs4 import BeautifulSoup
import json
import os
import ssl

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True)
  
st.title("ChatGPT-like clone")  
  
api_address = st.text_input("API Address", value="")  
api_key = st.text_input("API Key", value="")
website_link = st.text_input("Website Link", value="")
  
if "messages" not in st.session_state:  
    st.session_state.messages = []  
  
for message in st.session_state.messages:  
    with st.chat_message(message["role"]):  
        st.markdown(message["content"])  
  
if prompt := st.chat_input("What is up?"):  
    st.session_state.messages.append({"role": "user", "content": prompt})  
    with st.chat_message("user"):  
        st.markdown(prompt)  
  
    with st.chat_message("assistant"):  
        message_placeholder = st.empty()  
        full_response = ""  
  
        if api_address and api_key:
            message_placeholder.markdown(full_response)  
            chat_history = [  
                {  
                    "inputs": {"question": m["content"]},  
                    "outputs": {"answer": m["content"]},  
                }  
                for m in st.session_state.messages  
                if m["role"] == "user"  
            ]  
  
            # Download and strip website content
            if website_link:
                response = requests.get(website_link)
                soup = BeautifulSoup(response.content, "html.parser")
                stripped_content = soup.get_text().strip()

                context = f"*** BEGIN OF CONTEXT ***\n{stripped_content}\n*** END OF CONTEXT ***"
            else:
                context = ""

            # Add context to the beginning of the prompt                                                                                                                                                    
            if context:                                                                                                                                                                                     
                prompt = f"{context}\n{prompt}"                                                                                                                                                             
                                                                                                                                                                                                             
            data = {                                                                                                                                                                                        
                "chat_history": chat_history,                                                                                                                                                               
                "question": prompt,                                                                                                                                                                         
            }   
            
            body = str.encode(json.dumps(data))

            # Replace this with the primary/secondary key or AMLToken for the endpoint
            url = api_address
            if not api_key:
                raise Exception("A key should be provided to invoke the endpoint")

            # The azureml-model-deployment header will force the request to go to a specific deployment.
            # Remove this header to have the request observe the endpoint traffic rules
            headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': 'blue' }

            req = urllib.request.Request(url, body, headers)

            try:
                response = urllib.request.urlopen(req)
                x = json.loads(response.read())
                full_response += str(x['answer'])
                
            except urllib.error.HTTPError as error:
                print("The request failed with status code: " + str(error.code))

                # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
                print(error.info())
                print(error.read().decode("utf8", 'ignore'))

        else:  
            message_placeholder.markdown("Please enter a valid API Address and API Key.")  
  
        message_placeholder.markdown(full_response)  
    st.session_state.messages.append({"role": "assistant", "content": full_response})  
