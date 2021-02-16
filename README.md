# Test Work

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

### Installation

Install the dependencies

```sh
$ cd test_work_for_r
$ pip install -r requirements.txt
```

Initialize datebase and create user with all rights (test_user, test_password)
```sh
$ python init_db.py
```

Fill database from file example.cvs
```sh
$ python load_from_cvs.py
```

Start web service
```sh
$ python app.py
```
### API
##### User 
________
| Metod | URL |
| ------ | ------ |
| POST | /registration |
| POST | /login |
| POST | /token/refresh |

##### /registration
&nbsp;
```
{
    "username": "test_user",     
    "password": "test_password",
    "product_group_ids": [1, 2] //identifiers of product groups that are available to the user
}
```
##### /login
&nbsp;
```
{
    "username": "test_user",     
    "password": "test_password",
}
```
##### response:
&nbsp;
```
{
    "msg": "User test_user was created",
    "access_token": "", //use this token for authentication
    "refresh_token": ""
}
```

Use access_token in request headers:
```
 Authorization: Bearer *access_token*
```
_______
##### Product Group
____
| Metod | URL |
| ------ | ------ |
| GET | /product_groups |
| GET | /product_groups/{id} |
| POST | /product_groups |
| PUT | /product_groups/{id} |
| DELETE | /product_groups/{id} |

#### POST/PUT body
```
{
    "title": "group1",
    "parent_id": null,
    "children": [
        {
            "title": "group2",
            "children": []
        }
    ]
}
```
_______
##### Product Group
____
| Metod | URL |
| ------ | ------ |
| GET | /products |
| GET | /products/{id} |
| POST | /products |
| PUT | /products/{id} |
| DELETE | /products/{id} |

#### POST/PUT body
```
{
    "id": 4,
    "title": "art6",
    "product_group_id": 2
}
```
