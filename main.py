from flask import Flask, render_template, request, redirect
import psycopg
from dotenv import dotenv_values as dv
from psycopg.connection import Connection
from psycopg.errors import InFailedSqlTransaction
from psycopg.rows import TupleRow
from werkzeug.wrappers.response import Response


c: dict = dv(".env")  # loads env file
PORT: int = c["SPORT"]
app: Flask = Flask(__name__)

# connect to postgres database
conn: Connection[TupleRow] = psycopg.connect(
    dbname=c["DATABASE"],
    user=c["USER"],
    password=c["PASSWORD"],
    host=c["HOST"],
    port=c["PORT"],
)


def xcode(id: int) -> str:
    characters: str = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base: int = len(characters)
    ret_val: list[str] = []
    while id > 0:
        val: int = id % base
        ret_val.append(characters[val])
        id = id // base
    return "".join(ret_val[::-1])


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/api/new", methods=["POST", "GET"])
def url_short() -> Response | str:

    if request.method == "POST":
        u: str = request.form["long_url"]
        _: str = xcode(len(u) * 10000)

        try:
            with conn.cursor() as c:
                c.execute(
                    "INSERT INTO urls (name,long_url, short_url) VALUES(%s, %s, %s)",
                    ("config_err", u, _),
                )
                conn.commit()
            conn.close()
            print(f"localhost/{_}")
            return render_template("index.html")

        except InFailedSqlTransaction:
            print("transaction error")
            return redirect("/")

    else:
        return render_template("index.html")


if __name__ == "__main__":
    app.run(c["HOST"], PORT, debug=True)
