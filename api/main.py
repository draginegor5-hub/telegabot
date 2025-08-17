from http.client import responses

from fastapi import FastAPI, HTTPException
import  database as db

from pydantic import BaseModel
from typing import Optional, List


class ApiResponse(BaseModel):
    result: str
    comment: str = ""
    data: Optional[List[dict]] = None

class User(BaseModel):

    id_user: str
    lastname: str | None = None
    firstname:str | None = None
    username:str | None = None


common_responses = {
    500: {
        "description": "Внутренняя ошибка сервера",
        "content": {"application/json": {"example": {"detail": "Ошибка подключения к СУБД"}}}
    },
    400: {
        "description": "Некорректный запрос",
        "content": {"application/json": {"example": {"detail": "Описание ошибки"}}}
    }
}


app = FastAPI(title="Telegram Users API", version="1.0"
)


@app.get("/telega/v1/users/", response_model=ApiResponse, responses={
        500: {
            "description": "Ошибка подключения к базе данных",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Ошибка подключения к СУБД"
                    }
                }
            }
        },
        404: {
            "description": "Пользователь не найден",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Пользователь не найден"
                    }
                }
            }
        }
    })
def app_get_users(id: str = 'all'):

    rez = db.get_users(id)

    if rez.result is False:
        raise HTTPException(
            status_code=500,
            detail="Ошибка подключения к СУБД"
        )
    if not rez.data:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )

    return ApiResponse(result="success", data = rez.data)



@app.post("/telega/v1/users/", response_model=ApiResponse, responses=common_responses)
def app_post_user(user: User):
    rez = db.create_user(user.id_user,user.firstname,user.lastname,user.username)

    if rez.result is False and rez.error_code == 3:
        raise HTTPException(
            status_code=500,
            detail="Ошибка подключения к СУБД"
        )
    if rez.result is False and rez.error_code == 2:
        raise HTTPException(
            status_code=400,
            detail=rez.comment
        )

    #response = {'result':"success", 'comment':"Пользователь id ="+user.id_user+" создан"}
    return  ApiResponse(result ="success", comment =  "Пользователь id ="+user.id_user+" создан")



@app.delete("/telega/v1/users/{id}",response_model=ApiResponse, responses=common_responses)
def app_delete_user(id:str):
    rez = db.delete_users(id)
    if rez.result is False and rez.error_code == 3:
        raise HTTPException(
            status_code=500,
            detail="Ошибка подключения к СУБД"
        )
    if rez.result is False and rez.error_code == 1:
        raise HTTPException(
            status_code=400,
            detail=rez.comment
        )

    #response = {'result':'success', 'comment':"Пользователь id ="+id+" удален"}
    return ApiResponse(result ="success", comment =  "Пользователь id ="+id+" удален")


@app.put("/telega/v1/users/", response_model= ApiResponse, responses=common_responses)
def app_put_user(user:User):
    rez = db.update_user(user.id_user,user.firstname, user.lastname, user.username)
    if rez.result is False and rez.error_code == 3:
        raise HTTPException(
            status_code=500,
            detail="Ошибка подключения к СУБД"
        )
    if rez.result is False and rez.error_code == 1:
        raise HTTPException(
            status_code=400,
            detail=rez.comment
        )


    #response = {'result': 'success', 'comment': "Пользователь id =" + user.id_user + " обновлен"}
    return ApiResponse(result ="success", comment =  "Пользователь id =" + user.id_user + " обновлен")




