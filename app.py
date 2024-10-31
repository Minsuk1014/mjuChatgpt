from flask import Flask, request, render_template, jsonify, redirect, url_for
import pandas as pd
from openai import OpenAI
import os
from src.crawl import Coupang  # main.py에 있는 Coupang 클래스를 가져옴
from dotenv import load_dotenv

app = Flask(__name__)

link_history = []

# OpenAI 객체 생성 및 API 키 설정

client = OpenAI(api_key="your_key")  # 실제 API 키를 넣어주세요

# GPT-3.5 또는 GPT-4 모델을 사용한 Chat Completion 요청 함수
def get_completion(prompt, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0,
    )
    return response.choices[0].message.content

@app.route('/')
def index():
    return render_template('index.html',link_history=link_history)

@app.route('/process', methods=['POST'])
def process_url():
    # 웹 페이지에서 URL 입력받기
    data = request.get_json()
    url = data.get('url')
    
    link_history.append(url)
    # Coupang 클래스 인스턴스 생성 및 크롤링 시작
    coupang = Coupang()
    coupang.start(url)  # URL을 start 메서드에 전달

    # 크롤링된 엑셀 파일 경로 설정 (가장 최신 파일 가져오기)
    review_folder = os.path.join(os.path.dirname(__file__), 'Coupang-reviews')
    latest_file = max([os.path.join(review_folder, f) for f in os.listdir(review_folder)], key=os.path.getctime)

    # 엑셀 파일 불러오기
    df = pd.read_excel(latest_file)
    data_text = df.to_string()[:1000]  # 데이터가 너무 길 경우, 일부만 사용


    # GPT API 호출
    prompt = (
        f"""
        According to the following sentiment elements definition:\n
        − The 'aspect term' refers to a specific feature, attribute, or aspect of a product or service that a user may express an opinion
        about, the aspect term might be 'null' for implicit aspect.\n
        − The 'opinion term' refers to the sentiment or attitude expressed by a user towards a particular aspect or feature of a product
        or service, the aspect term might be 'null' for implicit opinion.\n
        − The 'aspect category' refers to a broader, predefined group or theme that encompasses multiple related aspects of a product, service, or topic. It provides a higher-level classification for organizing and grouping specific aspects. Aspect categories help in structuring the analysis and understanding the sentiment across different dimensions of the subject being analyzed.\n
        − The 'sentiment polarity' refers to the degree of positivity, negativity or neutrality expressed in the opinion towards a
        particular aspect or feature of a product or service, and the available polarities includes: 'positive', 'negative' and 'neutral'.\n
        
        Recognize all sentiment elements with their corresponding aspect terms, aspect categories, opinion terms and sentiment
        polarity in the following text with the format of [('aspect term', 'opinion term', 'aspect category', 'sentiment polarity'), …]:
        Text: never again !\n
        Sentiment Elements: [('null', 'never', 'restaurant general', 'bad')]\n
        Text: the food was mediocre at best but it was the horrible service that made me vow never to go back .\n
        Sentiment Elements: [('food', 'mediocre', 'food quality', 'bad'), ('service', 'horrible', 'service general', 'bad')]\n
        Text: we had the lobster sandwich and it was fantastic .\n
        Sentiment Elements: [('lobster sandwich', 'fantastic', 'food quality', 'great')]\n
        Text: they have it all −− great price , food , and service .\n
        Sentiment Elements: [('null', 'great', 'restaurant prices', 'great'), ('food', 'great', 'food quality', 'great'), ('service', 'great', 'service general', 'great')]\n
        Text: they even scoop it out nice ( for those on a diet ) not too much not to little .\n
        Sentiment Elements: [('null', 'nice', 'food style_options', 'great')]\n
        Text: also it 's great to have dinner in a very romantic and comfortable place , the service it 's just perfect … they 're so friendly\n
        that we never want to live the place !\n
        Sentiment Elements: [('place', 'romantic', 'ambience general', 'great'), ('place', 'comfortable', 'ambience general', 'great'), ('service', 'perfect', 'service general', 'great')]\n
        Text: my friend from milan and myself were pleasantly surprised when we arrived and everyone spoke italian .\n
        Sentiment Elements: [('null', 'pleasantly surprised', 'restaurant miscellaneous', 'great')]\n
        Text: i had their eggs benedict for brunch , which were the worst in my entire life , i tried removing the hollandaise sauce\n
        completely that was how failed it was .\n
        Sentiment Elements: [('eggs benedict', 'worst', 'food quality', 'bad')]\n
        Text: the food is authentic italian − delicious !\n
        Sentiment Elements: [('food', 'authentic italian', 'food quality', 'great'), ('food', 'delicious', 'food quality', 'great')]\n
        Text: a little pricey but it really hits the spot on a sunday morning !\n
        Sentiment Elements: [('null', 'pricey', 'restaurant prices', 'bad'), ('null', 'hits the spot', 'restaurant general', 'great')]\n
        {data_text}
        """
    )
    
    try:
        result = get_completion(prompt)  # get_completion 함수에 prompt 전달
    except Exception as e:
        print("API 호출 오류:", e)
        result = "API 호출 중 오류가 발생했습니다."

    # 결과를 HTML 페이지에 렌더링
    return jsonify({"result": result})

@app.route('/chat', methods=['POST'])
def chat():
    
    review_folder = os.path.join(os.path.dirname(__file__), 'Coupang-reviews')
    latest_file = max([os.path.join(review_folder, f) for f in os.listdir(review_folder)], key=os.path.getctime)

    # 엑셀 파일 불러오기
    df = pd.read_excel(latest_file)
    data_text = df.to_string()[:1000]  # 데이터가 너무 길 경우, 일부만 사용
    user_message = request.json.get("message", "")
    try:
        # OpenAI Chat API 호출
        bot_reply = get_completion(user_message)
    except Exception as e:
        bot_reply = f"오류가 발생했습니다: {str(e)}"
        
    return jsonify({"reply": bot_reply})   




if __name__ == '__main__':
    app.run(debug=True)