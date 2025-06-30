import google.generativeai as genai
import pandas as pd

api_key = "" # Replace with your actual API key
genai.configure(api_key=api_key)

course_desciptions = pd.read_csv("ucr_courses_202410_descriptions.csv")

prompt = "Please generate a viable schedule for a computer science major assiming no courses were taken previously.\n\n"
prompt += "Don't be too verbose.\n\n"
#prompt += "Here are the course descriptions for the University of California, Riverside (UCR) for the Winter 2024 term:\n\n"

#for _, row in course_desciptions.head().iterrows():
#    prompt += f"{row['subject']} {row['courseNumber']} - {row['courseTitle']}: {row['description']}\n\n"

model = genai.GenerativeModel(model_name="gemini-1.5-flash")
response = model.generate_content(prompt)
print(response.text)