#!/usr/bin/python3
# -*-coding: utf-8-*-
# file: app.py

from flask import *
from flask_mail import *
import os
import Crawler
import cv2
import time
import requests
from serial import Serial, SerialException
from flask_cors import CORS

try:	
    from . import Distance

except Exception as e:
    print("Distance libray was not found. Please check if 'Distance.py' is here")

port = "/dev/ttyACM"
arduino = None
_NoArduino = False
mail = Mail()
app = Flask(__name__)
app.config.from_pyfile('config.cfg')
mail.init_app(app)
_ischecked = False
face_cascade = cv2.CascadeClassifier('./lib/haarcascade_frontalface_alt2.xml')
user = False
_isError = False
password = "root_administrator"
users = 'unknown'
_ErrorCameraMessage = ""
cam = None
_ErrorTimes = 0
frame = None
_isReturn = False
ret = True
image = None
rects = None
new_username = ""


def connect_arduino():
    global arduino, _NoArduino, port
    for i in range(5):
        port = "/dev/ttyACM"
        try:
            port = port + str(i)
            print(port)
            arduino = Serial(port, 9600)
            print(arduino)
            _NoArduino = False
            break
        except (OSError, SerialException) as e:
            print(e)
            print("The arduino port is invalid. Try another port")
            _NoArduino = True


def frame_image(cap):
    global _ischecked, face_cascade, _isError, _ErrorCameraMessage, frame, ret, image, cam
    last_time = 0
    image = None
    while True:
        try:
            ret, frame = cap.read()
            frame.copy()
    
        except Exception as e:
            cam = None
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

        for (x, y, w, h) in rects:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            if last_time == 0:
                if len(rects) >= 1:
                    last_time = time.time()
                    print("finding")

                else:
                    last_time = 0

            elif time.time() - last_time > 3:
                image = frame[y:y + h, x:x + w]
                cv2.imwrite("./static/temp.jpg", image)
                _ischecked = True
                try:
                    send_image("/")

                except Exception as e:
                    print(e)
                break
    
        _, jpg = cv2.imencode('.jpg', image)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpg.tobytes() +
               b'\r\n\r\n')
        

def get_images(cap):
    global frame, face_cascade, image, rects, cam, _isError, _ErrorCameraMessage
    image = None
    last_time = time.time()
    while True:
        try:
            ret, frame = cap.read()
            frame.copy()
    
        except Exception as e:
            cam = None
            _isError = True
            _ErrorCameraMessage = "FACE_LIBRARY_NOT_FOUND"
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

        for (x, y, w, h) in rects:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            if time.time() - last_time >= 2:
                print("sending_image")
                image = image[y:y + h, x:x + w].copy()
                cv2.imwrite("./static/temp.jpg", image)
                send_image("/collect_data")
                last_time = time.time()
            
        _, jpg = cv2.imencode('.jpg', image)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpg.tobytes() +
               b'\r\n\r\n')


def send_image(page):
    global users
    # s = Crawler.html("http://kinda.ktrackmp.com/rpi")
    # _ip = Crawler.find(s, "<span id='Walker-TUF-Gaming-FX505GM'>", "</span>")
    _ip = "localhost"
    URL = "http://" + _ip + ":4000" + page
    files = {'media': open("./static/temp.jpg", "rb")}
    print(URL)
    try:
        req = requests.post(URL, files=files)
        users = req.text
        print(users)
    except requests.exceptions.ConnectionError:
        print("Little error")
        

@app.route("/")
def index():
    global _ErrorTimes, users, _ischecked, _ErrorCameraMessage
    users = "unknown"
    _ErrorTimes = 0
    _ischecked = False
    _ErrorCameraMessage = ""
    connect_arduino()
    return render_template("index.html")


@app.route("/return_ball")
def return_ball():
    global users, arduino
    try:
        arduino.flush()
        arduino.write(b"2")
    except UnicodeDecodeError:
        print("Unknown signal get")
    return render_template("return_ball.html", username=users)


@app.route("/Server_not_responsing")
def Server_not_responsing():
    global _ErrorCameraMessage
    _ErrorCameraMessage = "SERVER_NO_RESPONSE"
    return render_template("Server_no_response.html")


@app.route("/get_weather")
def get_weather():
    data = {}
    # html = Crawler.html("https://www.gov.mo/zh-hant/about-macau-sar/weather/current/")

    # section = Crawler.find(html, '<section id="weather-brief">', '</section>')
    # block1 = Crawler.find(section, '<div class="col-sm-4 content-block">', '</div>', 0)
    # block2 = Crawler.find(section, '<div class="col-sm-4 content-block">', '</div>', 1)
    
    data['temp'] = "28C"
    data['type'] = "晴天"
    data['rain'] = "--"
    return jsonify(data)


