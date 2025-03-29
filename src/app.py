from flask import Flask
from helper import get_env_variable

app = Flask(__name__)

app.config['WTF_CSRF_ENABLED'] = False
app.secret_key = "your_secret_key"

# register blueprints here...

@app.route("/")
def home():
  return(get_env_variable("TEST_MESSAGE"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
