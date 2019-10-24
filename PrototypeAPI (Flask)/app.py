from flask import Flask, render_template, request
import json, showData
import requests

url = "https://api.yelp.com/v3/businesses/search"

headers = {
    'Authorization': "Bearer -cfARevVogWB6vNqwyLZ7LrnAxyKNxj6T709QFGQSuDY-vxux_UMivRXpni_XQTMW4GxZPU1XNYVZ5fPJnIfUMEIGAXF8IMpEsXlVjLrkpRfGqoR3G56Dp-MRsypXXYx",
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

@app.route('/')
def index():
  return render_template("apiproto.html")

@app.route('/yelp', methods=["GET", "POST"])
def yelp():
  if request.method == "POST":
    city = request.form["city"]
    querystring = {"location": city}
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)
    dataList = []
    for restaurant in data['businesses']:
      dataList.append({"Name":restaurant["name"], "Rating":restaurant["rating"]})
    dataTable = showData.DataTable(dataList)
    return render_template("apiproto.html", yData = dataTable.getHTML())

if __name__ == '__main__':
  app.debug = True
  app.run()
