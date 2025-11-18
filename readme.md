## local setup

1. create (and enter) python virtual environment:
    ```
    python3 -m venv venv
    ```
    - to enter virtual env: `source venv/bin/activate`  
    - to leave virtual env: `deactivate`  

1. inside your virtual environment, install dependencies:
    ```
    python3 -m pip install -r requirements.txt
    ```

1. to run the jupyter notebook:
    ```
    jupyter notebook
    ```

1. to run the streamlit app:
    ```
    python3 -m streamlit run explorer_app.py
    ```
    
<!-- 1. create `.env` and store environment variables for project config in there (e.g. `API_KEY=<api-keys-value-here>`) -->
