import google.generativeai as genai

client = genai.Client() # if not through enviroment (api_key="api")

response = client.models.generate_content(
    model="gemini-2.0-flash-lite",
    contents="how many golf courses are there in washington?"
)

print(response.text)