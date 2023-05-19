# install

1. python -m venv venv
2. source ./venv/Scripts/activate (or) source ./venv/bin/activate
3. pip install flask pymongo python-dotenv argon2-cffi boto3 certifi

## SiteMap

| 페이지               | 경로                |
| -------------------- | ------------------- |
| 메인페이지           | /                   |
| 멤버 생성 페이지     | /manage/create      |
| 멤버 업데이트 페이지 | /manage/update/{id} |
| 멤버 삭제 페이지     | /member/{id}        |

## API

| 경로                 | HTTP   | 설명                                    | Request                                                      | 성공 Response                                                | 실패 Response                                                |
| -------------------- | ------ | --------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| /api/member          | GET    | 모든 멤버 가져오기                      |                                                              | {'result': allMember,'meg': '데이터를 성공적으로 불러왔습니다.'},200 | {'error': '데이터를 찾을 수 없습니다.'}),404                 |
| /api/member          | POST   | 새로운 멤버 생성하기                    | form: {<br />name: 이름 <br />image: (바이너리) <br />mbti: MBTI <br />blog_url: url <br />desc: 소개 <br />advantage: 장점 <br />co_style: 스타일 password: 1234<br />} | {'meg': '회원가입이 완료되었습니다.'},200                    | {'error': '잘못된 비밀번호입니다.'}),400<br />{'error': '회원가입에 실패했습니다.'}),404 |
| /api/member/{id}     | GET    | 단일 멤버 가져오기                      |                                                              | {'result': member},200                                       | {'error': '해당 멤버의정보를 찾을 수 없습니다.'}),404        |
| /api/member/{id}     | PUT    | 단일 멤버 업데이트하기                  | form: {<br />image: (바이너리)<br /> mbti: MBTI <br />blog_url: url <br />desc: 소개 <br />advantage: 장점<br /> co_style: 스타일<br />} | {'meg': '변경사항을 성공적으로 저장하였습니다.'},200         | {'error': '서버 오류로 인해 변경사항 저장을 실패하였습니다.'}),500 |
| /api/member/{id}     | DELETE | 단일 멤버 삭제하기                      | form: {<br />password: 1234<br />}                           | {'meg': '멤버를 성공적으로 삭제하였습니다.'},200             | {'error': '비밀번호가 일치하지 않습니다.'}),403<br />{'error': '서버 오류로 인해 멤버 삭제에 실패했습니다.'}),500 |
| /api/validation/{id} | POST   | 세션을 통해 멤버 업데이트 권한 가져오기 | form: {<br />password: 1234<br />}                           | {'meg': '인증에 성공하였습니다.'},200                        | {'error': '비밀번호가 일치하지 않습니다.'}),403              |