@app.route("/cv2_empty")
def cv2_empty():
    data = {}
    global _isError
    data["empty"] = _isError
    return jsonify(data)


@app.route("/ultrasonic_distance", methods=["GET", "POST"])
def ultrasonic_distance():
    global arduino
    data = {}
    distance = arduino.readline().decode("ASCII").replace("\r", "").replace("\n", "")
    if not distance == "":
        data['distance'] = distance
        print(data)
        return jsonify(data)
    data['distance'] = "2000"
    print(data)
    return jsonify(data)


@app.route("/send_error")
def send_error():
    global _ErrorCameraMessage
    topic = "Camera failed"
    msg = Message(topic, sender="root48960@gmail.com ", recipients=["chiioleong519@gmail.com"])
    msg.html = "<h1>The basketball machine's system has failed, please come and fix it</h1><br>Error code: " + _ErrorCameraMessage
    mail.send(msg)
    return render_template("error_send.html"), "message sent"


@app.route("/return_success")
def return_success():
    global arduino
    arduino.flush()
    arduino.write(b"3")
    return render_template("return_ball_success.html")


@app.route('/return_status_setter', methods=["POST", "GET"])
def return_status():
    global _isReturn
    data = {}
    _isReturn = request.form["val"]
    data['status'] = _isReturn
    return jsonify(data)


@app.route("/return_status_getter", methods=["POST", "GET"])
def return_status_getter():
    global _isReturn
    data = {}
    data['status'] = _isReturn
    return jsonify(data)


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
    global users, arduino, _NoArduino, _ErrorCameraMessage
    print(_NoArduino)
    if not _NoArduino:
        try:
            print("Writing signal...")
            arduino.flush()
            print(arduino.write(b"1"))
            print("Writing signal complete")
            _NoArduino = False
            return render_template("borrow_success.html")
        except Exception as e:
            print(e)
            _ErrorCameraMessage = "ARDUINO_CONNECTION_ERROR"
            return render_template("empty.html")
    else:
        _ErrorCameraMessage = "NO_ARDUINO_ERROR"
        return render_template("empty.html")


@app.route("/video_feed")
def video_feed():
    global cam
    print(cam)
    if cam is None:
        cam = cv2.VideoCapture(0)
    return Response(frame_image(cam), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/sign_up_feed")
def sign_up_feed():
    global cam
    if cam is None:
        cam = cv2.VideoCapture(0)
    
    return Response(get_images(cam), mimetype='multipart/x-mixed-replace; boundary=frame')


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
    # s = Crawler.html("http://kinda.ktrackmp.com/rpi")
    data['ip'] = "localhost"  # Crawler.find(s, "<span id='Walker'>", "</span>")
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


@app.route("/test")
def test():
    return render_template("test.html")


@app.route("/access")
def access():
    return render_template("settings.html")


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


@app.route("/get_username_setter", methods=['POST', 'GET'])
def get_username_setter():
    global new_username
    new_username = request.form['new_user']
    data = {}
    # s = Crawler.html("http://kinda.ktrackmp.com/rpi")
    _ip = "localhost"  # Crawler.find(s, "<span id='Walker-TUF-Gaming-FX505GM'>", "</span>")
    URL = "http://" + _ip + ":4000/request_new_user"
    print(URL)
    data['new_user'] = new_username
    requests.post(URL, data=data)
    return jsonify(data)


@app.route("/sign_up", methods=['POST', 'GET'])
def sign_up():
    return render_template("Sign_up.html")


@app.route("/Loading_new_user")
def Loading_new_user():
    return render_template("processing_new_user.html")


@app.route("/Loading_new_user_status", methods=['POST', 'GET'])
def Loading_new_user_status():
    data = {}
    # s = Crawler.html("http://kinda.ktrackmp.com/rpi")
    _ip = "localhost"  # Crawler.find(s, "<span id='Walker-TUF-Gaming-FX505GM'>", "</span>")
    URL = "http://" + _ip + ":4000/start_adding_user"
    data['loading_status'] = requests.get(URL, data={}).text
    print(data)
    return jsonify(data)


@app.route("/Add_success", methods=['POST', 'GET'])
def Add_success():
    return render_template("Add_new_user_success.html")


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
        CORS(app)
    except Exception as e:
        print("failed to open because {}".format(e))
