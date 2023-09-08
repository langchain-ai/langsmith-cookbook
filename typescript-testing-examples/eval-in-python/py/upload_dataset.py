"""Upload the dataset to the server."""
from langsmith import Client


if __name__ == "__main__":
    dataset_name = "Structured Output Example"
    examples = [
        {
            "input": "I am a person named John.",
            "output": {
                "name": "John",
                "type": "person",
            },
        },
        {
            "input": "I am a person named John and I am 20 years old.",
            "output": {
                "name": "John",
                "age": 20,
                "entity": "person",
            },
        },
        {
            "input": "I am a person named John and I am 20 years old. I live in New York.",
            "output": {
                "name": "John",
                "age": 20,
                "location": "New York",
            },
        },
        {
            "input": "There once was a hero named Ragnar the Red who came riding to Whiterun from ole Rorikstead.",
            "output": {
                "hero": "Ragnar the Red",
                "location": "Whiterun",
                "origin": "Rorikstead",
            },
        },
    ]
    client = Client()
    dataset = client.create_dataset(dataset_name=dataset_name)
    for example in examples:
        client.create_example(
            inputs={"input": example["input"]},
            outputs={"output": example["output"]},
            dataset_id=dataset.id,
        )
