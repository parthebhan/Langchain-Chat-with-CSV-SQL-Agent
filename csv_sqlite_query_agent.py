import os
import pandas as pd
from sqlalchemy import create_engine, inspect
import streamlit as st
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, HumanMessage

class CSVToSQLiteConverter:
    def __init__(self, files_dir, db_path) -> None:
        if not os.path.isdir(files_dir):
            raise ValueError(f"The path '{files_dir}' is not a valid directory.")
        
        self.files_directory = files_dir
        self.file_dir_list = os.listdir(files_dir)
        self.engine = create_engine(f"sqlite:///{db_path}")
        print("Number of CSV files:", len(self.file_dir_list))

    def _prepare_db(self):
        for file in self.file_dir_list:
            full_file_path = os.path.join(self.files_directory, file)
            file_name, file_extension = os.path.splitext(file)
            if file_extension == ".csv":
                try:
                    df = pd.read_csv(full_file_path, encoding='utf-8')
                except UnicodeDecodeError:
                    print(f"UnicodeDecodeError while reading {file}, trying 'ISO-8859-1' encoding.")
                    df = pd.read_csv(full_file_path, encoding='ISO-8859-1')
                except Exception as e:
                    print(f"Error reading {file}: {e}")
                    continue
                df.to_sql(file_name, self.engine, index=False, if_exists='replace')
            else:
                print(f"Skipping non-CSV file: {file}")
        print("==============================")
        print("All CSV files have been saved to the SQLite database.")

    def _validate_db(self):
        insp = inspect(self.engine)
        table_names = insp.get_table_names()
        print("==============================")
        print("Available table names in the created SQL DB:", table_names)
        print("==============================")

    def run_pipeline(self):
        self._prepare_db()
        self._validate_db()

def init_database(db_path: str) -> SQLDatabase:
    db_uri = f"sqlite:///{db_path}"
    return SQLDatabase.from_uri(db_uri)

def get_response(user_query: str, db: SQLDatabase) -> str:
    llm = ChatGroq(model="llama-3.1-70b-versatile", temperature=0)
    agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)
    result = agent_executor.invoke({"input": user_query})
    return str(result['output'])

def delete_all_files_in_dir(dir_path: str):
    if os.path.exists(dir_path):
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    os.rmdir(file_path)  # Remove directory if empty
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

# Load environment variables from .env file
load_dotenv()

# Streamlit App
st.set_page_config(page_title="CSV to SQLite and Query Interface", page_icon=":speech_balloon:")

st.title("CSV to SQLite and Chat with SQL Agent")

# Path to the SQLite database file and directory for CSV files
db_path = "student.sqlite"
temp_dir = "temp_csv_files"

with st.sidebar:
    st.subheader("Upload CSV Files, Save to SQLite, and Start Chatting")
    uploaded_files = st.file_uploader("Upload CSV files", type="csv", accept_multiple_files=True)
    
    if st.button("Save to SQLite"):
        if uploaded_files:
            os.makedirs(temp_dir, exist_ok=True)
            
            for uploaded_file in uploaded_files:
                with open(os.path.join(temp_dir, uploaded_file.name), "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            converter = CSVToSQLiteConverter(temp_dir, db_path)
            converter.run_pipeline()
            st.session_state.db = init_database(db_path)
            st.session_state.chat_history = [
                AIMessage(content="Hello! I'm a SQL assistant. Ask me anything about your database."),
            ]
            st.success("CSV files have been converted to SQLite database!")
            st.experimental_rerun()
        else:
            st.warning("Please upload CSV files before saving.")

    if st.button("Clear Chat and Delete All Files"):
        if "chat_history" in st.session_state:
            st.session_state.chat_history = []
        if os.path.exists(db_path):
            try:
                st.session_state.db = None  # Ensure the database connection is closed
                os.remove(db_path)
                st.success("Database file deleted successfully.")
            except PermissionError:
                st.error("Unable to delete the database file. It may be in use by another process.")
            except Exception as e:
                st.error(f"An unexpected error occurred while deleting the database file: {e}")
        if os.path.exists(temp_dir):
            delete_all_files_in_dir(temp_dir)
        st.experimental_rerun()

# Display chat messages
if "chat_history" in st.session_state:
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.markdown(message.content)

# Handle user input
user_query = st.chat_input("Type a message...")
if user_query and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    with st.chat_message("Human"):
        st.markdown(user_query)
    with st.chat_message("AI"):
        if 'db' in st.session_state and st.session_state.db:
            response = get_response(user_query, st.session_state.db)
            st.markdown(response)
            st.session_state.chat_history.append(AIMessage(content=response))
        else:
            st.markdown("Please upload CSV files and convert them to the database first.")
