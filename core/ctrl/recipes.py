import json
from bson.objectid import ObjectId
from core import app, data, utils, notifications


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

            changed = utils.detect_object_changes([
                'name',
                'description',
                'safe',
                'content'
            ], modify_recipe, recipe)

            recipes = app.db['recipes']

            if 'target' not in recipe or type(recipe['target']) != str:
                recipe['target'] = 'site'

            recipe = recipe_model(recipe)
            recipes.update_one({'_id': ObjectId(_id)}, {'$set': recipe})

            if changed == True:
                # Notification comes here
                notifications.db(
                    'recipe', _id, f"Recipe {recipe['name']} was modified.", json.dumps(recipe, indent=4))

            result['status'] = True
            result['message'] = f"Recipe {recipe['name']} modified"
            result['changed'] = changed

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

            if 'target' not in recipe or type(recipe['target']) != str:
                recipe['target'] = 'site'

            recipes = app.db['recipes']
            _id = recipes.insert_one(recipe)

            # Notification comes here
            html_message_data = {
                'app_full_name': app.config['name'],
                'username': app.config['user']['username'],
                'message': f"Recipe {recipe['name']} was created."
            }
            notifications.email('settings.notifications.sites',
                                'common-notification', f"{app.config['name']} - recipe created", html_message_data)
            notifications.db(
                'site', str(_id.inserted_id), f"Recipe {recipe['name']} was created.", json.dumps(recipe, indent=4))

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
        'target': utils.eval_key('target', recipe_data),
        'content': utils.eval_key('content', recipe_data),
        'creator': utils.eval_key('creator', recipe_data),
        'created_at': utils.eval_key('created_at', recipe_data),
        'updated_at': utils.eval_key('updated_at', recipe_data),
    }

    return recipe
