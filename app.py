from flask import Flask
import views

app = Flask(__name__)


# urls
app.add_url_rule('/base', 'base', views.base)
app.add_url_rule('/', 'index', views.index)
app.add_url_rule('/faceapp', 'faceapp', views.faceapp)
app.add_url_rule('/face_recognition', 'face_recognition', views.face_recognition, methods=['GET', 'POST'])
app.add_url_rule('/management', 'management', views.management, methods=['GET', 'POST'])

# run
if __name__=='__main__':
	app.run(debug=True)
