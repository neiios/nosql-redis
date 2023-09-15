import redis
from defaults import default_rooms


class Hotel:
    def __init__(self, hotel_name: str) -> None:
        self.r = redis.Redis(decode_responses=True, protocol=3)
        self.r.flushdb()  # TODO: Remove when done
        self.hotel_name = hotel_name

        for room in default_rooms:
            key = f"{self.hotel_name}:room:{room['room_id']}"
            self.r.hset(key, mapping=room["reservation"])

    def add_room(self, room_id: int) -> None:
        key = f"{self.hotel_name}:room:{room_id}"
        self.r.hsetnx(key, "booked", 0)

    def remove_room(self, room_id: int) -> None:
        key = f"{self.hotel_name}:room:{room_id}"
        self.r.delete(key)

    def reserve_room(
        self,
        room_id: int,
        name: str,
        start_date: str,
        end_date: str,
    ) -> None:
        key = f"{self.hotel_name}:room:{room_id}"
        pipeline = self.r.pipeline()
        pipeline.watch(key)

        status = pipeline.hget(key, "booked")
        if status == "0":
            pipeline.multi()
            pipeline.hset(
                key,
                mapping={
                    "booked": 1,
                    "name": name,
                    "start_date": start_date,
                    "end_date": end_date,
                },
            )
            pipeline.execute()
        else:
            print(f"Room {room_id} is already reserved.")

    def remove_reservation(self, room_id: int) -> None:
        key = f"{self.hotel_name}:room:{room_id}"
        pipeline = self.r.pipeline()
        pipeline.watch(key)

        status = pipeline.hget(key, "booked")
        if status == "1":
            pipeline.multi()
            pipeline.delete(key)
            pipeline.hset(key, "booked", 0)
            pipeline.execute()
        else:
            print(f"Room {room_id} wasn't booked to begin with.")


def main() -> None:
    hotel = Hotel("trivago")
    hotel.add_room(404)
    hotel.add_room(405)
    hotel.remove_room(405)
    hotel.reserve_room(103, "Jeffrey Epstein", "2019-08-09", "2019-08-10")
    hotel.reserve_room(101, "Joe Biden", "2019-08-09", "2019-08-10")
    hotel.remove_reservation(103)
    hotel.remove_reservation(102)
    hotel.reserve_room(103, "Joe Biden", "2019-08-09", "2019-08-10")


if __name__ == "__main__":
    main()
