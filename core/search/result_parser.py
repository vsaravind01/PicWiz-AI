from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, List, Dict

from models.tables import Album, Photo


class ResultParser(ABC):
    def __init__(self):
        self.entity_results = defaultdict(list)

    @abstractmethod
    def parse(self, results: Any, search_terms: List[str]) -> None:
        pass

    @abstractmethod
    def get_photos(self, search_term: str) -> List[Photo]:
        pass


class PeopleResultParser(ResultParser):
    def parse(self, results: Dict[str, Any], search_term: str) -> None:
        for person_id, photos in results.items():
            if search_term.lower() in person_id.lower():
                self.entity_results[search_term.lower()].append(
                    {
                        "id": person_id,
                        "photos": photos,
                    }
                )

    def get_photos(self, search_term: str) -> List[Photo]:
        if search_term.lower() not in self.entity_results:
            return []
        return [
            Photo(**photo)
            for records in self.entity_results[search_term.lower()]
            for photo in records["photos"]
        ]


class PhotoResultParser(ResultParser):
    def parse(self, results: List[Photo], search_term: str) -> None:
        for photo in results:
            if search_term.lower() in photo.entities:
                self.entity_results[search_term.lower()].append(
                    {
                        "id": photo.id,
                        "uri": photo.uri,
                        "owner_id": photo.owner_id,
                        "objects": photo.objects,
                        "scenes": photo.scenes,
                        "entities": photo.entities,
                        "datastore": photo.datastore,
                    }
                )

    def get_photos(self, search_term: str) -> List[Photo]:
        if search_term.lower() not in self.entity_results:
            return []
        return [Photo(**photo) for photo in self.entity_results[search_term.lower()]]


class AlbumResultParser(ResultParser):
    def parse(self, results: List[Album], search_terms: List[str]) -> None:
        for album in results:
            for term in search_terms:
                if term in album.name:
                    self.entity_results[term].append(
                        {
                            "id": album.id,
                            "name": album.name,
                            "description": album.description,
                            "cover": album.cover,
                        }
                    )

    def get_photos(self, search_term: str) -> List[Photo]:
        # TODO: For albums, we might have to fetch the photos associated with each album
        return []
