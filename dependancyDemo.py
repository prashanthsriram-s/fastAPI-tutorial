from typing import Annotated
from fastapi import FastAPI, Response, Query, Cookie, Body, Path, Depends
from pydantic import BaseModel, Required

app = FastAPI()



def query_string(q: str|None = None):
    return q

def query_or_cookie(q: Annotated[str|None, Depends(query_string)] = None,
                          last_q: Annotated[str|None, Cookie()] = None, response: Response = Required) ->str:
    if not q:
        return last_q
    response.set_cookie(key='last_q', value=q)
    return q

queryCookieStr = Annotated[str, Depends(query_or_cookie)]
    
@app.get("/item")
def read_stuff(stuff: queryCookieStr):
    return{
        'stuff': stuff
    }

# def query_extractor(q: str | None = None):
#     return q


# def query_or_cookie_extractor(
#     q: Annotated[str, Depends(query_extractor)],
#     last_query: Annotated[str | None, Cookie()] = None,
# ):
#     if not q:
#         return last_query
#     return q


# @app.get("/items/")
# async def read_query(
#     query_or_default: Annotated[str, Depends(query_or_cookie_extractor)]
# ):
#     return {"q_or_cookie": query_or_default}