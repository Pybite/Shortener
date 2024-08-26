from flask import Flask, render_template, request, redirect


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/new', methods=['POST', 'GET'])
def url_short():
    if request.method == 'POST':
        url = request.form
        print(url['long_url'])
        return redirect('/', code=200)

    else:
        return render_template('index.html')
    

if __name__ == '__main__':
    app.run('localhost', 5000, debug=True)