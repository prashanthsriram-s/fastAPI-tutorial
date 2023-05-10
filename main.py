from typing import Annotated
from fastapi import FastAPI, Query, Depends, Path, Body, Response, HTTPException
from pydantic import BaseModel, Required
from enum import Enum

app = FastAPI()


class ModelName(str, Enum):
    alexnet = 'alexnet'
    resnet  = 'resnet'
    lenet   = 'lenet'

class Item(BaseModel):
    name : str
    price: int
    desc: str | None

items :list[Item]= []

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}




# @app.get("/item/naan")
# def read_just_item():
#     return {"message": "Just an item"}


def common_parameters(*,q: str|None = None, id: int = 0, tax: int = 0  ):
    if q:
        return {
            'q': q,
            'id': id,
            'tax': tax
        }
    else:
        return {
            'id': id,
            'tax': tax
        }


@app.get("/item/{item_id}")
def read_item(item_id: int):
    if(item_id < len(items)):
        return {"item_id": item_id, "item": items[item_id]}
    else: return {'message': 'error'}

@app.get('/model/{model_name}')
def read_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return 'Alex'
    elif model_name is ModelName.resnet:
        return 'res'
    elif model_name is ModelName.lenet:
        return 'le'
    
@app.post("/item/")
def write_item(item: Item):
    items.append(item)
    return {'item_id': len(items)-1, "item": item}

@app.get("/items")
def read_items(q: Annotated[str| None, Query(max_length=30)] = None):
    if not q:return items
    return {
        'q': q,
        "items": items
    }

@app.get("/testDependency")
def read_stuff(commons: Annotated [dict, Depends(common_parameters)]):
    return commons

class DerivedModel(BaseModel):
    int1: int
    int2: int
    string: str|None = None

class Dependable:
    def __init__(self, q: str|None = None, skip: int=0, limit:int=10) -> None:
        self.q = q
        self.skip = skip
        self.limit = limit

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/testCustomClassDep")
def use_class_dep(params: Annotated[Dependable, Depends(Dependable)]):
    response = dict()
    if params.q:
        response.update({'q': params.q})
    itemsToConsider = fake_items_db[params.skip: params.skip + params.limit]
    response.update({'items': itemsToConsider})
    return response


@app.post("/testAll/{path_id}", response_model=None)
def read_all(
    path_id : Annotated[int, Path(gt=0)],
    query_string: Annotated[str|None, Query(alias='query-string', min_length=3, max_length=30)] = None,
    request_body: Annotated[DerivedModel, Body()] = Required
):
    if path_id > 10:
        raise HTTPException(status_code=404, detail='No such path')
    if query_string:
        return {
        'path_id': path_id,
        'q': query_string,
        'request': request_body
        }
    else:
        return {
        'path_id': path_id,
        'request': request_body
        }


    
