import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import requests


# 데이터 불러오기
data_frame = pd.read_csv("Video_Games_Data.csv")



# 추천 기능을 위한 코사인 유사도 객체 생성
tfidf = TfidfVectorizer(stop_words='english')

data_frame['Name'].isnull().values.any()

data_frame['Name'] = data_frame['Name'].fillna('')

tfidf_matrix = tfidf.fit_transform(data_frame['Name'])

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

indices = pd.Series(data_frame.index, index=data_frame['Name']).drop_duplicates()





def get_recommandations(Name): # 코사인 유사도를 통해 가장 유사도가 높은 10개 반환

        idx = data_frame[data_frame['Name'] == Name].index[0] # 인덱스 값 받기

        sim_scores = list(enumerate(cosine_sim[idx])) # 각 인덱스와 그 인덱스에 대한 유사도 값 얻기

        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True) # 유사도를 통해 내림차순 정렬 (높은 것 -> 낮은 것)

        sim_scores = sim_scores[1:11] # 1부터 10까지 인덱스와 유사도 출력

        game_indices = [i[0] for i in sim_scores] # 내림차순 한 것에서 인덱스만 뽑아오기

        recommandations_images = []
        recommandations_titles = []

        for i in game_indices:

            Name = data_frame['Name'].iloc[i]

            url = "https://api.igdb.com/v4/games"

            fields = 'cover.image_id'
            data = f'search "{Name}"; fields {fields}; limit 1;'
                
            headers = {
            "Client-ID": "532unf2hq5q02o8cukrgvf9o94mtq7",
            "Authorization": "Bearer kscq7zvvdbzan81fsxsoxkkkbba7kz"}

            response = requests.post(url, headers=headers, data=data)
            if len(response.json()) > 0 and response.json()[0].get("cover"):
                cover_id = response.json()[0]["cover"]["image_id"]
            else:
                cover_id = None
            if cover_id == None:
                recommandations_images.append("no_image.jpg")
            else:
                recommandations_images.append("https://images.igdb.com/igdb/image/upload/t_1080p/" + str(cover_id) + ".jpg")

            recommandations_titles.append(Name)

        return recommandations_images, recommandations_titles




def get_Metacritic_recommandations(): # 메타크리틱 점수를 통한 정렬

    Critic_Score_average = data_frame['Critic_Score'].mean()

    Critic_Count_average = data_frame['Critic_Count'].quantile(0.9) 

    Critic_games = data_frame.copy().loc[data_frame['Critic_Count'] >= Critic_Count_average]

    def Critic_weighted_rating(x, m=Critic_Count_average, C=Critic_Score_average):
        V = x['Critic_Count']
        R = x['Critic_Score']
        return (V / (V + m) * R) + (m / (m + V) * C)

    data_frame['score 1'] = Critic_games.apply(Critic_weighted_rating, axis=1)
    Critic_sorted_data = data_frame.sort_values(by=['score 1'], ascending=False)

    Critic_images = []
    Critic_titles = []

    for i in range(1, 11):

            Name = Critic_sorted_data['Name'].iloc[i]

            url = "https://api.igdb.com/v4/games"

            fields = 'cover.image_id'
            data = f'search "{Name}"; fields {fields}; limit 1;'
                
            headers = {
            "Client-ID": "532unf2hq5q02o8cukrgvf9o94mtq7",
            "Authorization": "Bearer kscq7zvvdbzan81fsxsoxkkkbba7kz"}

            response = requests.post(url, headers=headers, data=data)
            if len(response.json()) > 0 and response.json()[0].get("cover"):
                cover_id = response.json()[0]["cover"]["image_id"]
            else:
                cover_id = None
            if cover_id == None:
                Critic_images.append("no_image.jpg")
            else:
                Critic_images.append("https://images.igdb.com/igdb/image/upload/t_720p/" + str(cover_id) + ".jpg")

            Critic_titles.append(Name)

    return Critic_images, Critic_titles




def get_global_sales(): # 세계에서 가장 많이 팔린 게임 순 정렬

    images = []
    titles = []

    for i in range(1, 11):
            
            data_frame_original = data_frame.reset_index(drop=True)
            Name = data_frame_original['Name'].iloc[i]

            url = "https://api.igdb.com/v4/games"

            fields = 'cover.image_id'
            data = f'search "{Name}"; fields {fields}; limit 1;'
                
            headers = {
            "Client-ID": "532unf2hq5q02o8cukrgvf9o94mtq7",
            "Authorization": "Bearer kscq7zvvdbzan81fsxsoxkkkbba7kz"}

            response = requests.post(url, headers=headers, data=data)
            if len(response.json()) > 0 and response.json()[0].get("cover"):
                cover_id = response.json()[0]["cover"]["image_id"]
            else:
                cover_id = None
            if cover_id == None:
                images.append("no_image.jpg")
            else:
                images.append("https://images.igdb.com/igdb/image/upload/t_720p/" + str(cover_id) + ".jpg")

            titles.append(Name)

    return images, titles




st.set_page_config(layout='wide')
st.header("Video game recommendations")

game_list = data_frame['Name'].values

title = st.selectbox('What Vedio Game do you like?', game_list)
if st.button('Recommand'):
    with st.spinner('Please wait...'):
        recommendations_images, recommendations_titles = get_recommandations(title)

        idx2 = 0
        for i in range(0, 2):
            cols = st.columns(5)
            for col in cols:
                col.image(recommendations_images[idx2])
                col.write(recommendations_titles[idx2])
                idx2 += 1




st.title('Best selling game in the world')

with st.spinner('Please wait...'):
    images, titles = get_global_sales()

idx2 = 0
cols = st.columns(10)
for col in cols:
    col.image(images[idx2])
    col.write(titles[idx2])
    idx2 += 1




st.title('Vedio games with high Metacritic scores')

with st.spinner('Please wait...'):
    critic_images, critic_titles = get_Metacritic_recommandations()

idx2 = 0
cols = st.columns(10)
for col in cols:
    col.image(critic_images[idx2])
    col.write(critic_titles[idx2])
    idx2 += 1



st.text("The information in the data may be inaccurate, resulting in unwanted values.")














