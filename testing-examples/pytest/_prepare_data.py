import langsmith


client = langsmith.Client()

entities = [
    "Dennie's",
    "Piggly Wiggly",
    "Fox news",
    "McDonalds",
    "Shell",
    "In-N-Out",
    "the FBI",
    "the IAS",
    "Apple",
    "Gucci",
    "Google",
    "Dollar Tree",
    
]

try:
    client.delete_dataset(dataset_name="Entity Dataset")
    # client.read_dataset(dataset_name="Entity Dataset")
except:
    client.create_dataset(dataset_name="Entity Dataset")
    for entity in entities:
        client.create_example(inputs={"entity": entity}, dataset_name="Entity Dataset")
