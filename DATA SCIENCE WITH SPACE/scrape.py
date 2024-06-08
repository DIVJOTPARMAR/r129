from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import os

# URL of the page to scrape
START_URL = "https://en.wikipedia.org/wiki/List_of_brown_dwarfs"

# Initialize the Selenium WebDriver (Make sure you have ChromeDriver installed and in your PATH)
browser = webdriver.Chrome()
browser.get(START_URL)

# Wait for the page to fully load (adjust the timeout as needed)
WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'wikitable')))

# Use BeautifulSoup to parse the page content after it is fully loaded
soup = BeautifulSoup(browser.page_source, 'html.parser')

# Get all the tables of the page using find_all() method of the BeautifulSoup library
tables = soup.find_all('table', class_='wikitable')

# Create an empty list to store the row data
rows = []

# Get all the <tr> tags from the table
for table in tables:
    for row in table.find_all('tr')[1:]:  # Skip the header row
        cells = row.find_all('td')
        row_data = [cell.text.strip() for cell in cells]
        rows.append(row_data)

# Close the browser as we have already scraped the data
browser.quit()

# Create an empty list to store star name, radius, mass, and distance data
star_data = []

# Use a for loop to take out all the <td> tags, we only need the text and we can strip any other characters using strip() method
for row in rows:
    if len(row) >= 9:  # Ensure that there are enough columns (adjust if necessary)
        name = row[0]
        distance = row[5]
        mass = row[7]
        radius = row[8]
        star_data.append([name, distance, mass, radius])

# Define Header for DataFrame
headers = ["name", "distance", "mass", "radius"]

# Using the pandas library make a DataFrame from the above list
star_df = pd.DataFrame(star_data, columns=headers)

# Save the scraped data to a CSV file
star_df.to_csv('scraped_data.csv', index=True, index_label="id")

# Load the CSV file of brown dwarf stars
brown_dwarfs_df = pd.read_csv('scraped_data.csv')

# Clean the data by deleting NaN values
brown_dwarfs_df.dropna(inplace=True)

# Remove non-numeric characters from 'mass' and 'radius' columns
brown_dwarfs_df['mass'] = brown_dwarfs_df['mass'].str.extract('(\d+\.?\d*)').astype(float)
brown_dwarfs_df['radius'] = brown_dwarfs_df['radius'].str.extract('(\d+\.?\d*)').astype(float)

# Step 3: Convert radius and mass to solar units
# Multiply each value in the radius column with 0.102763 to convert to solar radius
brown_dwarfs_df['radius'] = brown_dwarfs_df['radius'] * 0.102763

# Multiply each value in the mass column with 0.000954588 to convert to solar mass
brown_dwarfs_df['mass'] = brown_dwarfs_df['mass'] * 0.000954588

# Create a new CSV file with the converted values
brown_dwarfs_df.to_csv('converted_brown_dwarfs.csv', index=True, index_label="id")

# Specify the path to the 'brightest_stars.csv' file
brightest_stars_csv_path = 'brightest_stars.csv'

# Check if the 'brightest_stars.csv' file exists
if os.path.exists(brightest_stars_csv_path):
    # Load the CSV file of brightest stars
    brightest_stars_df = pd.read_csv(brightest_stars_csv_path)

    # Ensure both DataFrames have consistent column names if necessary
    # For example, if both DataFrames have 'name', 'mass', 'radius', and 'distance' columns
    merged_df = pd.merge(brightest_stars_df, brown_dwarfs_df, on='name', how='outer')

    # Save the merged DataFrame to a new CSV file
    merged_df.to_csv('merged_stars_data.csv', index=True, index_label="id")

    print("Data scraped, cleaned, converted, and merged successfully.")
else:
    print(f"File '{brightest_stars_csv_path}' not found. Please check the path and ensure the file exists.")
