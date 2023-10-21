from dataclasses import dataclass


@dataclass
class User:
    id: int
    username: str
    name: str
    is_admin: bool = False

@dataclass
class Meme:
    id: int
    name: str
    owner: User
