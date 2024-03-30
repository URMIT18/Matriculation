from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

# Configure PostgreSQL connection
db_username = 'postgres'
db_password = '4486'
db_name = 'test'
db_host = 'localhost'
db_port = '5432'

# Define SQLAlchemy database URL
db_url = f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'

# Define the upload folder for mark sheets
app.config['UPLOAD_FOLDER'] = 'uploads'  # Set the upload folder

@app.route('/', methods=['GET'])
def display():
    # Connect to PostgreSQL database
    engine = create_engine(db_url)

    # Read data from PostgreSQL table into a pandas DataFrame
    df = pd.read_sql_table('excel_data', engine)

    # Check if search query is provided in the request
    search_query = request.args.get('search')

    # Filter DataFrame if search query is provided
    if search_query:
        df = df[df['enrollment '].str.lower().str.contains(search_query.lower(), na=False) | 
                df['name '].str.lower().str.contains(search_query.lower(), na=False)]

    # Convert DataFrame to HTML table
    html_table = df.to_html(index=False)

    return render_template('display.html', html_table=html_table, df=df)


@app.route('/display_selected', methods=['POST'])
def display_selected():
    selected_indices = request.form.getlist('selected_rows')
    
    # Connect to PostgreSQL database
    engine = create_engine(db_url)

    # Read data from PostgreSQL table into a pandas DataFrame
    df = pd.read_sql_table('excel_data', engine)

    # Filter DataFrame to display only selected rows
    selected_df = df.iloc[selected_indices]

    # Convert DataFrame to HTML table
    html_table = selected_df.to_html(index=False)

    return render_template('display_selected.html', html_table=html_table, df=selected_df)



import os
from flask import request, redirect, url_for

@app.route('/submit_marksheets', methods=['POST'])
def submit_marksheets():
    # Handle 10th and 12th mark sheet uploads
    upload_files(request.files.getlist("10th_marksheet"), "10th_marksheet")
    upload_files(request.files.getlist("12th_marksheet"), "12th_marksheet")

    # Redirect to a success page or do additional processing
    return redirect(url_for('success'))

def upload_files(files, folder):
    # Save uploaded files to the specified folder
    for file in files:
        if file.filename != '':
            # Get enrollment number from form data
            enrollment_no = request.form.get("enrollment_no")
            
            # Construct new file name with enrollment number
            new_filename = f"{enrollment_no}_{file.filename}"
            
            # Save file with new filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], folder, new_filename)
            file.save(file_path)


@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True)