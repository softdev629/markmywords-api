from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import anthropic
import json
from pydantic import BaseModel


class IAnnotationItem(BaseModel):
    subpart: str
    comment: str


class IChatMessageItem(BaseModel):
    role: str
    content: str


class IChatRequest(BaseModel):
    context: str
    annotations: list[IAnnotationItem]
    messages: list[IChatMessageItem]


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


@app.post("/api/annotate")
async def annotate(context: str = Body(embed=True)):
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=2048,
        system="""You are a seasoned teacher who has to assess student's submit and give annotations for improvements and fixes. You must return annotations in array of JSON format.
        {
          subpart: ANNOTATION_PART,
          comment: ANNOTATION_TEXT
        }
        
        subpart is the sub part of the context which needs annotation and comment is annotation text.
        """,  # <-- role prompt
        messages=[
            {
                "role": "user",
                "content": f"You must return JSON array data only. Annotate this context for a student: <document>{context}</document>",
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
