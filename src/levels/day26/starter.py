# Day 26: You're given stock, a dict of part -> how many we have
from flask import Flask

app = Flask(__name__)

# 1. home page


# 2. about page


# 3. stock page


client = app.test_client()
print(client.get("/").text)
