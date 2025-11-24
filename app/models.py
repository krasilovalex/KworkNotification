from dataclasses import dataclass


@dataclass
class Project:
    project_id: str
    title: str
    price: str
    url: str
    