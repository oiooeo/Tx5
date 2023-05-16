# install

1. python -m venv venv
2. source ./venv/Scripts/activate (or) source ./venv/bin/activate
3. pip install flask pymongo python-dotenv argon2-cffi

## SiteMap

| 페이지               | 경로           |
| -------------------- | -------------- |
| 메인페이지           | /              |
| 멤버 생성 페이지     | /manage/create |
| 멤버 업데이트 페이지 | /manage/{name} |
| 멤버 페이지          | /member/{name} |

## API

| 경로                   | HTTP   | 설명                                    |
| ---------------------- | ------ | --------------------------------------- |
| /api/member            | GET    | 모든 멤버 가져오기                      |
| /api/member            | POST   | 새로운 멤버 생성하기                    |
| /api/member/{name}     | GET    | 단일 멤버 가져오기                      |
| /api/member/{name}     | PUT    | 단일 멤버 업데이트하기                  |
| /api/member/{name}     | DELETE | 단일 멤버 삭제하기                      |
| /api/validation/{name} | POST   | 세션을 통해 멤버 업데이트 권한 가져오기 |
