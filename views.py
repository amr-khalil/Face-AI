from flask import render_template, redirect, request, url_for
import os
from PIL import Image
from api import detect_faces, detect_labels, get_img_metadata, add_face_to_collection,remove_face_from_collection
import random

UPLOAD_FOLDER = 'static/uploads/'

def base():
	return render_template("base.html")

def index():
	return render_template('index.html')

def faceapp():
	return render_template('faceapp.html')

def get_width(path):
	img = Image.open(path)
	aspect = img.size[0]/img.size[1]
	width = 300 * aspect
	return int(width)



def face_recognition():
	if request.method == 'POST':
		# read the uploaded file
		f = request.files['image']
		# take the file name
		filename = f.filename
		# create a path for the uploded file
		path = os.path.join(UPLOAD_FOLDER, filename)
		# save the uploaded file in the path
		f.save(path) 
		# processing
		w = get_width(path)
		#  detection
		faces = detect_faces(path, filename)
		labels = detect_labels(path)
		metadata = get_img_metadata(path)


		rand = random.randint(1,1000000000)


		return render_template('face_recognition.html', fileupload=True, img_name=filename, w=w, random=rand,
			faces=faces, labels=labels, metadata=metadata)
			#, Gender=Gender, Age_avg=Age_avg, Emotion=Emotion, Beard=Beard, Mustache=Mustache,
			#Eyeglasses=Eyeglasses, Sunglasses=Sunglasses, EyesOpen=EyesOpen, MouthOpen=MouthOpen, Smile=Smile)
	
	return render_template('face_recognition.html', fileupload=False)


def add_face():
	if request.method == 'POST':
		if request.form['submit'] == "submit_add":
			f = request.files['image']
			fname = request.form.get('fname')
			lname = request.form.get('lname')
			fname = fname.capitalize()
			lname = lname.capitalize()
			filename = f.filename
			path = os.path.join('./static/known_pepole', "{}_{}_{}".format(fname,lname,filename))
			f.save(path)
			add_face_to_collection(path,fname,lname)
			return render_template('add_face.html',face_add = True, fname=fname,face_remove=False, lname=lname)

		if request.form['submit'] == 'submit_remove':
			fname = request.form.get('fname')
			lname = request.form.get('lname')
			fname = fname.capitalize()
			lname = lname.capitalize()
			face_remove = remove_face_from_collection(fname, lname)
			return render_template('add_face.html',face_add = False,face_remove=face_remove, fname=fname, lname=lname)

	return render_template('add_face.html',face_add = False, face_remove=False)



