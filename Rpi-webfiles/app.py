from flask import *
import os
import Crawler
import cv2
import time
import requests

app = Flask(__name__)
_ischecked = False
face_cascade = cv2.CascadeClassifier('../../libs/haarcascade_frontalface_default.xml')


def frame(cap):
	global _ischecked, face_cascade
	last_time = 0
	while True:
		_, frame = cap.read()
		image = frame.copy()
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		rects = face_cascade.detectMultiScale(gray, minSize=(150, 150))
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
			break

		_, jpg = cv2.imencode('.jpg', image)
		yield(b'--frame\r\n'
			  b'Content-Type: image/jpeg\r\n\r\n' + jpg.tobytes() +
			  b'\r\n\r\n')
	cap.release()


def send_image():
	URL = "http://192.168.142.21:4000"
	files = {'media': open("/static/temp.jpg", "rb")}
	req = requests.post(URL, files=files)
	user = req.text



@app.route("/")
def index():
	return render_template("index.html")


@app.route("/get_weather")
def get_weather():
	data = {}
	s = Crawler.html('http://home.puiching.edu.mo/~pcama/')
	data['temp'] = Crawler.find(s, '<span class="temp">', '</span>')
	data['type'] = Crawler.find(s, '<span class="location">', '</span>')
	data['rain'] = Crawler.find(s, '<span class="rain">', '</span>')
	return jsonify(data)


@app.route("/camera_recognition")
def camera_recognition():
	global _ischecked
	_ischecked = False
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


@app.route("/recognize_image")
def recognize_image():
	return render_template("processings_face.html")


@app.route("/check_user")
def check_user():
	data = {}
	data["result"] = "1"
	return jsonify(data)



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
