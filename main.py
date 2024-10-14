import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import webbrowser  # To open a new browser session for the links
import re  # Import regular expressions


# Google Sheets setup, checking and creating a sheet for the current date
def setup_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('bionic-torch-438111-n3-836be08ebaee.json', scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet
    sheet = client.open("Glassdoor Job Links")

    # Get the current date in 'dd.mm' format
    current_date = datetime.now().strftime("%d.%m")

    try:
        # Check if a worksheet with the current date exists
        worksheet = sheet.worksheet(current_date)
    except gspread.exceptions.WorksheetNotFound:
        # If not, create a new worksheet with the current date as the name
        worksheet = sheet.add_worksheet(title=current_date, rows=1000, cols=5)

    return worksheet


# Load excluded and required words and logging preference from the config file
def load_words_and_settings(filename):
    excluded_words = []
    required_words = []
    log_to = "txt"  # Default logging method
    current_section = None

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:  # Ignore blank lines
                continue

            if line == "excluded_words:":
                current_section = 'excluded'
                continue
            elif line == "required_words:":
                current_section = 'required'
                continue
            elif line == "log_to:":
                current_section = 'log_to'
                continue

            # Ensure we only add non-empty words to the respective lists
            if current_section == 'excluded' and line:
                excluded_words.append(line.lower())
            elif current_section == 'required' and line:
                required_words.append(line.lower())  # Store in lowercase
            elif current_section == 'log_to' and line:
                log_to = line.lower()  # Read the logging method ('txt' or 'google_sheet')

    print(f"Loaded config: Excluded Words = {excluded_words}, Required Words = {required_words}, Logging to = {log_to}")
    return excluded_words, required_words, log_to


# Load the search URL from the extra_links.txt file
def load_search_link(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        search_url = file.readline().strip()  # Read the first line as the search URL
    return search_url


# Search jobs and store valid links based on the logging preference
def search_jobs(driver, excluded_words, required_words, log_to, sheet=None, log_filename=None, search_url=None):
    driver.get(search_url)  # Use the loaded search URL
    time.sleep(5)

    job_links = []
    try:
        job_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "JobCard_jobTitle___7I6y"))
        )

        print(f"Found {len(job_elements)} job elements.")  # Debugging: check number of job cards found

        for job in job_elements:
            job_url = job.get_attribute("href")
            print(f"Job URL: {job_url}")  # Debugging: print job URL being processed
            job_links.append(job_url)

        valid_links = []  # Collect valid links here

        for link in job_links:
            driver.get(link)
            time.sleep(3)

            # Try to click "Show More" button
            try:
                # Locate the button by its class name and text content ("Mehr anzeigen")
                show_more_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[@class='JobDetails_showMore___Le6L' and span[text()='Mehr anzeigen']]"))
                )
                show_more_button.click()  # Click the button if found
                time.sleep(2)
            except Exception as e:
                print(f"No 'Show More' button found or clickable: {e}")

            try:
                job_title = driver.find_element(By.CLASS_NAME, "heading_Heading__BqX5J").text
                job_description = driver.find_element(By.CSS_SELECTOR, "div.JobDetails_jobDescription__uW_fK").text

                print(f"Job Title: {job_title}")  # Debugging: print job title
                print(f"Job Description: {job_description[:100]}...")  # Debugging: print a snippet of job description

                # Check if any excluded words are in the job description
                excluded_word_found = None
                for word in excluded_words:
                    if word in job_description.lower():
                        excluded_word_found = word
                        break

                print(
                    f"Excluded Words Matched: {excluded_word_found}, Words Checked: {excluded_words}")  # Debugging: print excluded word

                # Check if any required words are in the job description using regex
                required_word_found = None
                for word in required_words:
                    word = word.strip().lower()  # Strip whitespace and convert to lowercase
                    # Use regex to find the word regardless of surrounding punctuation
                    pattern = r'\b' + re.escape(word) + r'\b'  # Create a regex pattern for whole words
                    if re.search(pattern, job_description.lower()):  # Compare with lowercase job description
                        required_word_found = word
                        break

                print(
                    f"Required Words Matched: {required_word_found}, Words Checked: {required_words}")  # Debugging: print required word

                # If no excluded words and at least one required word found, log the job
                if not excluded_word_found and required_word_found:
                    valid_links.append(link)  # Collect the valid link
                    if log_to == "txt":
                        with open(log_filename, 'a') as f:
                            f.write(link + '\n')
                            print(
                                f"Valid Job Link saved to .txt file: {link}, triggered by required word: {required_word_found}")
                    elif log_to == "google_sheet":
                        sheet.append_row([link])
                        print(
                            f"Valid Job Link saved to Google Sheet: {link}, triggered by required word: {required_word_found}")

            except Exception as e:
                print(f"Error extracting information from {link}: {e}")

            driver.back()
            time.sleep(2)

    except Exception as e:
        print("Error occurred while finding job links:", e)
        print("Page source:", driver.page_source)

    return valid_links


def is_english(text):
    common_english_words = ['the', 'and', 'is', 'in', 'to', 'of', 'for', 'a']
    return any(word in text.lower() for word in common_english_words)


def main():
    excluded_words, required_words, log_to = load_words_and_settings('config.txt')  # Load words and logging settings
    search_url = load_search_link('extra_links.txt')  # Load the search link
    driver = webdriver.Chrome()

    # Initialize logging
    sheet = None
    log_filename = None
    if log_to == "google_sheet":
        sheet = setup_google_sheet()  # Create/Access a tab with the current date
    elif log_to == "txt":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f'glassdoor_job_links_{timestamp}.txt'

    try:
        valid_links = search_jobs(driver, excluded_words, required_words, log_to, sheet, log_filename, search_url)
    finally:
        driver.quit()

    # Open valid links in a new Google Chrome session
    if valid_links:
        print("Opening links in a new Chrome session...")
        for link in valid_links:
            webbrowser.open(link)


if __name__ == "__main__":
    main()
