#!/opt/miniconda3/bin/python	
from flask import *
from flask_mail import *
import os
import Crawler
import cv2
import time
import requests

'''
	camera_recognition: 126
'''

mail = Mail()
app = Flask(__name__)
app.config.from_pyfile('config.cfg')
mail.init_app(app)
_ischecked = False
face_cascade = cv2.CascadeClassifier('../../libs/haarcascade_frontalface_default.xml')
user = False
_isError = False
password = "root_administrator"


def frame(cap):
	global _ischecked, face_cascade, _isError
	last_time = 0
	while True:
		_, frame = cap.read()
		try:
			frame.copy()
		except AttributeError as e:
			_isError = True
			break

		image = frame.copy()

		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		rects = []
		try:
			rects = face_cascade.detectMultiScale(gray, minSize=(150, 150))
		except Exception as e:
			cap.release()
			_isError = True
			break

		for(x, y, w, h) in rects:
			cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
		
		if last_time == 0:
			if len(rects) == 1:
				last_time = time.time()
				print("finding")
			
			else:
				last_time = 0
				
		elif time.time() - last_time > 3:
			cv2.imwrite("/home/pi/workspace/Rpi-app/Rpi-webfiles/static/temp.jpg", image)
			_ischecked = True
			send_image()
			break

		_, jpg = cv2.imencode('.jpg', image)
		yield(b'--frame\r\n'
			  b'Content-Type: image/jpeg\r\n\r\n' + jpg.tobytes() +
			  b'\r\n\r\n')
	cap.release()


def send_image():
	global user
	URL = "http://192.168.170.184:4000"
	files = {'media': open("/home/pi/workspace/Rpi-app/Rpi-webfiles/static/temp.jpg", "rb")}
	req = requests.post(URL, files=files)
	user = req.text


@app.route("/")
def index():
	return render_template("index.html")


@app.route("/return_ball")
def return_ball():
	return render_template("return_ball.html")


@app.route("/get_weather")
def get_weather():
	data = {}
	s = Crawler.html('http://home.puiching.edu.mo/~pcama/')
	data['temp'] = Crawler.find(s, '<span class="temp">', '</span>')
	data['type'] = Crawler.find(s, '<span class="location">', '</span>')
	data['rain'] = Crawler.find(s, '<span class="rain">', '</span>')
	data['last_update_time'] = Crawler.find(s, '<p id="reportUpdateTime">', '</p>')
	return jsonify(data)


@app.route("/cv2_empty")
def cv2_empty():
	data = {}
	global _isError
	data["empty"] = _isError
	return jsonify(data)


@app.route("/send_error")
def send_error():
	message = "The camera of the basketball machine has failed, please come and fix it"
	msg = Message(message, sender="root48960@gmail.com ", recipients=["chiioleong519@gmail.com"])
	mail.send(msg)
	return render_template("error_send.html"), "message sent"


@app.route("/return_success")
def return_success():
	return render_template("return_ball_success.html")


@app.route("/camera_is_empty")
def camera_is_empty():
	return render_template("empty.html")


@app.route("/camera_recognition")
def camera_recognition():
	global _ischecked, _isError
	_ischecked = False
	_isError = False
	return render_template("recognition.html")


@app.route("/welcome")
def welcome():
	return "welcome Thomas"


@app.route("/video_feed")
def video_feed():
	cap = cv2.VideoCapture(0)
	return Response(frame(cap), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/success", methods=["GET", "POST"])
def success():
	data = {}
	data["check"] = _ischecked
	return jsonify(data)


@app.route("/recognize_image", methods=['POST', 'GET'])
def recognize_image():
	return render_template("processings_face.html")


@app.route("/check_user")
def check_user():
	data = {}
	data["result"] = "1"
	return jsonify(data)


@app.route("/password_get", methods=["POST", "GET"])
def password_get():
	data = {}
	user_password = request.form["user_password"]
	if user_password == password:
		data["situation"] = True
	else:
		data["situation"] = False
	print(user_password)
	return jsonify(data)


@app.route('/get_face_count')
def get_face_count():
	global user
	if user:
		return render_template("Success.html")


@app.route("/access")
def access():
	return render_template("access.html")


@app.route("/denied")
def denied():
	return render_template("denied.html")


@app.route("/no_forgot_password")
def no_forgot_password():
	return render_template("forgot_password.html")


@app.route("/borrow_success")
def borrow_success():
	return render_template("Success.html")


@app.route("/enter_admin_password")
def enter_admin_password():
	return render_template("enter_password.html")


@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
	return render_template("500.html"), 500


@app.context_processor
def override_url_for():
	return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
	if endpoint == 'static':
		filename = values.get('filename', None)
		if filename:
			file_path = os.path.join(app.root_path, endpoint, filename)
			values['q'] = int(os.stat(file_path).st_mtime)
	return url_for(endpoint, **values)
	
	
if __name__ == '__main__':
	app.run(host="0.0.0.0", port=8540, debug=True)
