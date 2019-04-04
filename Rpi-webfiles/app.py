#!/opt/miniconda3/bin/python	
from flask import *
from flask_mail import *
import os
import Crawler
import cv2
import time
import requests
from serial import Serial, SerialException

try:	
	import Distance

except Exception as e:
	print("Server can't' run because {}".format(e))

port = "/dev/ttyACM0"
arduino = None
_NoArduino = False
mail = Mail()
app = Flask(__name__)
app.config.from_pyfile('config.cfg')
mail.init_app(app)
_ischecked = False
face_cascade = cv2.CascadeClassifier('/home/pi/workspace/libs/haarcascade_frontalface_alt2.xml')
user = False
_isError = False
password = "root_administrator"
users = ''
_ErrorCameraMessage = ""
_ErrorTimes = 0
frame = None
_isReturn = False


def connect_arduino():
	global arduino, _NoArduino
	try:
		arduino = Serial(port, 9600)
	except (OSError, SerialException):
		_NoArduino = True
		print("The arduino port is invalid. Try another port")


def frame_image(cap):
	global _ischecked, face_cascade, _isError, _ErrorCameraMessage, frame
	last_time = 0
	while True:
		try:
			_, frame = cap.read()
			frame.copy()
		except AttributeError:
			_isError = True
			_ErrorCameraMessage = "CAMERA_CONNECTION_ERROR"
			break

		image = frame.copy()

		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		try:
			rects = face_cascade.detectMultiScale(gray, minSize=(150, 150))
		except Exception:
			cap.release()
			_isError = True
			_ErrorCameraMessage = "FACE_LIBRARY_NOT_FOUND"
			break

		for(x, y, w, h) in rects:
			cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
		
			if last_time == 0:
				if len(rects) >= 1:
					last_time = time.time()
					print("finding")

				else:
					last_time = 0

			elif time.time() - last_time > 3:
				cap.release()
				image = frame[y:y+h, x:x+w]
				cv2.imwrite("/home/pi/workspace/Rpi-app/Rpi-webfiles/static/temp.jpg", image)
				_ischecked = True
				try:
					send_image()

				except Exception as e:
					print(e)
				break

		_, jpg = cv2.imencode('.jpg', image)
		yield(b'--frame\r\n'
			  b'Content-Type: image/jpeg\r\n\r\n' + jpg.tobytes() +
			  b'\r\n\r\n')


def send_image():
	global users
	s = Crawler.html("http://kinda.ktrackmp.com/rpi")
	_ip = Crawler.find(s, "<span id='Walker'>", "</span>")
	URL = "http://" + _ip + ":4000"
	files = {'media': open("/home/pi/workspace/Rpi-app/Rpi-webfiles/static/temp.jpg", "rb")}
	try:
		req = requests.post(URL, files=files)
		users = req.text
		print(users)
	except requests.exceptions.ConnectionError:
		print("Little error")


@app.route("/")
def index():
	global _ErrorTimes, users
	users = ""
	_ErrorTimes = 0
	connect_arduino()
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


@app.route("/ultrasonic_distance", methods=["GET", "POST"])
def ultrasonic_distance():
	data = {}
	Distance.setup(27, 17)
	data['distance'] = Distance.ping_cm()
	return jsonify(data)


@app.route("/send_error")
def send_error():
	global _ErrorCameraMessage
	topic = "Camera failed"
	msg = Message(topic, sender="root48960@gmail.com ", recipients=["chiioleong519@gmail.com"])
	msg.html = "<h1>The camera of the basketball machine has failed, please come and fix it</h1><br>Error code: " + _ErrorCameraMessage
	mail.send(msg)
	return render_template("error_send.html"), "message sent"


@app.route("/return_success")
def return_success():
	return render_template("return_ball_success.html")


@app.route("/camera_is_empty")
def camera_is_empty():
	global _ErrorCameraMessage, _ErrorTimes
	_ErrorTimes += 1
	return render_template("empty.html", errormessage=_ErrorCameraMessage, ErrorTimes=_ErrorTimes)


@app.route("/camera_recognition")
def camera_recognition():
	global _ischecked, _isError
	_ischecked = False
	_isError = False
	return render_template("recognition.html")


@app.route("/welcome")
def welcome():
	global users, arduino, _NoArduino
	if not _NoArduino:
		try:
			arduino.flush()
			arduino.write(b"2")
			arduino.write(b"1")
			_NoArduino = False
			return render_template("borrow_success.html")
		except Exception:
			return render_template("empty.html")
	else:
		return render_template("empty.html")


@app.route("/video_feed")
def video_feed():
	cap = cv2.VideoCapture(0)
	return Response(frame_image(cap), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/success", methods=["GET", "POST"])
def success():
	data = {}
	data["check"] = _ischecked
	return jsonify(data)


@app.route('/username', methods=['POST', 'GET'])
def username():
	global users
	data = {}
	data['user'] = users
	return jsonify(data)


@app.route("/recognize_image", methods=['POST', 'GET'])
def recognize_image():
	return render_template("processings_face.html")


@app.route("/Server_ip", methods=["POST", "GET"])
def Server_ip():
	data = {}
	s = Crawler.html("http://kinda.ktrackmp.com/rpi")
	data['ip'] = Crawler.find(s, "<span id='Walker'>", "</span>")
	return jsonify(data)


@app.route("/password_get", methods=["POST", "GET"])
def password_get():
	data = {}
	user_password = request.form["user_password"]
	if user_password == password:
		data["situation"] = True
	else:
		data["situation"] = False
	return jsonify(data)


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
	global users
	return render_template("borrow_success.html")


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
	try:
		app.run(host="0.0.0.0", port=8540, debug=True)
	except OSError as e:
		print("failed to open because {}".format(e))
