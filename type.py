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

class IAnnotationRequest(BaseModel):
    context: str
    task: str
    skillSet: list[str]
