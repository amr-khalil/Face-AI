import boto3
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont, ImageEnhance
import json
import boto3
import exifread
from geopy.geocoders import Nominatim
from datetime import datetime

# Cerditinal
from secret import access_key_id, secret_access_key
import os

# Client
client = boto3.client('rekognition', region_name='eu-central-1',
                      aws_access_key_id = access_key_id,
                      aws_secret_access_key = secret_access_key)


# Search Faces in my collection
# Give Photo path for the function to compare it with my collection
def search_in_collection(path):
    values = {}
    collectionId='MyCollection'
    threshold = 70
    maxFaces=100
    image_id = 'Unknown'
    
    try:
        # Convert image to binary
        with open(path, 'rb') as source_image:
            source_bytes = source_image.read()

        response=client.search_faces_by_image(CollectionId=collectionId,
                                    Image={'Bytes': source_bytes},
                                    FaceMatchThreshold=threshold,
                                    MaxFaces=maxFaces)

        faceMatches=response['FaceMatches']
        for match in faceMatches:
            image_id = str(match['Face']['ExternalImageId']).replace("_", " ")
            #face_id  = match['Face']['FaceId']
            #similarity = match['Similarity']
            #values[image_id] = (face_id,similarity)
                
    except:
        pass

    return image_id

# Recognize known-faces matches with my collection
# Compare the cropped photos with my collection
def recognize_known_faces():
    faces = []
    values = {}
    path = "./static/predict/faces"
    
    # open the faces folder
    for file in os.listdir(path):
        if file.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            faces.append(file)
   # loop on the all cropped faces
    for face in faces:
        # if a crooped face matches with my collection
        is_known = search_in_collection(path+"/"+face)
        if is_known:
            face_num = face[:face.rfind(".")] 
            values[is_known[0][0]] =  face_num
    # return the Name and Face Number
    # Output: [('Amr Khalil', '1')]
    return list(values.items())

# Recognize known-faces matches with my collection
def recognize_celebrities(path):
    values = {}
    try:
        with open(path, 'rb') as image:
            response = client.recognize_celebrities(Image={'Bytes': image.read()})
        for celebrity in response['CelebrityFaces']: 
            name = celebrity['Name']
            for url in celebrity['Urls']:
                values[celebrity['Name']] = url
    except:
        pass
    return list(values.items())



def detect_faces(path, filename):

    # Load image
    image=Image.open(path)

    # Convert image to binary
    with open(path, 'rb') as source_image:
        source_bytes = source_image.read()

    #Call DetectFaces 
    response = client.detect_faces( Image={ 'Bytes': source_bytes},Attributes=['ALL'])

    imgWidth, imgHeight = image.size  
    draw = ImageDraw.Draw(image)

    # font = ImageFont.truetype(<font-file>, <font-size>)
    text_size= int((imgHeight/imgWidth)*20)   
    font = ImageFont.truetype("fonts/arial.ttf", text_size)
    Count = "Count of Faces: 0"

    # Calculate and display bounding boxes for each detected face
    values = dict()       
    for face_num, faceDetail in enumerate(response['FaceDetails']):
        
        Count = "Count of Faces: "+str(len(response['FaceDetails']))
        Gender, Gender_c = faceDetail['Gender'].values()
        AgeRange, AgeRange_c = faceDetail['AgeRange'].values()
        Age_low = faceDetail['AgeRange']['Low']
        Age_high = int(faceDetail['AgeRange']['High'])
        Age_avg = int((Age_low + Age_high)/2)
        Emotion, Emotion_c = faceDetail['Emotions'][0].values()
        Beard, Beard_c  =   faceDetail['Beard'].values()
        Mustache, Mustache_c = faceDetail['Mustache'].values()
        Eyeglasses, Eyeglasses_c = faceDetail['Eyeglasses'].values()
        Sunglasses, Sunglasses_c = faceDetail['Sunglasses'].values()
        EyesOpen, EyesOpen_c = faceDetail['EyesOpen'].values()
        MouthOpen, MouthOpen_c = faceDetail['MouthOpen'].values()
        Smile, Smile_c = faceDetail['Smile'].values()
        

        box = faceDetail['BoundingBox']
        left = imgWidth * box['Left']
        top = imgHeight * box['Top']
        width = imgWidth * box['Width']
        height = imgHeight * box['Height']
       
        ##### Pull facecs ######
        #area = (left, top, right, lower)
        area = (left, top, left+width, top+height)
        cropped_img = image.crop(area)
        
        face_path = "./static/predict/faces/{}.jpg".format(face_num+1)
        cropped_img.save(face_path, quality=100, subsampling=0)

        
        # recognize known faces
        is_known = search_in_collection(face_path)
            
        ##### Pull facecs ######

        points = (
            (left,top),
            (left + width, top),
            (left + width, top + height),
            (left , top + height),
            (left, top)
        )

        color_set = ('#1bb7f4', '#ad1292')
        if Gender == 'Male':
            color = color_set[0]
        else:
            color = color_set[1]

        # Draw Box
        draw.line(points, fill=color, width=4)         
    
        # Write Text 
        draw = ImageDraw.Draw(image)
        
        # Text above box
        text = "Id {}".format(face_num+1)
        w, h = font.getsize(text)
        x, y = (left, top-h)
        draw.rectangle((x-2, y, x + w, y + h), fill=color)
        draw.text((x, y), text, fill= '#fff', font=font)

        # Text under box
        text = "{}".format(is_known)
        w, h = font.getsize(text)
        x, y = (left, top+height)
        draw.rectangle((x-2, y-2, x + w, y + h+3), fill=color)
        draw.text((x, y), text, fill= '#fff', font=font)


        text = "{}".format(Emotion.capitalize())
        w, h = font.getsize(text)
        x, y = (left, top+height+(h))
        draw.rectangle((x-2, y, x + w, y + h), fill=color)
        draw.text((x, y), text, fill= '#fff', font=font)
        #######
        values[face_num+1] =[(AgeRange, AgeRange_c), (Gender, int(Gender_c)),
                             (Emotion.capitalize(), int(Emotion_c)), 
                             (Beard, int(Beard_c)), (Mustache, int(Mustache_c)),
                             (Eyeglasses, int(Eyeglasses_c)),(Sunglasses, int(Sunglasses_c)),
                             (EyesOpen, int(EyesOpen_c)), (MouthOpen, int(MouthOpen_c)),
                             (Smile, int(Smile_c)), is_known]
    
        
    w, h = font.getsize(Count)
    x, y = (2,2)
    draw.rectangle((x, y, x + w+3, y + h+3), fill='#fff')
    draw.text((x,y), Count, fill= '#000', font=font)
    
   
    image.save("./static/predict/{}".format(filename), quality=100, subsampling=0)
    return list(values.items())



