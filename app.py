import os
import uuid
from dotenv import load_dotenv
from flask import Flask, render_template,session, request, jsonify,make_response,redirect,url_for
from pymongo import MongoClient
from argon2 import PasswordHasher
import boto3
from botocore.config import Config
import json
import base64

ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# load environment variable
load_dotenv()
# flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
# mongodb

MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
print('MongodbClient: ',client)
db = client['team-intro-app']
member_col = db.member

aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
# boto3

lambda_clinet = boto3.client('lambda',
                             region_name = 'ap-northeast-2',
                             aws_access_key_id = aws_access_key_id,
                             aws_secret_access_key = aws_secret_access_key
                             )

# argon2
ph = PasswordHasher()

##### flask app #####

## HOME Page
@app.route('/')
def home_page():
    return render_template('index.html')

## Create Page
@app.route('/manage/create')
def create_page():
    return render_template('create.html')

## Update Page
@app.route('/manage/update/<string:id>')
def update_page(id):
    try:
      member = member_col.find_one({'id':str(id)}, {'_id': False})
      if(member is None):
        return redirect(url_for('home_page'))
      elif (id == session.get('id')):
        return render_template('update.html',id=id)
      else:
        return render_template('validation.html',id=id)
    except Exception as e:
      return redirect(url_for('home_page'))
    
## Member Page
@app.route('/member/<string:id>')
def member_page(id):
    try:
      member = member_col.find_one({'id':str(id)}, {'_id': False})
      if(member is None):
        return redirect(url_for('/'))
      return render_template('member.html',id=id,name=member['name'])
    except Exception as e:
      return redirect(url_for('home_page'))
    

##### api #####

## Get all member / Create member
@app.route("/api/member", methods=["GET","POST"])
def get_all_or_create_member():
    if request.method == 'GET':
      try:
        allMember = list(member_col.find({}, {'_id': False}))
        return make_response(jsonify({'result': allMember}),200)
      except Exception as e:
        return make_response(jsonify({'meg': 'error'}),404)
    elif request.method == 'POST':
      try:
        id = str(uuid.uuid4())
        image = request.files['image']
        if (is_empty_file(image)):
          photo_url = 'https://intro-app-profile-image.s3.ap-northeast-2.amazonaws.com/No-Image-Placeholder.png';
        else:
          photo_url = upload_image(id,image)
        name = request.form['name']
        mbti = request.form['mbti'].upper()
        advantage = request.form['advantage']
        co_style = request.form['co_style']
        desc = request.form['desc']
        blog_url = request.form['blog_url']
        password = request.form['password']
        password_hash = ph.hash(str(password))
        doc = {
            'id' : id,
            'name': name,
            'photo_url': photo_url,
            'mbti': mbti,
            'advantage' : advantage,
            'co_style': co_style,
            'desc': desc,
            'blog_url' : blog_url,
            'password' : password_hash
        }
        db['member'].insert_one(doc)
        return make_response(jsonify({'url': '/member/'+id}),200)
      except Exception as e:
        return make_response(jsonify({'meg': str(e)}),404)

## Get member / Update member / Delete member
@app.route("/api/member/<string:id>", methods=["GET","PUT","DELETE"])
def handle_member(id):
    if request.method == 'GET':
      try:
        member = member_col.find_one({'id':str(id)}, {'_id': False})
        return make_response(jsonify({'result': member}),200)
      except Exception as e:
        return make_response(jsonify({'meg': 'error'}),404)
    elif request.method == 'PUT':
      try:
        image = request.files['image']
        if not (is_empty_file(image)):
          photo_url = upload_image(id,image)
        mbti = request.form['mbti'].upper()
        advantage = request.form['advantage']
        co_style = request.form['co_style']
        desc = request.form['desc']
        blog_url = request.form['blog_url']
        doc = {
            'mbti': mbti,
            'advantage' : advantage,
            'co_style': co_style,
            'desc': desc,
            'blog_url' : blog_url
        }

        if 'photo_url' in locals(): 
          doc['photo_url'] = photo_url
        print(doc)
        member_col.update_one({'id':str(id)},{'$set': doc})
        return make_response(jsonify({'meg': 'success'}),200)
      except Exception as e:
        return make_response(jsonify({'meg': 'error'}),404)
    elif request.method == 'DELETE':
      try:
        password = request.form['password']
        member = member_col.find_one({'id':str(id)},{'_id':False})
        print(member)
        ph.verify(member['password'], str(password))
        member_col.delete_one({'id':member['id']})
        session.clear()
        return make_response(jsonify({'meg': 'success'}),200)
      except Exception as e:
        return make_response(jsonify({'meg': 'error'}),404)
      
@app.route("/api/validation/<string:id>", methods=["POST"])
def validate_member(id):
    try:
      password = request.form['password']

      member = member_col.find_one({'id':str(id)}, {'_id': False})
      ph.verify(member['password'], str(password))
      session['id'] = id;
      return make_response(jsonify({'meg': 'success'}),200)
    except Exception as e:
      return make_response(jsonify({'meg': 'error'}),404)
       


class ImageUploadError(Exception):    
    def __init__(self):
        super().__init__('이미지 업로드에 실패했습니다.')

class InvalidExtensionError(Exception):    
  def __init__(self):
      super().__init__('잘못된 확장자입니다.')

def is_allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_IMAGE_EXTENSIONS

def is_empty_file(file_storage):
    return file_storage.filename == '' and file_storage.content_type == 'application/octet-stream'

def upload_image(id,image):
    try:
        filename =image.filename
        if not is_allowed_file(filename):
          raise InvalidExtensionError
        payload = {
        'id': id,
        'extension': filename.rsplit('.', 1)[1],
        'data': base64.b64encode(image.read()).decode('utf-8')
        }
        response = lambda_clinet.invoke(
        FunctionName='save-image-to-s3',
        InvocationType='RequestResponse',
        Payload= json.dumps(payload)
        )
        response_payload = response['Payload'].read().decode('utf-8')
        response_payload = json.loads(response_payload)
        return response_payload['body']
    except Exception as e:
        raise ImageUploadError
  
##### main #####
if __name__ == '__main__':
    app.run('0.0.0.0', port=5050, debug=True)