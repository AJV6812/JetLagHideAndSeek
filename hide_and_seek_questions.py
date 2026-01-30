import configparser

from hide_and_seek_interfaces import Question, QuestionInstance

par = configparser.ConfigParser()
par.read("hide_and_seek.cfg")

DEFAULT_ALLOCATED_PHOTO_TIME = par.getint("MASTER", "DEFAULT_ALLOCATED_PHOTO_TIME")
TENTACLES_DISTANCE = par.getint("MASTER", "TENTACLES_DISTANCE")


class MeasuringQuestion(Question):
    def __init__(self, location: str):
        self.location = location

    def get_short_question(self):
        return self.location

    def get_full_question(self) -> str:
        return f"Are you closer to a {self.get_short_question()} compared to me?"

    def get_options(self) -> list[str]:
        return ["CLOSER", "FURTHER", "NULL"]

    def get_reward(self) -> tuple[int, int]:
        return (3, 1)

    def to_instance(self, user_input: str) -> QuestionInstance:
        return MeasuringQuestionInstance(self.location, user_input)


class MeasuringQuestionInstance(MeasuringQuestion, QuestionInstance):
    def __init__(self, location: str, user_input: str):
        self.user_input = user_input
        super().__init__(location)

    def get_user_input(self) -> str:
        return self.user_input

    def get_full_question(self) -> str:
        return f"Is your closest {self.get_short_question()} closer than {self.get_user_input()}km\n({super().get_full_question()})"


class MatchingQuestion(Question):
    def __init__(self, location: str):
        self.location = location

    def get_short_question(self):
        return self.location

    def get_full_question(self) -> str:
        return f"Is your closest {self.get_short_question()} the same as mine?"

    def get_options(self) -> list[str]:
        return ["YES", "NO", "NULL"]

    def get_reward(self) -> tuple[int, int]:
        return (3, 1)

    def to_instance(self, user_input: str) -> QuestionInstance:
        return MatchingQuestionInstance(self.location, user_input)


class MatchingQuestionInstance(MatchingQuestion, QuestionInstance):
    def __init__(self, location: str, user_input: str):
        self.user_input = user_input
        super().__init__(location)

    def get_user_input(self) -> str:
        return self.user_input

    def get_full_question(self) -> str:
        return f"Is {self.get_user_input()} your closest {self.get_short_question()}?\n({super().get_full_question()})"


class TentaclesQuestion(Question):
    def __init__(self, location_type: str):
        self.location_type = location_type
        self.tentacle_distance: int = TENTACLES_DISTANCE

    def get_short_question(self):
        return self.location_type

    def get_full_question(self) -> str:
        return f"Which {self.get_short_question()} within {self.tentacle_distance}km of me are you closest to? (Fails if hider is further than {self.tentacle_distance}km)."

    def get_reward(self) -> tuple[int, int]:
        return (4, 2)

    def to_instance(self, user_input: str) -> QuestionInstance:
        return TentaclesQuestionInstance(self.location_type, user_input)


class TentaclesQuestionInstance(TentaclesQuestion, QuestionInstance):
    def __init__(self, location: str, user_input: str):
        self.user_input: list[str] = [x.strip() for x in user_input.split(",")]
        super().__init__(location)

    def get_user_input(self) -> str:
        return ", ".join(self.user_input)

    def get_options(self) -> list[str]:
        return ["OUT OF RANGE", "NULL"] + self.user_input


class RadarQuestion(Question):
    def __init__(self, distance_km: float):
        self.distance_km = distance_km

    def get_short_question(self):
        return f"{self.distance_km}km"

    def get_full_question(self) -> str:
        return f"Are you within {self.get_short_question()} of the seekers?"

    def get_reward(self) -> tuple[int, int]:
        return (2, 1)

    def to_instance(self, user_input: str) -> QuestionInstance:
        assert user_input == ""
        return RadarQuestionInstance(self.distance_km)

    def get_options(self) -> list[str]:
        return ["HIT", "MISS", "NULL"]


