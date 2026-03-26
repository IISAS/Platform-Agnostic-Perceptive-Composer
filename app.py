import os
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from utils.prompts import Conversationist
from tools.tool_definitions import builder
from tools.tool_functions import builder_call, sync_client, model

app = FastAPI()
security = HTTPBearer(auto_error=False)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    workspace_id: int


def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    expected_token = os.environ.get("CHAT_APP_TOKEN")
    if expected_token is None:
        return
    if credentials is None or credentials.credentials != expected_token:
        raise HTTPException(status_code=401, detail="Invalid or missing token")


@app.post("/chat")
def chat(request: ChatRequest, _=Depends(verify_token)):
    conversation = [
        {"role": "system", "content": Conversationist.get_system_prompt()}
    ]
    conversation += [{"role": m.role, "content": m.content} for m in request.messages]

    workflow = None

    while True:
        response = sync_client.responses.create(
            model=model,
            input=conversation,
            tools=[builder],
        )

        tool_calls = [item for item in response.output if item.type == "function_call"]
        if not tool_calls:
            break

        for call in tool_calls:
            workflow = builder_call(call.arguments)

            conversation.append(call)
            conversation.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": str(workflow),
        })

    try:
        _, output_text = response.output
        message = output_text.content[0].text
    except Exception:
        message = next(
            (item.content[0].text for item in reversed(response.output) if hasattr(item, "content")),
            "Unable to generate a response.",
        )

    response = {"message": message}

    if workflow is not None:
        response["workflow"] = workflow

    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6969)