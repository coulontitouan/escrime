# Create a virtual environment using Python 3
python -m venv venv

# Activate the virtual environment
. .\venv\Scripts\Activate

# Execute the Python script check.py
python .\check.py

# Check the exit code of the previous command
if ($LASTEXITCODE -eq 0) {
    # Install Python packages from requirements.txt
    pip install -r .\requirements.txt
}

# Change the working directory to appEscrime
cd .\appEscrime

# Run the Flask application
flask run -h 0.0.0.0 -p 8080

# Change the working directory back to the parent directory
cd ..

# Deactivate the virtual environment
deactivate
