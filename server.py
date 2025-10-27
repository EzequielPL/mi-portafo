from flask import Flask, render_template, request, redirect, url_for
import requests
import csv
from bs4 import BeautifulSoup


app = Flask(__name__)


def sort_stories_by_votes(hnlist):
    return sorted(hnlist, key=lambda k: k["votes"], reverse=True)


def get_noticias():
    page = 1
    hn = []

    for page in range(1, 3):

        url = f"https://news.ycombinator.com/news?p={page}"
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        page += 1

        for item in soup.select(".athing"):
            title_tag = item.select_one(".titleline a")
            title = title_tag.getText()
            href = title_tag.get("href")

            if not href or href == "#":
                continue
            if not href.startswith("http"):
                href = f"https://news.ycombinator.com/{href.lstrip('/')}"

            next_row = item.find_next_sibling("tr")
            score_tag = next_row.select_one(".score")

            if score_tag:
                points = int(score_tag.getText().replace(" points", ""))
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
    comments = load_comments()
    return render_template("single.html", posts=posts, comments=comments)


# def write_to_file(data):
#     with open(
#         r"E:\Mis Proyectos Web\database.txt", mode="a", encoding="utf8"
#     ) as database:
#         email = data["email"]
#         subject = data["subject"]
#         message = data["message"]
#         file = database.write(f"\n{email}, {subject}, {message}")
#     return file


def write_to_csv(data):
    with open("/database.csv", mode="a", encoding="utf8", newline="") as database2:
        email = data["email"]
        subject = data["subject"]
        message = data["message"]
        csv_writer = csv.writer(database2, delimiter=",", quotechar="|", quoting=1)
        csv_writer.writerow([email, subject, message])


@app.route("/submit_form", methods=["POST", "GET"])
def submit_form():
    if request.method == "POST":
        data = request.form.to_dict()
        write_to_csv(data)
        return redirect("/gracias.html")
    else:
        return "Algo salio mal..."


def save_comments(name, message):
    with open("comentarios.csv", mode="a", encoding="utf8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([name, message])


@app.route("/enviar_comentario", methods=["POST"])
def enviar_comentario():
    name = request.form.get("name")
    message = request.form.get("message")
    save_comments(name, message)
    return redirect(url_for("blog"))


def load_comments():
    comments = []
    try:
        with open("comentarios.csv", mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 2:
                    comments.append({"name": row[0], "message": row[1]})
    except FileNotFoundError:
        pass
    return comments