def detect_labels(path):
    values = {}
    with open(path, 'rb') as image:
        response = client.detect_labels(Image={'Bytes': image.read()})

    for label in response['Labels']:
        values[label['Name']] = int(label['Confidence'])
        
    return list(values.items())



def get_img_metadata(path):
    values = {}

    # convert lat. and lang. dgree minute second 
    def format_lati_long(data):#list2float
        list_tmp=str(data).replace('[', '').replace(']', '').split(',')
        list=[ele.strip() for ele in list_tmp]
        data_sec = int(list[-1].split('/')[0]) /(int(list[-1].split('/')[1])*3600)# Second value
        data_minute = int(list[1])/60
        data_degree = int(list[0])
        result=data_degree + data_minute + data_sec
        return result
    
    # read meta data
    img=exifread.process_file(open(path,'rb'))
    for i in img:
        # latitude
        if i == 'GPS GPSLatitude':
            latitude=format_lati_long(str(img['GPS GPSLatitude']))
            # longitude
            longitude=format_lati_long(str(img['GPS GPSLongitude']))
            # location
            loc = "{},{}".format(latitude,longitude)
            geolocator = Nominatim(user_agent="faceai")
            location = geolocator.reverse(loc)
            values['Location'] = location[0]
        # device
        if i == 'Image Make':
            device = str(img['Image Make'])
            values['Device'] = device
        # model
        if i == 'Image Model':
            model = str(img['Image Model'])
            values['Model'] = model
        # software
        if i == 'Image Software':
            software = str(img['Image Software'])
            values['Software'] = software
        # date_time
        if i == 'Image DateTime':
            date_time = str(img['Image DateTime'])
            # get date and time
            def get_date_time(date_time_str):
                date_time_obj = datetime.strptime(date_time, '%Y:%m:%d %H:%M:%S')
                date = date_time_obj.strftime("%d/%m/%Y")
                time = date_time_obj.strftime("%H:%M")
                return date, time
            # Extract date and time
            date, time = get_date_time(date_time)
            values['Date'] = date
            values['Time'] = time
     
    return values.items()


def add_face_to_collection(path, fname, lname, group):
    
    fname = fname.capitalize()
    lname = lname.capitalize()
    group = group.capitalize()
    image_id = "{}_{}_{}".format(fname, lname, group)
    collectionId='MyCollection'
   
    with open(path, 'rb') as source_image:
                source_bytes = source_image.read()

    response=client.index_faces(CollectionId=collectionId,
                                Image={'Bytes': source_bytes},
                                ExternalImageId=image_id,
                                MaxFaces=1,
                                QualityFilter="AUTO",
                                DetectionAttributes=['ALL'])


def remove_face_from_collection(img_id):
    value = False
    def list_faces_in_collection():
        values = {}
        collectionId='MyCollection'
        maxResults=1000
        response=client.list_faces(CollectionId=collectionId,
                                   MaxResults=maxResults)
        for face in response['Faces']:
            values[face['ExternalImageId']] = face['FaceId']
        return values
    value = False
    face_id_list=[]
    
    collectionId = 'MyCollection'
    
    name = img_id
    
    face_dict = list_faces_in_collection()
    if name in face_dict.keys():
        value =True
        face_id = face_dict[name]
        face_id_list.append(face_id)
        response=client.delete_faces(CollectionId=collectionId,
                               FaceIds=face_id_list)
        
        print(str(len(response['DeletedFaces'])) + ' faces deleted:')
        for face_id in response['DeletedFaces']:
             print (name, face_id)
            
    return value

def show_known_people():
    values = {}
    folder_path = './static/known_people'

    for img_path in os.listdir(folder_path):
        if img_path.endswith('.jpg'):
            img_id = img_path.split('.')
            img_id = img_id[0]
            img_id = img_id.split("_")
            name = "{} {}".format(img_id[0], img_id[1])
            group = img_id[2]
            values[img_path] = (name, group)
    return list(values.items())


def is_one_face(path):
    one_face = False
    # Load image
    image=Image.open(path)

    # Convert image to binary
    with open(path, 'rb') as source_image:
        source_bytes = source_image.read()

    #Call DetectFaces 
    response = client.detect_faces( Image={ 'Bytes': source_bytes},Attributes=['ALL'])
    count = len(response['FaceDetails'])
    if count == 1:
        one_face = True
    return one_face



