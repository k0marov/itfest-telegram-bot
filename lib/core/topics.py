"""Module that provides the topic class, list of supported topics, and topic helper functions"""
from dataclasses import dataclass
@dataclass(frozen=True)
class Topic:
    """Class that contains details about the topic"""
    id: str
    description: str
    hashtag: str
    vk_str_id: str
    vk_num_id: str

# some of the topics are from the same group (nauchim.online),
# so we should only display their posts if the posts contain the specific hashtag (e.g #VRARFest3D),
# otherwise duplicate posts will be sent to users
# this constant will help in implementing this check
BASE_TOPIC_STR_ID = "nauchim.online"

TOPICS_LIST = [
    Topic(
        "1",
        "Международный конкурс детских инженерных команд",
        "#Technocom",
        "technocom2022",
        "210998761",
    ),
    Topic(
        "2",
        "Международный фестиваль информационных технологий «IT-фест»",
        "#IT-fest_2022",
        "itfest2022",
        "210985709"
    ),
    Topic(
        "3",
        "Международный аэрокосмический фестиваль",
        "#IASF2022",
        "aerospaceproject",
        "196557207",
    ),
    Topic(
        "4",
        "Всероссийский фестиваль общекультурных компетенций",
        "#ФестивальОКК",
        "okk_fest",
        "211638918",
    ),
    Topic(
        "5",
        "Всероссийский фестиваль нейротехнологий «Нейрофест»",
        "#Нейрофест",
        "neurofest2022",
        "211803420",
    ),
    Topic(
        "6",
        "Всероссийский конкурс по микробиологии «Невидимый мир»",
        "#НевидимыйМир",
        "nauchim.online",
        "200248443",
    ),
    Topic(
        "7",
        "Всероссийский конкурс научно-исследовательских работ",
        "#КонкурсНИР",
        "nauchim.online",
        "200248443",
    ),
    Topic(
        "8",
        "Международный фестиваль 3D- моделирования и программирования VRAR-Fest",
        "#VRARFest3D",
        "nauchim.online",
        "200248443",
    )
]
TOPICS_MAP = {
    topic.id: topic
        for topic in TOPICS_LIST
}
def get_topic_by_id(topic_id: str) -> Topic:
    """Returns topic that has the given id"""
    return TOPICS_MAP[topic_id]
