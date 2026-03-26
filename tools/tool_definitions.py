piece_picker = {
    "type": "function",
    "name": "pick_piece",
    "description": (
        "Finds the most suitable Domino piece for each entry in a list of steps. "
        "Each entry must contain a domain and a step description."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "steps": {
                "type": "array",
                "description": "List of steps to find pieces for.",
                "items": {
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": (
                                "The data domain the step operates on, e.g. 'image processing', 'text processing', 'tabular data'."
                            )
                        },
                        "step_description": {
                            "type": "string",
                            "description": (
                                "A high-level description of the single workflow step to find a piece for."
                            )
                        }
                    },
                    "required": ["domain", "step_description"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["steps"],
        "additionalProperties": False
    }
}

builder = {
    "type": "function",
    "name": "builder",
    "description": (
        "Generates a runnable workflow for the supplied request "
        "or explains why a workflow cannot be constructed."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "identified_goal": {
                "type": "string",
                "description": (
                    "The identified objective the workflow is intended to achieve."
                )
            },
            "data_source": {
                "type": "string",
                "description": (
                    "Locations of input data. Can be multiple sources."
                )
            },
            "data_description": {
                "type": "string",
                "description": (
                    "A description of the structure, format, schema, and/or relevant characteristics of the input data."
                )
            },
            "output_destination": {
                "type": "string",
                "description": (
                    "Locations where workflow outputs should be stored. Can be multiple outputs."
                )
            },
            "workflow_description": {
                "type": "string",
                "description": (
                    "The description of the workflow user provided with no inferred information."
                )
            },
            "notes_and_feedback_stated_by_user": {
                "type": "string",
                "description": (
                    "Any notes and feedback the user may have (e.g. do not use this processing step, decide according to best practices). Do not pass them verbatim, extract the users intent."
                )
            }
        },
         "required": [
            "task_description",
            "identified_goal",
            "data_source",
            "data_description",
            "output_destination",
            "workflow_description",
            "constraints_stated_by_user"
        ],
        "additionalProperties": False
    }
}