class RadarQuestionInstance(RadarQuestion, QuestionInstance):
    def get_user_input(self) -> str:
        return ""


class ThermometerQuestion(Question):
    def __init__(self, min_dist_km: float):
        self.min_dist_km = min_dist_km

    def get_short_question(self):
        return f"{self.min_dist_km}km"

    def get_full_question(self) -> str:
        return f"After travelling {self.get_short_question()} am I warmer or colder?"

    def get_reward(self) -> tuple[int, int]:
        return (2, 1)

    def to_instance(self, user_input: str) -> QuestionInstance:
        return ThermometerQuestionInstance(self.min_dist_km, user_input)

    def get_options(self) -> list[str]:
        return ["WARMER", "COLDER", "NULL"]


class ThermometerQuestionInstance(ThermometerQuestion, QuestionInstance):
    def __init__(self, distance_km: float, user_input: str):
        self.user_input: list[str] = [x.strip() for x in user_input.split(",")]
        assert len(user_input) == 2
        super().__init__(distance_km)

    def get_user_input(self) -> str:
        return ", ".join(self.user_input)

    def get_full_question(self) -> str:
        return f"The seekers have moved from {self.user_input[0]} to {self.user_input[1]}. Are they warmer or colder? ({super().get_full_question()})"


class PhotoQuestion(Question):
    def __init__(self, photo_type: str):
        self.photo_type = photo_type

    def get_short_question(self):
        return self.photo_type

    def get_allocated_time(self) -> int:
        return DEFAULT_ALLOCATED_PHOTO_TIME

    def get_full_question(self) -> str:
        return f"Send a photo of {self.get_short_question()}."

    def get_reward(self) -> tuple[int, int]:
        return (1, 1)

    def to_instance(self, user_input: str) -> QuestionInstance:
        assert user_input == ""
        return PhotoQuestionInstance(self.photo_type)

    def get_options(self) -> list[str]:
        return ["PHOTO SENT", "NULL"]


class PhotoQuestionInstance(PhotoQuestion, QuestionInstance):
    def get_user_input(self) -> str:
        return ""


class QuestionManager:
    def __init__(self):
        self.questions: list[Question] = []
        self.questions += (
            [
                MatchingQuestion(x)
                for x in [
                    "Commercial Airport",
                    "Transit Line",
                    "Station Name Length",
                    "Local Council Area",
                    "Suburb",
                    "Park",
                    "Amusement Park",
                    "Zoo",
                    "Aquarium",
                    "Golf Course",
                    "Museum",
                    "Movie Theatre",
                    "Hospital",
                    "Library",
                    "Foreign Consulate",
                ]
            ]
            + [
                MeasuringQuestion(x)
                for x in [
                    "Commercial Airport",
                    "Rail station",
                    "Local Council Border",
                    "Suburb Border",
                    "Body of Water",
                    "Coastline",
                    "Park",
                    "Amusement Park",
                    "Zoo",
                    "Aquarium",
                    "Golf Course",
                    "Museum",
                    "Movie Theatre",
                    "Hospital",
                    "Library",
                    "Foreign Consulate",
                ]
            ]
            + [RadarQuestion(x) for x in [0.5, 1, 2, 5, 10, 15, 40, 80, 160]]
            + [ThermometerQuestion(x) for x in [1, 5, 15]]
            + [
                TentaclesQuestion(x)
                for x in ["Museums", "Libraries", "Movie Theatres", "Hospitals"]
            ]
            + [
                PhotoQuestion(x)
                for x in [
                    "a tree",
                    "the sky",
                    "you",
                    "widest street",
                    "tallest structure in your sightline",
                    "any building visible from the station",
                    "tallest building visible from the station",
                    "trace nearest path or street",
                    "two buildings",
                    "restaurant interior",
                    "park",
                    "grocery store aisle",
                ]
            ]
        )

    def get_possible_questions(self) -> set[Question]:
        return set(self.questions)

    def get_questions_of_type(self, question_type: Question.__class__) -> set[Question]:
        return set(
            [x for x in self.get_possible_questions() if isinstance(x, question_type)]
        )
