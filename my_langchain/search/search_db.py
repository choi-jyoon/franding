from fastapi import FastAPI, HTTPException
import pandas as pd
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import uvicorn


# 데이터 로드
def load_data():
    qna_csv = pd.read_csv('my_langchain/csv_file/QnA.csv')
    return qna_csv


# 임베딩 모델 초기화
def init_model():
    # sbert = SentenceTransformerEmbeddings(model_name='jhgan/ko-sroberta-multitask')
    sbert = HuggingFaceEmbeddings(model_name='jhgan/ko-sroberta-multitask')
    return sbert 


# data_file()['title'].tolist()+data_file()['content'].tolist() 어떻게?
def vector_store_texts(data_file):
    id = data_file()['id'].tolist()
    title = data_file()['title'].tolist()
    content = data_file()['content'].tolist()
    created_at = data_file()['created_at'].tolist()
    text_list = []

    for i, x, y, z in zip(id, title, content, created_at):
        str_i = str(i)
        texts = str_i + ", " + x + ", " + y + ", " + z
        text_list.append(texts)

    return text_list


# 벡터 저장소 생성
def init_vector_store(data_file, sbert):
    # texts= [
    #         purfume()['description'].tolist(), 
    #         purfume()['summary'].tolist(),
    # ],
    vector_store = Chroma.from_texts(
        # texts = [str(x) for x in data_file()['id'].tolist()], 
        # texts = data_file()['title'].tolist(),
        texts = vector_store_texts(data_file),
        embedding=sbert(),
    )
    return vector_store


# def query(search="6월 5일"):
#     return search


# fastapi 등록
# app = FastAPI()

# @app.post("/search/")
def search_question(query):
    vector_store = init_vector_store(load_data, init_model)
    results = vector_store.similarity_search(query=query, k=10)  # 상위 3개 결과 반환
    return {"query": query, "results": results}


if __name__ == "__main__":
    # uvicorn.run("cart.search_db:app", host="127.0.0.1", port=9000, reload=True)
    pass