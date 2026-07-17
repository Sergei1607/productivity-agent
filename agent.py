import json


def read_tasks():
    with open("tasks.json", "r") as f:
        return json.load(f)


if __name__ == "__main__":
    tasks = read_tasks()
    for task in tasks:
        print(task)