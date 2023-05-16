import os
from dotenv import load_dotenv
from flask import Flask, render_template,session, request, jsonify,make_response,redirect,url_for
from pymongo import MongoClient
from argon2 import PasswordHasher

# flask
app = Flask(__name__)
app.secret_key = 'w5n2k365j522jlnnvewkjoew'
# mongodb
load_dotenv()
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
@app.route('/manage/update/<string:name>')
def update_page(name):
    try:
      member = member_col.find_one({'name':str(name)}, {'_id': False})
      if(member is None):
        return redirect(url_for('home_page'))
      elif (name == session.get('userName')):
        return render_template('update.html',name=name)
      else:
        return render_template('validation.html',name=name)
    except Exception as e:
      return redirect(url_for('home_page'))
    
## Member Page
@app.route('/member/<string:name>')
def member_page(name):
    try:
      member = member_col.find_one({'name':str(name)}, {'_id': False})
      if(member is None):
        return redirect(url_for('/'))
      return render_template('member.html',name=name)
    except Exception as e:
      return redirect(url_for('home_page'))


##### api #####

## Get all member / Create member
@app.route("/api/member", methods=["GET","POST"])
def create_member():
    if request.method == 'GET':
      try:
        allMember = list(member_col.find({}, {'_id': False}))
        return make_response(jsonify({'result': allMember}),200)
      except Exception as e:
        return make_response(jsonify({'meg': 'error'}),404)
    elif request.method == 'POST':
      try:
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
        return make_response(jsonify({'url': '/member/'+name}),200)
      except Exception as e:
        return make_response(jsonify({'meg': 'error'}),404)

## Get member / Update member / Delete member
@app.route("/api/member/<string:name>", methods=["GET","PUT","DELETE"])
def get_member(name):
    if request.method == 'GET':
      try:
        member = member_col.find_one({'name':str(name)}, {'_id': False})
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
        member_col.update_one({'name':str(name)},{'$set': doc})
        return make_response(jsonify({'meg': 'success'}),200)
      except Exception as e:
        return make_response(jsonify({'meg': 'error'}),404)
    elif request.method == 'DELETE':
      try:
        password = request.form['password']
        member = member_col.find_one({'name':str(name)})
        ph.verify(member['password'], str(password))
        member_col.delete_one({'_id':member['_id']})
        session.clear()
        return make_response(jsonify({'meg': 'success'}),200)
      except Exception as e:
        return make_response(jsonify({'meg': 'error'}),404)
      
@app.route("/api/validation/<string:name>", methods=["POST"])
def validation(name):
    try:
      password = request.form['password']

      member = member_col.find_one({'name':str(name)}, {'_id': False})
      ph.verify(member['password'], str(password))
      session['userName'] = name;
      return make_response(jsonify({'meg': 'success'}),200)
    except Exception as e:
      return make_response(jsonify({'meg': 'error'}),404)
       

##### main #####
if __name__ == '__main__':
    app.run('0.0.0.0', port=5050, debug=True)