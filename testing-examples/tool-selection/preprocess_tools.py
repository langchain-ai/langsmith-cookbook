import json
from pathlib import Path

# Downloaded from https://github.com/OpenBMB/ToolBench/tree/3010778f5834fde71dc7658b4d51d1023affc21d?tab=readme-ov-file
root = Path("~/Downloads/data/instruction/").expanduser()
with (root / "G2_query.json").open("r") as f:
    d = json.load(f)

category = "Logistics"
selected = []
for row in d:
    if set(x["category_name"] for x in row["api_list"]) == {category}:
        selected.append(row)


def convert_to_tool(api):
    schema = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    # Add required parameters
    for param in api["required_parameters"]:
        schema["properties"][param["name"]] = {
            "type": param["type"].lower(),
            "description": param["description"],
        }
        schema["required"].append(param["name"])

    # Add optional parameters
    for param in api["optional_parameters"]:
        schema["properties"][param["name"]] = {
            "type": param["type"].lower(),
            "description": param["description"],
        }
    return {
        "type": "function",
        "function": {
            "name": api["tool_name"]
            .replace(" ", "")
            .replace("&", "And")
            .replace("(", "")
            .replace(")", ""),
            "description": api["api_description"],
            "parameters": schema,
        },
    }


def convert_apis(apis):
    json_schemas = []
    for api in apis:
        schema = convert_to_tool(api)
        json_schemas.append(schema)
    return json_schemas


def convert_all_apis(apis):
    tools = {}
    for api in apis:
        for tool in convert_apis(api["api_list"]):
            tools[tool["function"]["name"]] = tool

    return list(tools.values())


tools = convert_all_apis(selected)

with Path("./data/tools.json").open("w") as f:
    json.dump(tools, f)
