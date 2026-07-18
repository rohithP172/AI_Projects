from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def helloWorldWelcome():
    # return "Hello, World! Welcome to the Artificial Intelligence and Human Computer Interaction Course."
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
