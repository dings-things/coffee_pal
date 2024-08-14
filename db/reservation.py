from datetime import datetime
import json
import os
import uuid
from pydantic import BaseModel
from filelock import FileLock

import utils

UTF8_ENCODING = "utf-8"


class ReservationEntity(BaseModel):
    target_id: str
    date: datetime
    message: dict
    uuid: str = str(uuid.uuid4())

    def to_dict(self):
        data = self.model_dump()
        data["date"] = self.date.isoformat()  # datetime을 ISO 형식의 문자열로 변환
        return data

    @classmethod
    def from_dict(cls, data):
        data["date"] = datetime.fromisoformat(
            data["date"]
        )  # 문자열을 datetime 객체로 변환
        return cls(**data)


class FileDB:
    def __init__(self, file_path: str, file_lock_path: str):
        self.file_path = file_path
        self.lock_path = file_lock_path
        self.lock = FileLock(self.lock_path)
        self.data: dict[str, list[ReservationEntity]] = self.load()
        self.reload()

    def load(self) -> dict[str, list[ReservationEntity]]:
        if not os.path.exists(self.file_path):
            return {}

        with open(self.file_path, "r", encoding=UTF8_ENCODING) as f:
            raw_data = json.load(f)
            data = {}
            for user_id, reservations in raw_data.items():
                data[user_id] = [
                    ReservationEntity.from_dict(res) for res in reservations
                ]
            return data

    def save(self):
        with self.lock:
            try:
                with open(self.file_path, "w", encoding=UTF8_ENCODING) as f:
                    json.dump(
                        {
                            user_id: [res.to_dict() for res in reservations]
                            for user_id, reservations in self.data.items()
                        },
                        f,
                        ensure_ascii=False,
                        indent=4,
                    )
                print(f"Data saved successfully to {self.file_path}")
            except Exception as e:
                print(f"Error saving file: {e}")

    def add(self, user_id: str, reservation: ReservationEntity):
        if user_id not in self.data:
            self.data[user_id] = []
        self.data[user_id].append(reservation)
        self.save()

    def get_reservations_by_user_id(self, user_id: str) -> list[ReservationEntity]:
        if user_id not in self.data:
            return []

        now = utils.now_kst()
        # 현재 시간보다 이전인 항목 제거
        self.data[user_id] = [res for res in self.data[user_id] if res.date > now]
        # 시간순으로 정렬
        self.data[user_id].sort(key=lambda res: res.date)
        return self.data[user_id]

    def delete(self, uuid: str):
        for user_id, reservations in self.data.items():
            self.data[user_id] = [res for res in reservations if res.uuid != uuid]
            if not self.data[user_id]:
                del self.data[user_id]
                break
        self.save()

    def reload(self):
        now = utils.now_kst()
        new_data = {
            user_id: [res for res in reservations if res.date > now]
            for user_id, reservations in self.data.items()
            if any(res.date > now for res in reservations)
        }

        self.data = new_data
        self.save()
