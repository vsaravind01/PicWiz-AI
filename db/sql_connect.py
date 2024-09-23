from __future__ import annotations

import uuid
from typing import Any, Literal, Optional

from sqlalchemy import Delete, Select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import InstrumentedAttribute
from sqlmodel import SQLModel, Session, select, delete, func

from db import DBConnection, SqlDatabaseManager
from db.errors import DBDuplicateKeyError
from db.config import Entity


class SqlConnection(DBConnection):
    def __init__(self, entity: Entity) -> None:
        super().__init__(entity)
        self.model = entity.get_class()

    def connect(self):
        return self

    def close(self):
        pass

    def apply_operator(self, query, key: str | InstrumentedAttribute, condition: tuple) -> Select:
        column = (
            key if isinstance(key, InstrumentedAttribute) else getattr(self.model, key)
        )
        if isinstance(condition, tuple) and len(condition) == 2:
            operator, value = condition
            if operator == "==":
                return query.where(column == value)
            elif operator == "!=":
                return query.where(column != value)
            elif operator == ">":
                return query.where(column > value)
            elif operator == "<":
                return query.where(column < value)
            elif operator == ">=":
                return query.where(column >= value)
            elif operator == "<=":
                return query.where(column <= value)
            elif operator == "in":
                return query.where(column.in_(value))
            elif operator == "like":
                return query.where(column.like(value))
            elif operator == "ilike":
                return query.where(column.ilike(value))
            elif operator == "contains":
                return query.where(column.contains(value))
            elif operator == "icontains":
                return query.where(column.icontains(value))
            else:
                raise ValueError(f"Operator {operator} not supported")
        else:
            return query.where(column == condition)

    def apply_fields(
        self, model: SQLModel, fields: Optional[dict] = None
    ) -> list[InstrumentedAttribute]:
        model_columns = model.__table__.columns.keys()  # type: ignore

        if not fields:
            return [getattr(model, key) for key in model_columns]

        values = set(fields.values())
        if values - {0, 1}:
            raise ValueError("Fields values should be either 0 or 1")

        if 1 in values:
            return [getattr(model, key) for key, value in fields.items() if value == 1]
        elif 0 in values:
            return [
                getattr(model, key)
                for key in model_columns
                if key not in fields or fields[key] != 0
            ]
        else:
            return [getattr(model, key) for key in model_columns]

    def generate_statement_from_query(
        self,
        query: dict,
        fields: Optional[dict] = None,
        operation: Literal["select", "delete"] = "select",
    ) -> tuple[list[InstrumentedAttribute], Select | Delete]:
        columns_to_select = self.apply_fields(self.model, fields)  # type: ignore

        if operation == "select":
            statement = select(*columns_to_select)
        elif operation == "delete":
            statement = delete(self.model)
        else:
            raise ValueError(f"Operation {operation} not supported")

        for key, condition in query.items():
            column = getattr(self.model, key)
            if column in columns_to_select:
                statement = self.apply_operator(statement, column, condition)

        return columns_to_select, statement

    def insert(self, data: dict):
        try:
            model = self.model(**data)
            with SqlDatabaseManager() as db:
                db.add(model)
                db.commit()
                db.refresh(model)
        except IntegrityError as e:
            raise DBDuplicateKeyError(e)

    def insert_many(self, data: list[dict]):
        models = [self.model(**item) for item in data]
        with SqlDatabaseManager() as db:
            db.add_all(models)
            db.commit()

    def find(
        self,
        query: dict,
        fields: dict = dict(),
        limit: int = 100,
        page: int = 0,
    ):
        columns, statement = self.generate_statement_from_query(query, fields, "select")
        statement = statement.limit(limit).offset(page * limit)  # type: ignore

        with SqlDatabaseManager() as db:
            temp = db.exec(statement).all()  # type: ignore

        result = []
        for item in temp:
            if isinstance(item, list):
                print(item)
                result.append(item)
            else:
                result.append({column.name: getattr(item, column.name) for column in columns})
        return result

    def find_by_id(self, id: uuid.UUID) -> Optional[SQLModel]:
        with SqlDatabaseManager() as db:
            return db.get(self.model, id)

    def count(self, query: dict):
        statement = self.generate_statement_from_query(query)
        with SqlDatabaseManager() as db:
            return db.exec(func.count(statement))  # type: ignore

    def update(self, query: dict, data: dict, override_set: bool = False):
        with SqlDatabaseManager() as db:
            statement = db.query(self.model).filter_by(**query)
            result = statement.update(data, synchronize_session=False)
            db.commit()
            return result

    def delete(self, query: dict):
        columns, statement = self.generate_statement_from_query(
            query, operation="delete"
        )
        statement = statement.returning(*columns)  # type: ignore
        with SqlDatabaseManager() as db:
            result = db.exec(statement).all()  # type: ignore
            db.commit()
            return len(result)

    @staticmethod
    def execute(statement: Any):
        with SqlDatabaseManager() as db:
            return db.exec(statement)

    @property
    def session(self) -> Session:
        return SqlDatabaseManager().session()

    def join_query(
        self,
        main_entity: Entity,
        join_entities: list[tuple[tuple[Entity, str], tuple[Entity, str]]],
        conditions: dict,
        fields: Optional[dict] = None,
        limit: int = 100,
        page: int = 0,
        select_from: Optional[SQLModel] = None,
    ):
        main_model = main_entity.get_class()
        select_fields = self.apply_fields(main_model, fields)  # type: ignore

        statement = select(*select_fields)
        if select_from:
            statement = statement.select_from(select_from)  # type: ignore

        join_models = {main_entity: main_model}

        for (join_entity, right_key), (from_entity, left_key) in join_entities:
            join_model = join_entity.get_class()
            join_models[join_entity] = join_model
            from_model = join_models[from_entity]

            statement = statement.join(
                join_model, getattr(from_model, left_key) == getattr(join_model, right_key)
            )

            if fields:
                select_fields.extend(self.apply_fields(join_model, fields))  # type: ignore

        for key, value in conditions.items():
            for model in join_models.values():
                if hasattr(model, key):
                    statement = statement.where(getattr(model, key) == value)
                    break

        skip = page * limit
        statement = statement.offset(skip).limit(limit)  # type: ignore

        with SqlDatabaseManager() as db:
            result = db.exec(statement).all()

        return [
            {
                column.name: getattr(item, column.name, None)
                for column in select_fields
                if hasattr(item, column.name)
            }
            for item in result
        ]
