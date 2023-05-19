# Tx5

B반 7조 팀소개 프로젝트 23.05.15 - 23.05.19 

## 팀원
MBTI T만 5명이 모인 B반 7조 Tx5입니다

| 팀원   | 구분      | MBTI | 블로그                       |
| ------ | -------- | ---- | ---------------------------- |
| 최윤서 |  `팀장`   | ISTJ | https://velog.io/@choiys1103 |
| 황태규 |  팀원     | ESTJ | https://velog.io/@gosky0328  |
| 전동헌 |  팀원     | INTP | https://neda.tistory.com/    |                                  
| 양지원 |  팀원     | ESTJ | https://loo1o.tistory.com/   |    
| 양현서 |  팀원     | ENTP | https://ahrhl.tistory.com/   |         
                             

## 목차

-   [1. 프로젝트 소개](#1-프로젝트-소개)
-   [2. 프로젝트 시연 영상](#2-프로젝트-시연-영상)
-   [3. API Table](#3-api-table)
-   [4. 구현기능](#4-구현-기능)

## 1. 프로젝트 소개

멤버를 소개하는 페이지. 
멤버카드를 생성, 수정, 삭제 할 수 있으며 수정/삭제 시 생성할 때 입력한 비밀번호를 사용해야 한다.

## 2. 프로젝트 시연 영상

[유튜브 링크](https://youtu.be/WxRj-VLi5Xc)

## 3. API Table

| 경로                 | HTTP   | 설명                                    | 성공                                                         | 실패                                                         |
| -------------------- | ------ | --------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| /api/member          | GET    | 모든 멤버 가져오기                      | {'result': allMember,'meg': '데이터를 성공적으로 불러왔습니다.'},200 | {'error': '데이터를 찾을 수 없습니다.'}),404                 |
| /api/member          | POST   | 새로운 멤버 생성하기                    | {'meg': '회원가입이 완료되었습니다.'},200                    | {'error': '잘못된 비밀번호입니다.'}),400<br />{'error': '회원가입에 실패했습니다.'}),404 |
| /api/member/{id}     | GET    | 단일 멤버 가져오기                      | {'result': member},200                                       | {'error': '해당 멤버의정보를 찾을 수 없습니다.'}),404        |
| /api/member/{id}     | PUT    | 단일 멤버 업데이트하기                  | {'meg': '변경사항을 성공적으로 저장하였습니다.'},200         | {'error': '서버 오류로 인해 변경사항 저장을 실패하였습니다.'}),500 |
| /api/member/{id}     | DELETE | 단일 멤버 삭제하기                      | {'meg': '멤버를 성공적으로 삭제하였습니다.'},200             | {'error': '비밀번호가 일치하지 않습니다.'}),403<br />{'error': '서버 오류로 인해 멤버 삭제에 실패했습니다.'}),500 |
| /api/validation/{id} | POST   | 세션을 통해 멤버 업데이트 권한 가져오기 | {'meg': '인증에 성공하였습니다.'},200                        | {'error': '비밀번호가 일치하지 않습니다.'}),403              |

## 4. 구현 기능

### 1) 홈 화면 및 멤버 카드생성 화면
![home](https://github.com/oiooeo/Tx5/assets/130683029/64ac78bd-8967-4940-bb06-4880e3814387)
![creat](https://github.com/oiooeo/Tx5/assets/130683029/ae055c9e-7e3a-4d34-a744-946eced660b8)

### 2) 카드별 멤버 소개 화면
![mamber](https://github.com/oiooeo/Tx5/assets/130683029/410cc088-5b36-496a-9bfa-51cd74788724)

### 3) 카드 수정/삭제 창 비밀번호로 접근 
![pass](https://github.com/oiooeo/Tx5/assets/130683029/0765df6c-0afe-424d-a97f-00eff4820e1f)
