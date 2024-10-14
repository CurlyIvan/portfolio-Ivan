# Job Scraper

## Overview

The **Job Scraper** is a Python application designed to scrape job listings from Glassdoor, focusing on positions relevant to project management. The application retrieves job descriptions and logs valid job links based on specific criteria defined in a configuration file. It can save the links either to a Google Sheet or a local text file.

## Features

- **Web Scraping**: Utilizes Selenium to automate the extraction of job postings from Glassdoor.
- **Configuration File**: Easily configurable to include/exclude certain keywords to filter job descriptions.
- **Google Sheets Integration**: Logs valid job links directly into a Google Sheet for easy tracking.
- **Dynamic Search URL**: Allows users to specify the search URL, making it adaptable to different job markets.

## Technologies Used

- **Python**: The core language for developing the application.
- **Selenium**: For automating web browser interaction and scraping job listings.
- **gspread**: For managing and writing to Google Sheets.
- **OAuth2Client**: For Google API authentication.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/job-scraper.git
   cd job-scraper

2. **Create a virtual environment (optional but recommended):**

bash
Копировать код
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. **Install the required packages:**

pip install -r requirements.txt

4. **Set up Google Sheets API:**

Create a project in the Google Developer Console.
Enable the Google Sheets API.
Create service account credentials and download the JSON file.
Rename the JSON file to credentials.json and place it in the project directory.

**Configuration**
Create a config.txt file to specify:

excluded_words: Words that should not be in the job descriptions.
required_words: Words that must be in the job descriptions.
log_to: Specify whether to log to a text file or Google Sheets.

**Usage**
Specify the search URL in extra_links.txt:
https://www.glassdoor.com/Job/germany-project-manager-jobs-SRCH_IL.0,7_IN96_KO8,23.htm?fromAge=1&minRating=3.0

**Run the application:**
python job_scraper.py

View your results:

Valid job links will be saved in your specified format (Google Sheets or text file).
