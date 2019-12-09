from flask import Flask, render_template, request
import json, showData
import requests
from . import config

#API Endpoint
url = "https://api.yelp.com/v3/businesses/search"

#Postman generated headers
headers = {
    'Authorization': "Bearer " + config.YELP_KEY,
    'User-Agent': "PostmanRuntime/7.18.0",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Postman-Token': "f8b0070f-8c9e-41c1-a089-302c63f00d38,5851f57a-66a4-4abd-b779-ebdd71f221b9",
    'Host': "api.yelp.com",
    'Accept-Encoding': "gzip, deflate",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }

app = Flask(__name__)

#Home page
@app.route('/')
def index():
  return render_template("apiproto.html")

#Called on submit button from home page
@app.route('/yelp', methods=["GET", "POST"])
def yelp():
  if request.method == "POST":
      try:
        city = request.form["city"]
        querystring = {"location": city, "limit": "50"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        data = json.loads(response.text)
        dataList = []
        for restaurant in data["businesses"]:
            if "price" in restaurant:
                dataList.append({"Name":restaurant["name"],
                                 "Rating":restaurant["rating"],
                                 "Price":restaurant["price"]})
        dataTable = showData.DataTable(dataList)
        return render_template("apiproto.html", table = dataTable.getHTML())
      except:
        return render_template("apiproto.html")

if __name__ == '__main__':
  app.debug = True
  app.run()
