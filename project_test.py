#Streamlit 호출
import streamlit as st
# 정규표현식 검색
import re
# 패키지 불러오기
from langchain.document_loaders import YoutubeLoader

#Bedrock 호출 및 연결
import boto3
import json
session = boto3.Session()
bedrock = session.client(
    service_name='bedrock-runtime',
    region_name='us-east-1',
    endpoint_url="https://bedrock-runtime.us-east-1.amazonaws.com"
)


###################
# 클루드 관련 함수
###################
def ask_claude(prompt):
    body = json.dumps({
        "prompt": "\n\nHuman: " + prompt + "\n\nAssistant:",
        "max_tokens_to_sample": 1000,
        "temperature": 0.1,
        "top_p": 0.9,
    })

    modelId = 'anthropic.claude-v2'
    accept = 'application/json'
    contentType = 'application/json'

    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())

    return response_body.get('completion')


####################
# 유튜브 URL 체크
####################
def youtube_url_check(url):
    pattern = r'^https:\/\/www\.youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)(\&ab_channel=[\w\d]+)?$'
    match = re.match(pattern, url)
    return match is not None

####################
# 페이지 생성
####################
st.set_page_config(page_title="유튜브 지식 탐색기", layout="wide")
st.header('긴 유튜브 영상에 대해 궁금했던 점을 물어보자')
st.markdown('---')

#두개의 열로 분할
col1, col2 = st.columns(2)

#첫 열의 엔티티 입력 (ex : https://www.youtube.com/watch?v=cItcOUjqoEs)
with col1:
    urlinput = st.text_input('유튜브 영상 링크 입력', placeholder='ex : https://www.youtube.com/watch?v=**')
    urlbtn = st.button
    if st.button('로드'):
        if len(urlinput)>2:
            if not youtube_url_check(urlinput): # URL을 잘못 입력했을 경우
                st.error("YouTube URL을 확인하세요.")
            else: # URL을 제대로 입력했을 경우
                st.write('로드 입력됨')
                col1.video(data=urlinput)


#두번쨰 열의 엔티티 입력
with col2:
    question = st.text_input('궁금한 점', placeholder='여기에 들어감')

    if question:
                #유튜브 스크립트 추출하기
                loader = YoutubeLoader.from_youtube_url(urlinput)
                transcript = loader.load()
                #Debug : 스크립트 보여주기
                print(transcript[0].page_content)

                #AI 프롬포트 작성
                prompt = f'''
                아래는 유튜브에서 추출한 유튜브 스크립트 내용이야 아래 내용을 읽어보고 아래의 질문에 대해 아는대로 대답해줘
                대답할 때는 한국어로 대답해줘
                - 내용: {transcript[0].page_content}
                - 질문: {question}
                '''

                #출력 시작
                st.text_area(ask_claude(prompt))