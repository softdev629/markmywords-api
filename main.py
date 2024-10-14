from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import anthropic
import json
from type import IChatRequest, IAnnotationRequest
import requests


load_dotenv()

anthropicApiKey = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(
    api_key=anthropicApiKey,
)


app = FastAPI()

origins = [
    "https://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/signin")
async def signin(email: str = Body(embed=True)):
    exists = False
    response = requests.post(
        url="https://dev.markmywords.tech/api/admin/email",
        headers={
            "Authorization": "Bearer 01923272-490c-7fa4-ba32-a7af7235be06",
            "Content-Type": "application/json",
        },
        json={"email": email},
    )
    if response.status_code == 200:
        json_data = response.json()
        exists = json_data["exists"]
    return {"status": "success", "data": {"exists": exists}}


@app.post("/api/annotate")
async def annotate(reqData: IAnnotationRequest):
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=2048,
        system="""You are a seasoned teacher who has to assess student's submit and give annotations for improvements and fixes. Context, Task Type, Skillsets are Given. You must return annotation assess result in JSON format.

        {
          graph: [
            {
              name: SKILLSET_ITEM,
              score: SCORE
            }
          ],
          improve: [
            {
                subpart: ANNOTATION_PART,
                comment: ANNOTATION_TEXT
            }
          ]
        }
        
        graph part is array of json for scores for skillset items given, name is skillset item name, score is the score(1-100) you've assessed for that skillset item
        improve part is array of json for annotations, subpart is the sub part which is in the context searchable which needs annotation and comment is annotation text.
        """,  # <-- role prompt
        messages=[
            {
                "role": "user",
                "content": f"You must return JSON array data only.\n\ncontext: <context>{reqData.context}</context>\n\Task Type: <task>{reqData.task}</task>\n\nSkillsets: <skillsets>{reqData.skillSet}</skillsets>",
            }
        ],
    )
    json_string = response.content[0].text
    print(json_string)
    json_array = json.loads(json_string)
    print(json_array)
    return {"status": "success", "data": json_array}


@app.post("/api/chat")
async def chat(reqData: IChatRequest):
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=2048,
        system=f"You are a seasoned teacher who assessed student's writing and gave them annotations for improvements already. The student will ask some questions about your assessments and unclear things. This is a conversation between teacher and the student. \n\n Reference following contexts:\n{reqData.context} \n\n There are annotations you gave to the student. Reference below annotations. It is array consists of subpart(annotation part) and comment(annotation comment).\n{reqData.annotations}",
        messages=reqData.messages,
    )
    resMsg = response.content[0].text
    return {"status": "success", "data": {"message": resMsg}}
