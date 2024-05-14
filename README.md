# merch-track
This repo will contain the source code for the Merch Track Django App

### Instructions to contribute to the codebase

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/gab-cat/merch-track.git
    cd merch-track
    ```

2. **Create a Virtual Environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # For MacOS/Unix
    
    # On Windows use:
    .venv\Scripts\Activate.ps1
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Make Your Changes**:
    - Start Django Server 
    ```bash
    python manage.py runserver
    ```

    - Open another terminal and start Tailwind Dev to see real-time changes
    ```bash
    cd theme/static_src
    npm install
    npm start
    ```

5. **Update Static Files**:
    ```bash
    # Close the tailwind terminal
    # npm run build

    # Close the terminal used to run the server
    python manage.py collectstatic
    ```

5. **Update `requirements.txt`** (if you add new dependencies):
    ```bash
    pip freeze > requirements.txt
    ```

6. **Commit and Push Your Changes**:
    ```bash
    git add .
    git commit -m "Your detailed commit message"
    git push origin <your_branch>
    ```

7. **Create a Pull Request**:
    - Go to the repository on GitHub.
    - Create a new Pull Request from your branch to the main branch.
    - Provide a detailed description of the changes you made.

9. **Code Review**:
    - Respond to any feedback or requested changes from the code reviewers promptly.

10. **Merge the Pull Request**:
    - Once approved, merge the pull request as per the project's guidelines.


## How to access PostgreSQL database

### Database Info


| Parameter  | Value                                  |
|------------|----------------------------------------|
| NAME       | merch-track_db                         |
| USER       | merch-track                            |
| PASSWORD   | 6m56rP:Drn4f9Ts                       |
| HOST       | postgresql-merch-track.alwaysdata.net |
| PORT       | 5432                                   |



1. **Go to the Website**:
   - Open your web browser and navigate to [https://phppgadmin.alwaysdata.com/](https://phppgadmin.alwaysdata.com/).

2. **Login to phppgadmin**:
   - Enter your username and password provided by the hosting provider or database administrator.

3. **Select Your Database**:
   - Once logged in, you will see a list of databases associated with your account. Click on the database you want to access.

4. **Navigate Tables and Data**:
   - After selecting the database, you can navigate through its tables, views, and other objects.
   - Click on the table name to view its data or structure.

5. **Perform Operations**:
   - You can perform various operations such as viewing, inserting, updating, and deleting data.
   - Use the provided tools and options to execute SQL queries or manage database objects.

6. **Logout** (Optional):
   - Once you are done, it's a good practice to log out of phppgadmin to secure your account.

## Packages required for Virtual Environment
| Package               | Version             |
|-----------------------|---------------------|
| arrow                 | 1.3.0               |
| asgiref               | 3.8.1               |
| binaryornot           | 0.4.4               |
| certifi               | 2024.2.2            |
| chardet               | 5.2.0               |
| charset-normalizer    | 3.3.2               |
| click                 | 8.1.7               |
| cookiecutter          | 2.6.0               |
| Django                | 5.0.6               |
| django-tailwind       | 3.8.0               |
| idna                  | 3.7                 |
| Jinja2                | 3.1.4               |
| markdown-it-py        | 3.0.0               |
| MarkupSafe            | 2.1.5               |
| mdurl                 | 0.1.2               |
| pip                   | 23.0.1              |
| psycopg2-binary       | 2.9.9               |
| Pygments              | 2.18.0              |
| python-dateutil       | 2.9.0.post0         |
| python-slugify        | 8.0.4               |
| PyYAML                | 6.0.1               |
| requests              | 2.31.0              |
| rich                  | 13.7.1              |
| setuptools            | 65.5.0              |
| six                   | 1.16.0              |
| sqlparse              | 0.5.0               |
| tailwind              | 3.1.5b0             |
| text-unidecode        | 1.3                 |
| types-python-dateutil | 2.9.0.20240316      |
| typing_extensions     | 4.11.0              |
| urllib3               | 2.2.1               |
