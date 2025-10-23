from flask import Flask, render_template, request, redirect
import requests
import csv

from bs4 import BeautifulSoup


app = Flask(__name__)


def sort_stories_by_votes(hnlist):
    return sorted(hnlist, key=lambda k: k["votes"], reverse=True)


def get_noticias():
    page = 1
    hn = []
    for page in range(4):
        url = f"https://news.ycombinator.com/news?p={page}"
        response = requests.get(url, timeout=1)
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.select(".titleline")
        subtext = soup.select(".subtext")
        page += 1
        for idx, item in enumerate(links):

            title = links[idx].getText()
            href = links[idx].get("href", None)
            vote = subtext[idx].select(".score")
            if len(vote):
                points = int(vote[0].getText().replace(" points", ""))
                if points > 99:
                    hn.append({"title": title, "link": href, "votes": points})
    return sort_stories_by_votes(hn)


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/<string:page_name>")
def main_page(page_name):
    return render_template(page_name)


@app.route("/single.html")
def blog():
    posts = get_noticias()
    return render_template("single.html", posts=posts)


def write_to_file(data):
    with open(
        r"E:\Mis Proyectos Web\database.txt", mode="a", encoding="utf8"
    ) as database:
        email = data["email"]
        subject = data["subject"]
        message = data["message"]
        file = database.write(f"\n{email}, {subject}, {message}")
    return file


def write_to_csv(data):
    with open(
        r"E:\Mis Proyectos Web\database.csv", mode="a", encoding="utf8"
    ) as database2:
        email = data["email"]
        subject = data["subject"]
        message = data["message"]
        csv_writer = csv.writer(
            database2, delimiter=",", newline="", quotechar="|", quoting=1
        )
        csv_writer.writerow([email, subject, message])


@app.route("/submit_form", methods=["POST", "GET"])
def submit_form():
    if request.method == "POST":
        data = request.form.to_dict()
        write_to_csv(data)
        return redirect("/gracias.html")
    else:
        return "Algo salio mal..."
