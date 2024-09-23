from abc import ABC, abstractmethod
from typing import Any
from models import User
from core.search.result_parser import (
    PeopleResultParser,
    PhotoResultParser,
    AlbumResultParser,
    ResultParser,
)


class EntitySearcher(ABC):
    @abstractmethod
    async def search(self, query: dict[str, Any], user: User) -> ResultParser:
        pass


class PeopleSearcher(EntitySearcher):
    def __init__(self, person_handler):
        self.person_handler = person_handler
        self.result_parser = PeopleResultParser()

    async def search(self, query: dict[str, Any], user: User) -> ResultParser:
        person_names = query.get("entities", [])
        if "<me>" in person_names:
            person_names.remove("<me>")
            person_names.append(user.name)
        results = await self.person_handler.search_by_name(person_names, user)
        self.result_parser.parse(results, person_names)
        return self.result_parser


class PhotoSearcher(EntitySearcher):
    def __init__(self, photo_handler):
        self.photo_handler = photo_handler
        self.result_parser = PhotoResultParser()

    async def search(self, query: dict[str, Any], user: User) -> ResultParser:
        search_terms = query.get("entities", [])
        results = await self.photo_handler.search_by_terms(search_terms, user)
        self.result_parser.parse(results, search_terms)
        return self.result_parser


class AlbumSearcher(EntitySearcher):
    def __init__(self, album_handler):
        self.album_handler = album_handler
        self.result_parser = AlbumResultParser()

    async def search(self, query: dict[str, Any], user: User) -> ResultParser:
        # TODO: Need to find a way to search albums effectively
        # For now, we can just map the photos to albums with minimum #photos threshold
        album_names = query.get("description", [])
        results = await self.album_handler.search_by_description(album_names, user)
        self.result_parser.parse(results, album_names)
        return self.result_parser


class DatabaseOperations:
    def __init__(self):
        self.searchers: dict[str, EntitySearcher] = {}

    def register_searcher(self, entity_types: list[str], searcher: EntitySearcher):
        for entity_type in entity_types:
            self.searchers[entity_type] = searcher

    async def search_database(
        self, parsed_query: dict[str, Any], user: User, **kwargs
    ) -> dict[str, Any]:
        entities = parsed_query.get("entities", {"people": [], "objects": [], "locations": []})
        query = parsed_query.get("query", {})

        results = {"photos": {}, "entities": {}}
        for entity_type, entity_names in entities.items():
            for entity in entity_names:
                searcher = self.searchers[entity_type]
                entity_results = await searcher.search({"entities": entity}, user)
                entity_photos = entity_results.get_photos(entity)
                if entity_photos:
                    if entity not in results["entities"]:
                        results["entities"][entity] = []
                    results["entities"][entity].extend([photo.id for photo in entity_photos])
                    for photo in entity_photos:
                        if photo.id not in results["photos"]:
                            results["photos"][photo.id] = photo

        filtered_results = self._apply_query(results, query)

        return filtered_results

    def _apply_query(self, results: dict[str, Any], query: dict[str, Any]) -> dict[str, Any]:
        if not query:
            return results

        return self._process_query(results, query)

    def _process_query(self, results: dict[str, Any], query: dict[str, Any]) -> dict[str, Any]:
        operator = list(query.keys())[0]
        if operator == "$and":
            return self._process_and(results, query["$and"])
        elif operator == "$or":
            return self._process_or(results, query["$or"])
        elif operator == "$not":
            return self._process_not(results, query["$not"])
        else:
            entity = list(query.values())[0]
            return {
                "photos": {
                    photo_id: results["photos"][photo_id]
                    for photo_id in results["entities"].get(entity, [])
                },
                "entities": {entity: results["entities"].get(entity, [])},
            }

    def _process_and(
        self, results: dict[str, Any], conditions: list[dict[str, Any]]
    ) -> dict[str, Any]:
        filtered_photo_ids = None
        for condition in conditions:
            condition_results = self._process_query(results, condition)
            condition_photo_ids = set(condition_results["photos"].keys())
            if filtered_photo_ids is None:
                filtered_photo_ids = condition_photo_ids
            else:
                filtered_photo_ids &= condition_photo_ids

        if filtered_photo_ids is None:
            return {"photos": {}, "entities": {}}

        return {
            "photos": {photo_id: results["photos"][photo_id] for photo_id in filtered_photo_ids},
            "entities": {
                entity: [photo_id for photo_id in photo_ids if photo_id in filtered_photo_ids]
                for entity, photo_ids in results["entities"].items()
            },
        }

    def _process_or(
        self, results: dict[str, Any], conditions: list[dict[str, Any]]
    ) -> dict[str, Any]:
        filtered_photo_ids = []
        for condition in conditions:
            condition_results = self._process_query(results, condition)
            for photo_ids in condition_results["photos"].values():
                filtered_photo_ids.extend(
                    [photo_id for photo_id in photo_ids if photo_id not in filtered_photo_ids]
                )
        return {
            "photos": {photo_id: results["photos"][photo_id] for photo_id in filtered_photo_ids},
            "entities": {
                entity: [photo_id for photo_id in photo_ids if photo_id in filtered_photo_ids]
                for entity, photo_ids in results["entities"].items()
            },
        }

    def _process_not(self, results: dict[str, Any], condition: dict[str, Any]) -> dict[str, Any]:
        excluded_results = self._process_query(results, condition)
        excluded_photo_ids = set(excluded_results["photos"].keys())
        all_photo_ids = set(results["photos"].keys())
        filtered_photo_ids = all_photo_ids - excluded_photo_ids
        return {
            "photos": {photo_id: results["photos"][photo_id] for photo_id in filtered_photo_ids},
            "entities": {
                entity: [photo_id for photo_id in photo_ids if photo_id in filtered_photo_ids]
                for entity, photo_ids in results["entities"].items()
            },
        }
