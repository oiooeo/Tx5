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
import certifi

ca = certifi.where()
ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# load environment variable
load_dotenv()
# flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = 600
# mongodb

MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI,tlsCAFile=ca)
print('MongodbClient: ',client)
db = client['team-intro-app']
member_col = db.member

aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
# boto3

lambda_client = boto3.client('lambda',
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
      print('update_page Error: ',str(e))
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
      print('member_page Error: ',str(e))
      return redirect(url_for('home_page'))
    

##### api #####

## Get all member / Create member
@app.route("/api/member", methods=["GET","POST"])
def get_all_or_create_member():
    if request.method == 'GET':
      try:
        allMember = list(member_col.find({}, {'_id': False}))
        return make_response(jsonify({'result': allMember,'meg': '데이터를 성공적으로 불러왔습니다.'}),200)
      except Exception as e:
        print('/api/member [GET] Error: ',str(e))
        return make_response(jsonify({'error': '데이터를 찾을 수 없습니다.'}),404)
    elif request.method == 'POST':
      
      id = str(uuid.uuid4())
      image = request.files['image']
      if (is_empty_file(image)):
        photo_url = 'https://intro-app-profile-image.s3.ap-northeast-2.amazonaws.com/No-Image-Placeholder.png';
      else:
        photo_url = upload_image(id,image)
      password = request.form['password']
      if (len(password)<4):
        return make_response(jsonify({'error': '잘못된 비밀번호입니다.'}),400)
      password_hash = ph.hash(str(password))
      name = request.form['name']
      mbti = request.form['mbti'].upper()
      advantage = request.form['advantage']
      co_style = request.form['co_style']
      desc = request.form['desc']
      blog_url = request.form['blog_url']
      try:
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
        return make_response(jsonify({'meg': '회원가입이 완료되었습니다.'}),200)
      except Exception as e:
        print('/api/member [POST] Error: ',str(e))
        return make_response(jsonify({'error': '회원가입에 실패했습니다.'}),404)

## Get member / Update member / Delete member
@app.route("/api/member/<string:id>", methods=["GET","PUT","DELETE"])
def handle_member(id):
    if request.method == 'GET':
      try:
        member = member_col.find_one({'id':str(id)}, {'_id': False})
        return make_response(jsonify({'result': member}),200)
      except Exception as e:
        print('/api/member/<id> [GET] Error: ',str(e))
        return make_response(jsonify({'error': '해당 멤버의 정보를 찾을 수 없습니다.'}),404)
    elif request.method == 'PUT':
      if 'is_reset_image' in request.form:
        photo_url = 'https://intro-app-profile-image.s3.ap-northeast-2.amazonaws.com/No-Image-Placeholder.png';
      image = request.files['image']
      if not (is_empty_file(image)):
        photo_url = upload_image(id,image)
      mbti = request.form['mbti'].upper()
      advantage = request.form['advantage']
      co_style = request.form['co_style']
      desc = request.form['desc']
      blog_url = request.form['blog_url']
      try:
        doc = {
            'mbti': mbti,
            'advantage' : advantage,
            'co_style': co_style,
            'desc': desc,
            'blog_url' : blog_url
        }
        if 'photo_url' in locals(): 
          doc['photo_url'] = photo_url
        member_col.update_one({'id':str(id)},{'$set': doc})
        return make_response(jsonify({'meg': '변경사항을 성공적으로 저장하였습니다.'}),200)
      except Exception as e:
        print('/api/member/<id> [PUT] Error: ',str(e))
        return make_response(jsonify({'error': '서버 오류로 인해 변경사항 저장을 실패하였습니다.'}),500)
    elif request.method == 'DELETE':
      try:
        password = request.form['password']
        member = member_col.find_one({'id':str(id)},{'_id':False})
        ph.verify(member['password'], str(password))
      except Exception as e:
        print('/api/member/<id> [DELETE] Error: ',str(e))
        return make_response(jsonify({'error': '비밀번호가 일치하지 않습니다.'}),403)
      try:  
        delete_image(str(id))
        member_col.delete_one({'id':member['id']})
        session.clear()
        return make_response(jsonify({'meg': '멤버를 성공적으로 삭제하였습니다.'}),200)
      except Exception as e:
        print('/api/member/<id> [DELETE] Error: ',str(e))
        return make_response(jsonify({'error': '서버 오류로 인해 멤버 삭제에 실패했습니다.'}),500)
      
@app.route("/api/validation/<string:id>", methods=["POST"])
def validate_member(id):
    try:
      password = request.form['password']
      member = member_col.find_one({'id':str(id)}, {'_id': False})
      ph.verify(member['password'], str(password))
    except Exception as e:
      print('/api/validation/<id> [POST] Error: ',str(e))
      return make_response(jsonify({'error': '비밀번호가 일치하지 않습니다.'}),403)
    session['id'] = id;
    return make_response(jsonify({'meg': '인증에 성공하였습니다.'}),200)
       


class ImageUploadError(Exception):    
    def __init__(self):
        super().__init__('이미지 업로드에 실패했습니다.')

class ImageDeleteError(Exception):    
    def __init__(self):
        super().__init__('이미지 삭제에 실패했습니다.')

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
        response = lambda_client.invoke(
          FunctionName='save-image-to-s3',
          InvocationType='RequestResponse',
          Payload= json.dumps(payload)
        )
        response_payload = response['Payload'].read().decode('utf-8')
        response_payload = json.loads(response_payload)
        return response_payload['body']
    except Exception as e:
        print('upload_image error: ',str(e))
        raise ImageUploadError

def delete_image(id):
  try:
      payload = {
         'id': id
      }
      response = lambda_client.invoke(
         FunctionName='delete-image-in-s3',
         InvocationType='RequestResponse',
         Payload= json.dumps(payload)
      )
      response_payload = response['Payload'].read().decode('utf-8')
      response_payload = json.loads(response_payload)
      return response_payload['body']
  except Exception as e:
      print('delete_image error: ',str(e))
      raise ImageDeleteError 
  
##### main #####
if __name__ == '__main__':
    app.run('0.0.0.0', port=5050, debug=True)