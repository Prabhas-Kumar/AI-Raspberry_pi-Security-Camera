import cv2
import sys
from mail import sendEmail
from flask import Flask, render_template, Response
from camera import VideoCamera
from flask_basicauth import BasicAuth
import time
import threading

email_update_interval = 600 # sends an email only once in this time interval (600 = 10 min./600 sec. )
video_camera = VideoCamera(flip=True) # creates a camera object, flip vertically

# An opencv classifier
object_classifier = cv2.CascadeClassifier("models/fullbody_recognition_model.xml") # you may also choose following casifiers : -   
# 1> For facial detection, use this link ["models/facial_recognition_model.xml"] instead of above link 
# 2> For upperbody classification use this link ["models/upperbody_recognition_model.xml"]  instead of above link 

# App Globals (not to be edit)
app = Flask(__name__)
app.config['BASIC_AUTH_USERNAME'] = 'CHANGE_ME_USERNAME'
app.config['BASIC_AUTH_PASSWORD'] = 'CHANGE_ME_PLEASE'
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)
last_epoch = 0

def check_for_objects():
	global last_epoch
	while True:
		try:
			frame, found_obj = video_camera.get_object(object_classifier)
			if found_obj and (time.time() - last_epoch) > email_update_interval:
				last_epoch = time.time()
				print "Sending email..."
				sendEmail(frame)
				print "done!"
		except:
			print "Error sending email: ", sys.exc_info()[0]

@app.route('/')
@basic_auth.required
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(video_camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    t = threading.Thread(target=check_for_objects, args=())
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', debug=False)
