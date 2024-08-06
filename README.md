# **Chat Interface with AI Using SQL Agent**

## `Complete CSV QA: From Upload to Database Storage and Querying`

[![Streamlit App](https://img.shields.io/badge/Streamlit_App_-CSV_Chatbot-ff69b4.svg?style=for-the-badge&logo=Streamlit)](https://langchain-chat-with-csv-sql-agent-fgra9nwxng6utyytzzg692.streamlit.app/)
## Purpose

This application provides a Streamlit interface that allows users to upload CSV files, convert them into SQLite database tables, and interact with the database using an AI-powered chat interface. Users can ask questions about the database content and receive responses through a conversational AI model.

## Dependencies

- **Streamlit:** For building the interactive web application.
- **pandas:** For reading CSV files and managing data.
- **sqlalchemy:** For database connection and operations.
- **langchain_community:** Provides SQL database utilities and SQL agent tools.
- **langchain_groq:** For integrating with Llama-3.1-70b-versatile AI models.
- **dotenv:** For loading environment variables from a `.env` file.

## Main Functions and Workflow

### `CSVToSQLiteConverter`

**Purpose:** Converts CSV files in a specified directory into tables in an SQLite database.

#### Methods:

- **`__init__(self, files_dir, db_path)`:** Initializes the converter with the directory of CSV files and SQLite database path.

- **`_prepare_db(self)`:** Converts CSV files to SQL tables and saves them into the SQLite database. Each CSV file’s name (excluding the extension) is used as the table name.

- **`_validate_db(self)`:** Prints available table names in the created SQLite database for validation.

- **`run_pipeline(self)`:** Executes the data import pipeline, including database preparation and validation.

### `init_database(db_path: str) -> SQLDatabase`

**Purpose:** Initializes the SQLDatabase from the SQLite database URI.

**Implementation:** Uses `SQLDatabase.from_uri()` with the database URI.

### `get_response(user_query: str, db: SQLDatabase, chat_history: list)`

**Purpose:** Handles user queries and retrieves responses using the AI chat model.

**Implementation:**

- **`llm`:** Initializes **`ChatGroq`** with Llama-3.1 AI model.
- **`agent_executor`:** Creates an SQL agent for query processing.
- **`result`:** Performs the query and returns the result as a string.

### Streamlit App

**Purpose:** Sets up the Streamlit web interface for CSV file upload, database conversion, and chat-based querying.

**Implementation:**

- **`st.set_page_config()`:** Configures the Streamlit page settings.
- **`st.title()`:** Sets the title of the Streamlit app.
- **File Upload and Conversion:** Users can upload CSV files, which are saved and processed into an SQLite database on clicking "Save to SQLite".
- **Chat Interface:** Displays chat history and handles user input to query the database using the AI chat model.

## Usage

1. **Upload CSV Files:** Users upload CSV files through the Streamlit interface.
2. **Convert to SQLite:** Clicking "Save to SQLite" processes the files and saves them into the database.
3. **Ask Questions:** Users can type questions related to the database content, and the AI model provides answers based on the processed data.

## Summary

This application integrates AI and NLP techniques to enhance the interaction with PDF content through a web interface. It supports seamless text extraction, database storage, and query handling using AI capabilities.

## Author

Created by **Parthebhan Pari**.

## Notes

- Ensure a stable internet connection for interacting with the Gemini Pro model.
- Handle and store your API key securely.


### **🔗 Connect with Me**

Feel free to connect with me on :

[![portfolio](https://img.shields.io/badge/my_portfolio-000?style=for-the-badge&logo=ko-fi&logoColor=white)](https://parthebhan143.wixsite.com/datainsights)

[![LinkedIn Profile](https://img.shields.io/badge/LinkedIn_Profile-000?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/parthebhan)

[![Kaggle Profile](https://img.shields.io/badge/Kaggle_Profile-000?style=for-the-badge&logo=kaggle&logoColor=white)](https://www.kaggle.com/parthebhan)

[![Tableau Profile](https://img.shields.io/badge/Tableau_Profile-000?style=for-the-badge&logo=tableau&logoColor=white)](https://public.tableau.com/app/profile/parthebhan.pari/vizzes)


