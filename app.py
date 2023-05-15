import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify,make_response
from pymongo import MongoClient

# flask
app = Flask(__name__)

# mongodb
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGODB_URI)
print(client)
db = client['team-intro-app']


##### flask app #####

## HOME page
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/manage/create')
def create():
    return render_template('create.html')

## Member page
@app.route('/member/<string:name>')
def member(name):
    return render_template('member.html',name=name)


##### api #####
## create member
@app.route("/api/member", methods=["POST"])
def create_member():
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
      return jsonify({'msg': 'success'},200)
    except Exception as e:
      return jsonify({'msg': 'error'},404)

## get member data
@app.route("/api/member/<string:Name>", methods=["GET"])
def get_member(Name):
    try:
      member = list(db.member.find({'name':str(Name)}, {'_id': False}).limit(1))
      return jsonify({'result': member})
    except Exception as e:
      return make_response(jsonify({'meg': 'error'}),404)

## get all member data
@app.route("/api/", methods=["GET"])
def get_members():
    try:
      allMember = list(db.member.find({}, {'_id': False}))
      return jsonify({'result': allMember})
    except Exception as e:
      return make_response(jsonify({'meg': 'error'}),404)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5050, debug=True)