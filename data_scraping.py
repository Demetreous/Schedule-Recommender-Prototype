# Libraries
import requests
from requests.api import request
from requests.cookies import RequestsCookieJar
from bs4 import BeautifulSoup
import csv


# Get the JSESSIONID
JSESSIONID = requests.get("https://registrationssb.ucr.edu").cookies["JSESSIONID"]

# Set the headers for the request
headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}

# Make a post request to search the page to establish the connection to get the cookies
term = "202410" #  the first 4 digits mean the year and the last 2 digits mean the quarter you want to search for (10 = winter, 20 = spring, 30 = summer, 40 = fall)
r = request("POST", "https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/term/search?mode=search", data={"term": term})

# Store the cookies in your cookie jar
jar = RequestsCookieJar()
jar.update(r.cookies)

# Get the total number of courses/sections in the quarter:
pageOffset = 0
pageMaxSize = 500

# Initial request to get totalCount of courses
url = f"https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/searchResults/searchResults?&txt_term={term}&pageOffset={pageOffset}&pageMaxSize={pageMaxSize}&sortColumn=subjectDescription&sortDirection=asc"
response = request("GET", url, headers=headers, cookies=jar)
totalCount = response.json()["totalCount"]

# Print the total number of courses
print(f"Total number of courses in term {term}: {totalCount}")

pageMaxSize = 500  # max request size
courses = []
pageOffset = 0


while True:
    print(len(courses))
    url = f"https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/searchResults/searchResults?&txt_term={term}&startDatepicker=&endDatepicker=&pageOffset={pageOffset}&pageMaxSize={pageMaxSize}&sortColumn=subjectDescription&sortDirection=asc"
    
    response = request("GET", url, headers=headers, cookies=jar)
    response.raise_for_status()
    new_courses = response.json()["data"]
       
    if not new_courses:
        print("No more courses available.")
        break
       
    courses.extend(new_courses)
       
    if len(new_courses) < pageMaxSize:
        print("Fetched all available data.")
        break
       
    pageOffset += pageMaxSize # getting next 500 sections
       
    if len(courses) >= totalCount:
        break

# Filter out unique courses based on (subject, courseNumber)
unique_courses = {}

for course in courses:
    key = (course["subject"], course["courseNumber"])
    if key not in unique_courses:
        unique_courses[key] = course

print(f"Total unique courses fetched: {len(unique_courses)}")
#pprint(unique_courses)

def fetch_course_description(course, term, headers):
    response = requests.post(
        "https://registrationssb.ucr.edu/StudentRegistrationSsb/ssb/searchResults/getCourseDescription", 
        headers=headers, 
        data={"term": term, "courseReferenceNumber": course["courseReferenceNumber"]}
    )
    return response

def extract_clean_description(response):
    soup = BeautifulSoup(response.text, "html.parser")
    section = soup.find("section", {"aria-labelledby": "courseDescription"})
    if section:
        return section.get_text(separator=" ", strip=True)
    else:
        return "No description available."

# Build a list of cleaned course records
course_records = []

for course_key in unique_courses:
    course = unique_courses[course_key]
    response = fetch_course_description(course, term, headers)
    description = extract_clean_description(response)

    record = {
        "subject": course["subject"],
        "courseNumber": course["courseNumber"],
        "courseTitle": course.get("courseTitle", ""),
        "description": description
    }
    course_records.append(record)

# Save to CSV
csv_filename = f"ucr_courses_{term}_descriptions.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["subject", "courseNumber", "courseTitle", "description"])
    writer.writeheader()
    writer.writerows(course_records)

print(f"Saved {len(course_records)} courses to '{csv_filename}'")