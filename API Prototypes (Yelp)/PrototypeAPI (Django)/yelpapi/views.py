from django.shortcuts import render
from django.http import HttpResponse
from . import showData, config
import requests, json

url = "https://api.yelp.com/v3/businesses/search"

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


def yelpform(request):
    return render(request, 'yelpapi/yelpform.html')

def yelpsearch(request):
    if request.method == "POST":
        try:
            city = request.POST.get("city")
            querystring = {"location": city, "limit": "50"}
            response = requests.request("GET", url, headers=headers, params=querystring)
            data = json.loads(response.text)
            dataList = []
            for restaurant in data['businesses']:
              if 'price' in restaurant:
                  dataList.append({"name":restaurant["name"],
                                   "rating":restaurant["rating"],
                                   "price":restaurant["price"]})
            table = showData.genTable(request, dataList)
            context = {'table': table}
            return render(request, 'yelpapi/yelpform.html', context)
        except:
            return render(request, 'yelpapi/yelpform.html')
