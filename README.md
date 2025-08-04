# README - Global Exam Automation Script

This script automates login and exercise solving on **Global Exam** until 20 hours of activity are reached.

## Requirements
1. **Python 3.9+** installed
2. Install dependencies from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   playwright install
   ```
3. Put your credentials in the `.env` file:
   ```env
   EMAIL=your_email
   PASSWORD=your_password
   ```

## Running the Script
Execute:
```bash
python script_resolve.py
```

The script will:
1. Log into Global Exam with your credentials
2. Automatically accept cookies
3. Start the exercise in **IT & Cybersecurity > IT is everywhere**
4. Loop through the exercise until 20 hours of activity are reached

Finally, the browser will automatically close after a few seconds.
