from flask import Flask, render_template, request
import calendar, datetime, json, showData
import requests

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('week.html')

@app.route('/weekselect', methods=["GET", "POST"])
def weekselect():
  if request.method == "POST":
    start = request.form["start"]
    end = request.form["end"]
    print(start)
    print(end)
    return render_template("personal.html")

@app.route('/personal', methods=["GET", "POST"])
def personal():
  if request.method == "POST":
    location = request.form["location"]
    cuisine = request.form.get("cuisine")
    price = request.form.get("price")
    restrictions = request.form.getlist("restriction")
    print(location)
    print(cuisine)
    print(price)
    print(restrictions)
    return render_template("session.html")


if __name__ == '__main__':
  app.debug = True
  app.run()
