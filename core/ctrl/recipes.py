from bson.objectid import ObjectId
from core import app, data, utils


def list_recipes(filter_data):
    finder = {
        'collection': 'recipes',
        'filter': filter_data,
    }
    return data.ex(finder)


def load_recipe(filter_data):
    finder = {
        'collection': 'recipes',
        'filter': filter_data
    }
    return data.one(finder)


def modify(recipe_data):
    result = validator(recipe_data)

    if 'id' not in recipe_data.keys():
        result['message'] = 'Need id to modify recipe'
        result['status'] = False

    if len(str(recipe_data['id'])) != 24:
        result['message'] = 'Recipe id is invalid'
        result['status'] = False

    if result['status'] == True:

        finder = load_recipe({
            '$and': [
                {
                    '$or': [
                        {'name': recipe_data['name']},
                        {'content': recipe_data['content']}
                    ],
                },
                {
                    '_id': {
                        '$ne': ObjectId(recipe_data['id'])
                    }
                }
            ]
        })

        modify_recipe = load_recipe({
            '_id': ObjectId(recipe_data['id'])
        })

        if type(finder) is not dict and type(modify_recipe) is dict:
            _id = recipe_data.pop('id', None)
            recipe_data.pop('creator', None)
            recipe_data.pop('created_at', None)

            recipe = dict()
            recipe.update(modify_recipe)
            recipe.update(recipe_data)

            recipe['updated_at'] = utils.now()

            recipes = app.db['recipes']

            recipe = recipe_model(recipe)
            recipes.update_one({'_id': ObjectId(_id)}, {'$set': recipe})

            result['status'] = True
            result['message'] = f"Recipe {recipe['name']} modified"

        else:
            param_found = ''
            if finder['name'] == recipe_data['name']:
                param_found = f"with name {recipe_data['name']}"
            if len(param_found) == 0 and finder['content'] == recipe_data['content']:
                param_found = f"with same content"

            result['status'] = False
            result['message'] = f"Recipe {param_found} already exists"

    return result


def insert(recipe_data):
    result = validator(recipe_data)

    if result['status'] == True:

        recipe = recipe_model(recipe_data)

        finder = load_recipe({
            '$or': [
                {'name': recipe['name']},
                {'content': recipe['content']}
            ]
        })

        if type(finder) is not dict:

            recipe_data.pop('id', None)
            recipe_data.pop('updated_at', None)

            recipe['created_at'] = utils.now()
            recipe['creator'] = app.config['user']['_id']

            recipes = app.db['recipes']
            recipes.insert_one(recipe)
            result['status'] = True
            result['message'] = f"Recipe {recipe['name']} created"
        else:

            param_found = ''
            if finder['name'] == recipe['name']:
                param_found = f"with name {recipe['name']}"
            if len(param_found) == 0 and finder['content'] == recipe['content']:
                param_found = f"with same content"

            result['status'] = False
            result['message'] = f"Recipe {param_found} already exists"

    return result


def delete(recipe_data):
    result = {
        'status': False,
        'message': 'Need id to delete recipe',
        'recipe_data': recipe_data
    }

    if 'id' in recipe_data.keys():
        recipes = app.db['recipes']
        r = recipes.delete_one({'_id': ObjectId(recipe_data['id'])})
        result['delete_status'] = r.deleted_count
        result['status'] = False if r.deleted_count == 0 else True
        result['message'] = 'Recipe delete error' if r.deleted_count == 0 else 'Recipe deleted'

    return result


def validator(recipe_data):
    result = {
        'status': False,
        'message': "Data error",
    }

    if type(recipe_data) is dict and 'content' in recipe_data.keys() and 'name' in recipe_data.keys():
        if type(recipe_data['name']) != str or len(recipe_data['name']) < 2:
            result['message'] = f"'{recipe_data['name']}' is not a valid recipe name"
            return result

        if type(recipe_data['content']) != str or len(recipe_data['content']) < 10:
            result['message'] = f"{recipe_data['name']} invalid recipe content"
            return result

        result['status'] = True

    return result


def recipe_model(recipe_data):
    if type(recipe_data) is not dict:
        recipe_data = {}

    recipe = {
        'name': utils.eval_key('name', recipe_data),
        'description': utils.eval_key('description', recipe_data),
        'safe': utils.eval_key('safe', recipe_data, 'bool'),
        'content': utils.eval_key('content', recipe_data),
        'creator': utils.eval_key('creator', recipe_data),
        'created_at': utils.eval_key('created_at', recipe_data),
        'updated_at': utils.eval_key('updated_at', recipe_data),
    }

    return recipe
