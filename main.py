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
try:
    conn: Connection[TupleRow] = psycopg.connect(
        dbname=c["DATABASE"],
        user=c["USER"],
        password=c["PASSWORD"],
        host=c["HOST"],
        port=c["PORT"],
    )
except psycopg.OperationalError:
    print('DB server not started !!! please start DB server')

def xcode(id: int) -> str:
    characters: str = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base: int = len(characters)
    ret_val: list[str] = []
    while id > 0:
        val: int = id % base
        ret_val.append(characters[val])
        id = id // base
    return "".join(ret_val[::-1])


@app.route("/", methods=["POST", "GET"])
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
            
            print(f"localhost/{_}")
            return render_template("index.html", short_url=_)

        except InFailedSqlTransaction:
            print("transaction error")
            return redirect("/")

    else:
        return render_template("index.html")


@app.get('/<url>')
def decode(url) -> Response | str:
    try:
        with conn.cursor() as c:
            c.execute("SELECT * FROM urls WHERE short_url = %s", [url])
            d = c.fetchone()
            conn.commit()
        return redirect(d[2])
    except TypeError:
        print('no urls has been processed')
        return render_template('index.html')

if __name__ == "__main__":
    app.run(c["HOST"], PORT, debug=True)
