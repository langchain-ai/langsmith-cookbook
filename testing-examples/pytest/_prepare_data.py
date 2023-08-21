from typing import Optional
import langsmith


def create_dataset(
    dataset_name: str, descriptions: list, labels: Optional[list] = None
):
    client = langsmith.Client()
    ds = client.create_dataset(dataset_name=dataset_name)
    labels_ = labels or [None] * len(descriptions)
    for desc, label in zip(descriptions, labels_):
        client.create_example(
            inputs={"description": desc}, outputs=label, dataset_id=ds.id
        )


if __name__ == "__main__":
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

    dataset_1_name = "ORG Entities"
    langsmith.Client().delete_dataset(dataset_name=dataset_1_name)
    create_dataset(
        dataset_1_name,
        [f"I am a long-time employee of {entity}" for entity in entities],
    )

    entities_2 = [
        "I am a recent college graduate with a degree in Engineering, working full-time",
        "I am a single parent of two children, working two part-time jobs, with a mixed credit history",
        "I am a retired veteran, living on a fixed pension",
        "I am a an immigrant entrepreneur, owning a small business for 3 years,"
        " with a short but positive credit history in the country",
    ]
    dataset_2_name = "Person Entities"
    langsmith.Client().delete_dataset(dataset_name=dataset_2_name)
    labels = [
        {"expected": "There is not enough information to answer."},
    ] * len(entities_2)
    create_dataset(dataset_2_name, entities_2, labels=labels)
