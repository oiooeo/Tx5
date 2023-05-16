import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify,make_response,redirect,url_for
from pymongo import MongoClient

# flask
app = Flask(__name__)

# mongodb
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
print(client)
db = client['team-intro-app']
member_col = db.member


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
        return redirect(url_for('/'))
      return render_template('update.html',name=name)
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
        doc = {
            'name': name,
            'photo_url': photo_url,
            'mbti': mbti,
            'advantage' : advantage,
            'co_style': co_style,
            'desc': desc,
            'blog_url' : blog_url
        }
        db['member'].insert_one(doc)
        return make_response(jsonify({'url': '/member/'+name}),200)
      except Exception as e:
        return make_response(jsonify({'meg': 'error'}),404)

## Get member / Update member / Delete member
@app.route("/api/member/<string:name>", methods=["GET","PUT","DELETE"])
def get_member(name):
    if request.method == 'GET':
      print('get')
      try:
        member = member_col.find_one({'name':str(name)}, {'_id': False})
        return make_response(jsonify({'result': member}),200)
      except Exception as e:
        return make_response(jsonify({'meg': 'error'}),404)
    elif request.method == 'PUT':
      print('put')
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
        member_col.delete_one({'name':str(name)})
        return make_response(jsonify({'meg': 'success'}),200)
      except Exception as e:
        return make_response(jsonify({'meg': 'error'}),404)
    
       
##### main #####
if __name__ == '__main__':
    app.run('0.0.0.0', port=5050, debug=True)