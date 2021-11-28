from dataclasses import dataclass
from enum import Enum
from typing import List


class ModMode(Enum):
    OFF = 0
    AUTOFLAG = 1
    AUTODELETE = 2


@dataclass
class FiexmoSetting:
    mode: ModMode
    ignores: List[int]
    use_roles: List[int]


class FiexmoSettingStore:
    def __init__(self, db):
        self.db = db
        self.servers = db.collection('servers')
        self.cache = {}

    def get(self, guild_id: int) -> FiexmoSetting:
        if guild_id not in self.cache:
            doc = self.servers.document(str(guild_id))
            doc_dict = doc.get().to_dict()
            if doc_dict is None:
                self.set(guild_id, FiexmoSetting(ModMode.OFF, [], []))
            else:
                self.cache[guild_id] = FiexmoSetting(ModMode(doc_dict["mode"]),
                                                     doc_dict["ignores"],
                                                     doc_dict["use_roles"])

        return self.cache[guild_id]

    def set(self, guild_id: int, fset: FiexmoSetting):
        self.cache[guild_id] = fset
        doc = self.servers.document(str(guild_id))
        doc.set({"mode": int(fset.mode.value), "ignores": fset.ignores, "use_roles": fset.use_roles})
