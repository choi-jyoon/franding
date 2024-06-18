from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
import os
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
# from langchain.llms import OpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import SystemMessagePromptTemplate
# from cart.views import check_user_authentication


def db_url():  
    username='postgres'
    password=os.getenv("DB_PASSWORD")
    port='25432'
    database='franding_db'
    host='hanslab.org'

    return f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"

def create_chain(db, llm, answer_prompt):    
    execute_query = QuerySQLDataBaseTool(db=db)
    write_query = create_sql_query_chain(llm, db)
    
    chain = (
        RunnablePassthrough.assign(query=write_query).assign(
            result=itemgetter("query") | execute_query
        )
        | answer_prompt()
        | llm
        | StrOutputParser()
    )

    return chain


def best_items_answer_prompt():
    answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
    데이터베이스에서 많은 사람이 구매한 제품을 추천해주세요.
    데이터베이스에서 별점이 많은 상품을 추천해주세요.
    데이터베이스에서 가격이 높은 상품을 추천해주세요.
    데이터베이스에서 리뷰가 좋은 제품을 추천해주세요.
    상품을 3개 이상 추천해주세요.

    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
    )
    return answer_prompt


def best_items():
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    pg_uri = db_url()

    db = SQLDatabase.from_uri(pg_uri)

    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0)

    chain = create_chain(db, llm, best_items_answer_prompt)


    response = chain.invoke({"question": "향수를 추천해줘", "query": "write_query.invoke(question)", "result": "execute_query.invoke(query)"})
    return response

def similar_product_recommendations_answer_prompt():
    answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
    

    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
    )
    return answer_prompt


def similar_product_recommendations():
    pass