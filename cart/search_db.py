from fastapi import FastAPI, HTTPException
import pandas as pd
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import uvicorn


# 데이터 로드
def load_data():
    qna_csv = pd.read_csv('QnA.csv')
    return qna_csv


# 임베딩 모델 초기화
def init_model():
    sbert = SentenceTransformerEmbeddings(model_name='jhgan/ko-sroberta-multitask')
    return sbert    


# 벡터 저장소 생성
def init_vector_store(data_file, sbert):
    # texts= [
    #         purfume()['description'].tolist(), 
    #         purfume()['summary'].tolist(),
    # ],
    vector_store = Chroma.from_texts(
        # texts = [str(x) for x in data_file()['id'].tolist()], 
        texts = data_file()['title'].tolist(),
        embedding=sbert(),
    )
    return vector_store


def query(search="괜찮나요"):
    return search


# fastapi 등록
# app = FastAPI()

# @app.post("/search/")
def search_books(query=query):
    vector_store = init_vector_store(load_data, init_model)
    results = vector_store.similarity_search(query=query(), k=3)  # 상위 3개 결과 반환
    return {"query": query, "results": results}

print(search_books())


if __name__ == "__main__":
    # uvicorn.run("cart.search_db:app", host="127.0.0.1", port=9000, reload=True)
    pass