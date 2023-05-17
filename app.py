import os
import uuid
from dotenv import load_dotenv
from flask import Flask, render_template,session, request, jsonify,make_response,redirect,url_for
from pymongo import MongoClient
from argon2 import PasswordHasher

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
        name = request.form['name']
        photo_url = request.form['photo_url']
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
        return make_response(jsonify({'meg': 'error'}),404)

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
        photo_url = request.form['photo_url']
        mbti = request.form['mbti'].upper()
        advantage = request.form['advantage']
        co_style = request.form['co_style']
        desc = request.form['desc']
        blog_url = request.form['blog_url']
        doc = {
            'photo_url': photo_url,
            'mbti': mbti,
            'advantage' : advantage,
            'co_style': co_style,
            'desc': desc,
            'blog_url' : blog_url
        }
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
       

##### main #####
if __name__ == '__main__':
    app.run('0.0.0.0', port=5050, debug=True)