import json
from openai import OpenAI

from tools.tool_definitions import builder
from tools.tool_functions import builder_call
from utils.prompts import Conversationist
from utils.utils import get_user_message


# ---- Client setup ----
client = OpenAI(
    api_key="APIKEY",
    base_url="http://localhost:8001/v1",
)

model = client.models.list().data[0].id

user_input = "build me a workflow that preprocesses images and trains a classifier on them. load images from /images and store output to /images/preprocessed for images and /output for the trained model"

conversation = [
    {
        "role": "system",
        "content": Conversationist.get_system_prompt(),
    },
    {
        "role": "user",
        "content": user_input,
    }
]



print("ASSISTANT:")
# ---- Main loop ----
while True:
    response = client.responses.create(
        model=model,
        input=conversation,
        tools=[builder],
    )

    # Extract tool calls from output
    tool_calls = [
        item for item in response.output
        if item.type == "function_call"
    ]
    conversation_1 = []
    if tool_calls:
        for call in tool_calls:
            arguments = json.loads(call.arguments)
            print(response.output[0].content[0].text)
            result = str(builder_call(call.arguments))

            conversation.append(call)

            conversation.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": result
            })

        # Send tool results back, continuing the same response thread
        response = client.responses.create(
            model=model,
            input=conversation,
            tools=[builder],
        )

        print("ASSISTANT:")

        continue

    # No tool calls → model produced a final or conversational response
    try:
        reasoning, output_text = response.output
        print("reasoning:")
        print(reasoning.content[0].text)
        print("output_text:")
        print(output_text.content[0].text)
        # Get next user input
        user_input = get_user_message()

        conversation += [{"role": output_text.role, "content": output_text.content[0].text}]
        conversation += [{"role": "user", "content": user_input}]

    except Exception as e:
        print("could not parse response")
        print(response)

