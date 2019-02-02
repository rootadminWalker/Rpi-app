from flask import *
from flask_mail import *

mail = Mail()

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
mail.init_app(app)

@app.route("/")
def index():
    msg = Message("hello", sender="chiioleong519@gmail.com", recipients=["chiioleong519@gmail.com"])
    mail.send(msg)
    return "message sent"


app.run(port=8080, debug=True)
