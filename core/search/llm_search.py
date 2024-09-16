import os
import json

import cohere
from db.mongo_connect import MongoConnection, MongoCollections
from db.qdrant_connect import QdrantConnection, QdrantCollections
from core.embed.clip import get_clip_embedding
from models.person import PersonResponse
from models.photo import Photo

from enum import Enum

from models import person, photo
from models.user import User

COHERE_API_KEY = os.environ.get("COHERE_API_KEY")


class FewshotPromptOptions(Enum):
    GENERAL_QUERY = """Extract the person names, place, objects and a short description from the GIVEN QUERY and return them as a json output. 
And identify the type of task to be done. Choose tasks only from (GENERATE, FIND, MATCH).
If the context refers to the first person, then add "<me>" in the person_names list.
If you are unable to find any of the classes, use empty array for the class.
The description should be generated only when a suitable description can a made, if not keep description as None.
The place should not mention a named location. Instead it should be general. For example, louvre meseum or louvre should be just "museum".
Include additional similar words in each class for places and objects.
The description should be simple english in 1-2 lines and it will be used for image retrieval search.
Use the EXAMPLE SCENARIOS as examples,

EXAMPLE SCENARIOS:
1 - Show all the photos of bob, jack and aravind.
Output:
{
"person_names": ["bob", "jack", "aravind"],
"objects": [],
"places": [],
"task": "fetch",
"description": "None"
}
2 - Generate an photo album with my beach photos with aravind
Output
{
"person_names": ["<me>", "aravind"],
"objects":[],
"places": ["beach", "sea", "ocean", "lighthouse"],
"task": "generate",
"description": "People having fun at the beach, creating unforgettable memories with friends"
}
3 - Get all my photos standing near a bike
Output
{"person_names": ["<me>"],
"objects": ["bike", "motorcycle", "bicycle"],
"places": [],
"task": "fetch",
"description": "People standing near a bicycle"
}
4 - an album with me and sandeep
{
  "person_names": ["<me>", "sandeep"],
  "objects": [],
  "places": [],
  "task": "fetch",
  "description": "None"
}"""

    def generate_prompt(self, query: str):
        return self.value + "\n\n" + "GIVEN TEXT: " + query


class CohereSearch:
    def __init__(self, user: User, model: str = "command-r"):
        self.model = model
        self.user = user
        self.client = cohere.Client(api_key=COHERE_API_KEY)

    def search(
        self, query: str, prompt_type: FewshotPromptOptions = FewshotPromptOptions.GENERAL_QUERY
    ) -> dict:
        prompt = prompt_type.generate_prompt(query)
        response = self.client.chat(model=self.model, message=prompt, response_format={"type": "json_object"})  # type: ignore

        content = json.loads(response.text)
        places = content.get("places", [])
        objects = content.get("objects", [])
        person_names = content.get("person_names", [])
        task = content.get("task", "fetch")
        description = content.get("description", None)

        if description:
            embedding1 = get_clip_embedding(query)
            embedding2 = get_clip_embedding(description)

        with QdrantConnection(collection=QdrantCollections.CLIP_EMBEDDINGS) as conn:
            results1 = conn.search(embedding1, top_k=10)
            results2 = conn.search(embedding2, top_k=10)

        results = results1 + results2
        seen = set()
        results = [x for x in results if not (x["id"] in seen or seen.add(x["id"]))]

        with MongoConnection(collection=MongoCollections.PERSON) as conn:
            persons_response = []
            for name in person_names:
                response = conn.find_many(
                    {"name": {"$regex": name, "$options": "i"}, "owner": self.user.id}
                )
                for res in response:
                    persons_response.append(PersonResponse(**res).model_dump())

        with MongoConnection(collection=MongoCollections.PHOTO) as conn:
            obj_response = []
            if objects:
                re_q = [{"entities": {"$regex": term, "$options": "i"}} for term in objects]
                photos = conn.find_many({"$or": re_q, "owner": self.user.id})
                for photo in photos:
                    obj_response.append(Photo(**photo).model_dump())

            place_response = []
            if places:
                re_q = [{"entities": {"$regex": term, "$options": "i"}} for term in places]
                photos = conn.find_many({"$or": re_q, "owner": self.user.id})
                for photo in photos:
                    place_response.append(Photo(**photo).model_dump())

        return {
            "person": persons_response,
            "places": place_response,
            "objects": obj_response,
            "task": task,
            "results": results,
        }
