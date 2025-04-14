from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    emails = summarize_emails(main())
    return render_template('index.html', emails=emails)

if __name__ == '__main__':
   app.run(debug=True)