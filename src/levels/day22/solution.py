# Day 22: Scrape ChipCo's price list
import requests
from bs4 import BeautifulSoup

resp = requests.get("https://chipco.example/gpus")
soup = BeautifulSoup(resp.text, "html.parser")

heading = soup.find("h1").text
rows = soup.find_all("tr", class_="chip")
prices = {row.find("td", class_="name").text: float(row.find("td", class_="price").text.replace("£", "")) for row in rows}
in_stock = [row.find("td", class_="name").text for row in rows if row.find("td", class_="stock").text == "In stock"]
cheapest = min(in_stock, key=lambda name: prices[name])

print(heading, "| cheapest in stock:", cheapest)
