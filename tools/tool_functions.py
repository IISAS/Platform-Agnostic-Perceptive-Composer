import asyncio
import json
import os

from openai import AsyncOpenAI, OpenAI
import polars as pl

from utils.prompts import Builder, PiecePicker, Composer
from utils.query_db import get_pieces_info
from tools.tool_definitions import piece_picker
from utils.workflow_transform import build_workflow_json

# ---- Client setup ----
_base_url = os.environ["LLM_BASE_URL"]
_api_key = os.environ["LLM_API_KEY"]

sync_client = OpenAI(
    api_key=_api_key,
    base_url=_base_url,
)

client = AsyncOpenAI(
    api_key=_api_key,
    base_url=_base_url,
)

model = sync_client.models.list().data[0].id


async def _call_piece_picker(step: dict, available_pieces: pl.DataFrame) -> dict:
    input_list = [
        {
            "role": "system",
            "content": PiecePicker.get_system_prompt(available_pieces.write_csv())
        },
        {
            "role": "user",
            "content": f"domain: {step['domain']}; step - {step['step_description']}"
        }
    ]

    response = await client.responses.create(
        model=model,
        input=input_list,
        temperature=0,
    )

    ids = json.loads(response.output[1].content[0].text)
    csv_no_header = available_pieces.filter(pl.col("id").is_in(ids)).write_csv(include_header=False)
    step["chosen_pieces"] = f"{[row for row in csv_no_header.strip().split("\n") if row]}"

    return step


def pick_piece(steps: list[dict]) -> list[dict]:
    available_pieces = get_pieces_info()

    print("PIECE PICKER:")

    async def _gather():
        return await asyncio.gather(
            *[_call_piece_picker(step, available_pieces) for step in steps]
        )

    results = asyncio.run(_gather())

    for result in results:
        print("____________")
        print(result["domain"])
        print(result["step_description"])
        print(result["chosen_pieces"])

    return list(results)


def _enrich_workflow_with_piece_info(workflow_text: str) -> str:
    pieces_df = get_pieces_info()
    enriched_lines = []
    for line in workflow_text.strip().split("\n"):
        parts = [p.strip() for p in line.split(":::")]
        if len(parts) >= 3:
            try:
                piece_id = int(parts[2])
                row = pieces_df.filter(pl.col("id") == piece_id)
                if len(row) > 0:
                    parts[2] = row.write_csv(include_header=False).strip()
            except ValueError:
                pass
        enriched_lines.append(" ::: ".join(parts))
    return "\n".join(enriched_lines)


def builder_call(conversation_summary: str):
    print("BUILDER:")
    print(conversation_summary)

    conversation = [
        {"role": "system", "content": Builder.get_system_prompt()},
        {"role": "user", "content": conversation_summary}
    ]
    while True:
        response = sync_client.responses.create(
            model=model,
            input=conversation,
            temperature=0,
            tools=[piece_picker],
        )

        tool_calls = [item for item in response.output if item.type == "function_call"]
        if not tool_calls:
            break

        for call in tool_calls:
            arguments = json.loads(call.arguments)
            result = pick_piece(steps=arguments["steps"])
            conversation.append(call)
            conversation.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(result),
            })


    reasoning, workflow_text = response.output
    print("builder reasoning:")
    print(reasoning.content[0].text)
    print("builder output:")
    print(workflow_text.content[0].text)

    enriched_workflow = _enrich_workflow_with_piece_info(workflow_text.content[0].text)

    conversation = [
        {"role": "system", "content": Composer.get_system_prompt()},
        {"role": "user", "content": Composer.format_user_input(conversation_summary, enriched_workflow)},
    ]

    response = sync_client.responses.create(
        model=model,
        input=conversation,
        temperature=0
    )

    reasoning, output_text = response.output
    print("composer reasoning:")
    print(reasoning.content[0].text)
    print("composer output:")
    print(output_text.content[0].text)

    return build_workflow_json(output_text.content[0].text)

