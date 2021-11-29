from dataclasses import dataclass, field
from enum import Enum
from typing import List


class ModMode(int, Enum):
    OFF = 0
    AUTOFLAG = 1
    AUTODELETE = 2


@dataclass
class FiexmoSetting:
    mode: ModMode = ModMode.OFF
    ignores: List[int] = field(default_factory=list)
    use_roles: List[int] = field(default_factory=list)
    allowed_mimes: List[str] = field(default_factory=lambda: ["video/*", "image/*", "audio/*", "text/*"])


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
                self.set(guild_id, FiexmoSetting())
            else:
                self.cache[guild_id] = FiexmoSetting(ModMode(doc_dict["mode"]),
                                                     doc_dict["ignores"],
                                                     doc_dict["use_roles"],
                                                     doc_dict["allowed_mimes"])

        return self.cache[guild_id]

    def set(self, guild_id: int, fset: FiexmoSetting):
        self.cache[guild_id] = fset
        doc = self.servers.document(str(guild_id))
        #doc.set({"mode": int(fset.mode.value), "ignores": fset.ignores, "use_roles": fset.use_roles})
        doc.set(fset.__dict__)
