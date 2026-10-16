import warnings
from pathlib import Path

import openpyxl
from sqlalchemy import select

warnings.filterwarnings("ignore", message="Data Validation extension")

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "BB - Database.xlsx"


def load_sheet(name: str):
    return openpyxl.load_workbook(DATA_FILE, data_only=True)[name]


def get_or_create(db, model, name: str, **fields):
    obj = db.scalar(select(model).where(model.name == name))
    if obj is None:
        obj = model(name=name, **fields)
        db.add(obj)
        db.flush()
    else:
        for key, value in fields.items():
            setattr(obj, key, value)
    return obj


def upsert(db, model, keys: dict, **fields):
    stmt = select(model)
    for column, value in keys.items():
        stmt = stmt.where(getattr(model, column) == value)
    obj = db.scalar(stmt)
    if obj is None:
        obj = model(**keys, **fields)
        db.add(obj)
        db.flush()
    else:
        for column, value in fields.items():
            setattr(obj, column, value)
    return obj

