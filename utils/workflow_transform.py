import json
import os
import re
from typing import Optional
from uuid import uuid4

from .query_db import get_pieces_full_info


def _maybe_parse(v):
    """Parse a value that may be a JSON string from the DB."""
    if isinstance(v, str):
        try:
            return json.loads(v)
        except (json.JSONDecodeError, ValueError):
            pass
    return v


def _wrap_value(v):
    base = {"fromUpstream": False, "upstreamId": "", "upstreamArgument": "", "upstreamValue": ""}
    if isinstance(v, list):
        return {**base, "value": [{**base, "value": elem} for elem in v]}
    return {**base, "value": v}


def _parse_steps(workflow_text: str) -> list[dict]:
    steps = []
    for line in workflow_text.strip().split("\n"):
        parts = [p.strip() for p in line.split(":::")]
        if len(parts) < 3:
            continue
        try:
            step_num = int(re.search(r"\d+", parts[0]).group())
            step_data = json.loads(parts[1])
            next_step = parts[2]
            steps.append({"step": step_num, **step_data, "next": next_step})
        except (ValueError, json.JSONDecodeError, AttributeError):
            continue
    return steps


def build_workflow_json(workflow_text: str) -> Optional[dict]:
    steps = _parse_steps(workflow_text)
    if not steps:
        return None

    pieces_meta = get_pieces_full_info()

    # Generate a stable node ID per step
    node_ids = [f"{step['piece_id']}_{uuid4()}" for step in steps]

    workflow_pieces = {}
    workflow_pieces_data = {}
    workflow_nodes = []
    workflow_edges = []

    for i, (step, node_id) in enumerate(zip(steps, node_ids)):
        piece_id = step["piece_id"]
        meta = pieces_meta.get(piece_id, {})

        # Parse DB JSON string fields into objects
        container_resources = _maybe_parse(meta.get("container_resources"))
        style = _maybe_parse(meta.get("style"))
        dependency = _maybe_parse(meta.get("dependency"))
        input_schema = _maybe_parse(meta.get("input_schema"))
        output_schema = _maybe_parse(meta.get("output_schema"))
        secrets_schema = _maybe_parse(meta.get("secrets_schema"))
        piece_name = meta.get("name", step.get("piece_name", ""))

        # workflowPieces
        workflow_pieces[node_id] = {
            "id": piece_id,
            "name": piece_name,
            "description": meta.get("description", ""),
            "dependency": dependency,
            "source_image": meta.get("source_image"),
            "input_schema": input_schema,
            "output_schema": output_schema,
            "secrets_schema": secrets_schema,
            "container_resources": container_resources,
            "tags": meta.get("tags", []),
            "style": style,
            "source_url": meta.get("source_url"),
            "repository_url": meta.get("repository_url"),
            "repository_id": meta.get("repository_id"),
        }

        # workflowPiecesData
        use_gpu = container_resources.get("use_gpu", False) if isinstance(container_resources, dict) else False
        workflow_pieces_data[node_id] = {
            "storage": {"storageAccessMode": "Read/Write"},
            "containerResources": {
                "cpu": 500,
                "memory": 512,
                "useGpu": use_gpu,
            },
            "inputs": {
                arg_name: _wrap_value(value)
                for arg_name, value in step.get("arguments", {}).items()
            },
        }

        # workflowNodes
        if i == 0:
            pos = {"x": 547.5, "y": 391}
        else:
            pos = {"x": 547.5 + i * 207.75, "y": 390.5}

        workflow_nodes.append({
            "id": node_id,
            "type": "CustomNode",
            "position": pos,
            "data": {
                "name": piece_name,
                "style": style,
                "validationError": False,
                "orientation": "horizontal",
            },
            "width": 150,
            "height": 70,
            "selected": i == 0,
            "positionAbsolute": pos,
            "dragging": False,
        })

        # workflowEdges (connect i-1 → i)
        if i > 0:
            src = node_ids[i - 1]
            tgt = node_id
            edge_id = f"reactflow__edge-{src}source-{src}-{tgt}target-{tgt}"
            workflow_edges.append({
                "source": src,
                "sourceHandle": f"source-{src}",
                "target": tgt,
                "targetHandle": f"target-{tgt}",
                "id": edge_id,
                "markerEnd": {"type": "arrowclosed", "width": 20, "height": 20},
            })

    final_json = {
        "workflowPieces": workflow_pieces,
        "workflowPiecesData": workflow_pieces_data,
        "workflowNodes": workflow_nodes,
        "workflowEdges": workflow_edges,
    }

    with open(os.path.join(os.path.dirname(__file__), "workflow.json"), "w") as f:
        json.dump(final_json, f, indent=4)

    return final_json
