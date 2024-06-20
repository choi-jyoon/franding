from django.shortcuts import render
from django.conf import settings
from langchain_community.utilities import SQLDatabase
from django.http import JsonResponse
from langchain_openai import ChatOpenAI
from langchain.chains import create_sql_query_chain
from operator import itemgetter
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
import os
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_protect

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
DATABASES = settings.DATABASES['default']

pg_uri = f"postgresql+psycopg2://{DATABASES['USER']}:{DATABASES['PASSWORD']}@{DATABASES['HOST']}:{DATABASES['PORT']}/{DATABASES['NAME']}"
db = SQLDatabase.from_uri(pg_uri)
llm = ChatOpenAI(openai_api_key=API_KEY, temperature=0.5) # gpt-4-turbo

@csrf_protect
def chat_response(request):
    if request.method == "POST":
        user_message = request.POST.get('message', '')
        if not user_message:
            return JsonResponse({"error": "Message is required."}, status=400)

        execute_query = QuerySQLDataBaseTool(db=db)
        write_query = create_sql_query_chain(llm, db)
        answer_prompt = PromptTemplate.from_template(
            """유저의 질문에 따라 관련된 SQL 쿼리와 그 결과를 사용하여 답변을 제공하세요. 불필요한 정보는 생략합니다.
            너는 데이터베이스를 기반으로 질의응답을 하는 로봇이야.
            너는 사용자에게 친절한 답변을 해줘.
            유저의 질문에 답을 할 수 없을때는 '죄송해요😥 아직 답변을 찾지 못했어요.' 라고 말해줘.
            
            질문: {question}
            SQL 쿼리: {query}
            SQL 결과: {result}
            답변: """
        )
        parser = StrOutputParser()
        answer = answer_prompt | llm | parser
        chain = (
            RunnablePassthrough.assign(query=write_query).assign(
                result=itemgetter("query") | execute_query
            )
            | answer
        )

        response_data = chain.invoke({"question": user_message})
        return JsonResponse({"response": response_data})
    return JsonResponse({"error": "Invalid request method."}, status=405)

def chatbot(request):
    return render(request, 'templates/base.html')
