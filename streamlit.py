import os
import pandas as pd
from sqlalchemy import create_engine, inspect
import streamlit as st
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage

groq_api_key = st.secrets["groq_api_key"]

class CSVToSQLiteConverter:
    def __init__(self, files_dir, db_path) -> None:
        if not os.path.isdir(files_dir):
            raise ValueError(f"The path '{files_dir}' is not a valid directory.")
        self.files_directory = files_dir
        self.file_dir_list = os.listdir(files_dir)
        self.engine = create_engine(f"sqlite:///{db_path}")

    def _prepare_db(self):
        for file in self.file_dir_list:
            full_file_path = os.path.join(self.files_directory, file)
            file_name, file_extension = os.path.splitext(file)
            if file_extension == ".csv":
                try:
                    df = pd.read_csv(full_file_path, encoding='utf-8')
                except UnicodeDecodeError:
                    df = pd.read_csv(full_file_path, encoding='ISO-8859-1')
                except Exception as e:
                    print(f"Error reading {file}: {e}")
                    continue
                df.to_sql(file_name, self.engine, index=False, if_exists='replace')
            else:
                print(f"Skipping non-CSV file: {file}")

    def _validate_db(self):
        insp = inspect(self.engine)
        table_names = insp.get_table_names()
        print("Available table names in the created SQL DB:", table_names)

    def run_pipeline(self):
        self._prepare_db()
        self._validate_db()

def init_database(db_path: str) -> SQLDatabase:
    db_uri = f"sqlite:///{db_path}"
    return SQLDatabase.from_uri(db_uri)

def get_response(user_query: str, db: SQLDatabase, chat_history: list):
    llm = ChatGroq(model="llama-3.1-70b-versatile", temperature=0, groq_api_key=groq_api_key)
    agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)
    result = agent_executor.invoke({"input": user_query})
    return str(result['output'])

st.set_page_config(page_title="CSV to SQLite and Query Interface", page_icon=":speech_balloon:")

st.title("CSV ChatBot: Chat with Your Data 💬📊")

with st.sidebar:
    st.subheader("This is a simple chat application using SQL Agent. .Upload CSV Files and Connect to the database and start chatting")
    uploaded_files = st.file_uploader("Upload CSV files", type="csv", accept_multiple_files=True)
    
    if st.button("Save to SQLite"):
        if uploaded_files:
            temp_dir = "temp_csv_files"
            os.makedirs(temp_dir, exist_ok=True)
            
            for uploaded_file in uploaded_files:
                with open(os.path.join(temp_dir, uploaded_file.name), "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            converter = CSVToSQLiteConverter(temp_dir, "student.sqlite")
            converter.run_pipeline()
            st.session_state.db = init_database("student.sqlite")
            st.session_state.chat_history = [
                AIMessage(content="Hello! I'm a SQL assistant. Ask me anything about your database."),
            ]
            st.success("CSV files have been converted to SQLite database!")
            st.session_state.refresh_needed = True  # Custom flag to indicate a refresh
        else:
            st.warning("Please upload CSV files before saving.")

if st.session_state.get("refresh_needed", False):
    st.session_state.refresh_needed = False  # Reset flag
    st.write("Data has been refreshed.")  # Trigger UI update

if "chat_history" in st.session_state:
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.markdown(message.content)

user_query = st.chat_input("Type a message...")
if user_query and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    with st.chat_message("Human"):
        st.markdown(user_query)
    with st.chat_message("AI"):
        if 'db' in st.session_state:
            try:
                response = get_response(user_query, st.session_state.db, st.session_state.chat_history)
                st.markdown(response)
                st.session_state.chat_history.append(AIMessage(content=response))
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.write(e)
        else:
            st.markdown("Please upload CSV files and convert them to the database first.")
