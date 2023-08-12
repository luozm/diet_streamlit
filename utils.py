import json
import re
from main import load_recipes
from collections import defaultdict
from tqdm import tqdm


def normalize_and_concat_new_recipes(recipes_old, recipes_new):
    idx_new = len(recipes_old) + 1
    recipes_norm = []
    for recipe in recipes_old:
        total_ingredients = recipe['total_ingredients']
        ingredients_detailed = {'fresh_ingredient': {}, 'condiment': {}}
        # split fresh and condiment
        for ingred, ingred_dict in total_ingredients.items():
            if ingred_dict['type'] == 'fresh_ingredient':
                ingred_dict_new = {}
                if ingred_dict['weight'] != 0:
                    ingred_dict_new['weight'] = ingred_dict['weight']
                elif ingred_dict['count'] != 0:
                    ingred_dict_new['count'] = ingred_dict['count']
                else:
                    raise NameError
                ingredients_detailed['fresh_ingredient'][ingred] = ingred_dict_new
            else:
                ingredients_detailed['condiment'][ingred] = ""
        recipe['ingredients_detailed'] = ingredients_detailed
        del recipe['total_ingredients']
        instructions = recipe['instructions']
        # Splitting the instructions by step number using regular expressions
        instructions_list = re.split(r'\s*\d+、|\s*\d+\.', instructions)[1:]  # Removing the first empty element
        if len(instructions_list) < 2:
            raise NameError
        recipe['instructions'] = instructions_list
        recipes_norm.append(recipe)
    for recipe in recipes_new:
        recipe['id'] = idx_new
        idx_new += 1
        total_ingredients = recipe['total_ingredients']
        ingredients_detailed = {'fresh_ingredient': {}, 'condiment': {}}
        # split fresh and condiment
        for ingred, ingred_dict in total_ingredients.items():
            if ingred_dict['type'] == 'fresh_ingredient':
                ingred_dict_new = {}
                if ingred_dict.get('weight', 0) != 0:
                    ingred_dict_new['weight'] = ingred_dict['weight']
                elif ingred_dict.get('count', 0) != 0:
                    ingred_dict_new['count'] = ingred_dict['count']
                else:
                    raise NameError
                ingredients_detailed['fresh_ingredient'][ingred] = ingred_dict_new
            else:
                ingredients_detailed['condiment'][ingred] = ""
        recipe['ingredients_detailed'] = ingredients_detailed
        del recipe['total_ingredients']
        instructions = recipe['instructions']
        if type(instructions) == str:
            instructions_new = re.split(r'\s*\d+、|\s*\d+\.', instructions)[1:]  # Removing the first empty element
        else:
            # Splitting the instructions by step number using regular expressions
            instructions_new = []
            for instruction in instructions:
                temp = re.split(r'\s*\d+、|\s*\d+\.', instruction)
                if len(temp)>1:
                    instructions_new.append(temp[1])
                else:
                    instructions_new.append(instruction)
        recipe['instructions'] = instructions_new
        recipes_norm.append(recipe)
    return recipes_norm


def calculate_nutrition_from_FDC():
    with open('fdc_foundation_nutrition.json', 'r', encoding='utf-8') as file:
        FDC_foundation = json.load(file)

    # 创建一个字典来存储食材的营养值
    nutrition_values = {}

    # 遍历Foundation Foods dataset，提取食材的营养信息
    for food in FDC_foundation['FoundationFoods']:
        description = food['description']
        food_nutrients = food['foodNutrients']

        # 初始化营养值
        nutrition = {'calories': 0, 'carbs': 0, 'fat': 0, 'protein': 0}

        # 提取营养信息
        for nutrient in food_nutrients:
            nutrient_name = nutrient['nutrient']['name']
            nutrient_amount = nutrient.get('amount', 0)  # 使用get方法，防止"amount"键不存在
            if nutrient_name == 'Energy (Atwater General Factors)':
                nutrition['calories'] = nutrient_amount
            elif nutrient_name == 'Carbohydrate, by difference':
                nutrition['carbs'] = nutrient_amount
            elif nutrient_name == 'Total lipid (fat)':
                nutrition['fat'] = nutrient_amount
            elif nutrient_name == 'Protein':
                nutrition['protein'] = nutrient_amount
        # 将提取的营养值添加到字典中
        nutrition_values[description] = nutrition
    with open('fdc_foundation_nutrition.json', 'w', encoding='utf-8') as file:
        json.dump(nutrition_values, file, indent=4)


def calculate_nutrition_from_FDC_survey():
    with open('FoodData_Central_survey_food_json_2022-10-28.json', 'r', encoding='utf-8') as file:
        FDC_foundation = json.load(file)

    # 创建一个字典来存储食材的营养值
    nutrition_values = {}

    # 遍历Foundation Foods dataset，提取食材的营养信息
    for food in tqdm(FDC_foundation['SurveyFoods']):
        description = food['description']
        # translation = ts.translate_text(description, from_language='en', to_language='zh-Hans')
        food_nutrients = food['foodNutrients']

        # 初始化营养值
        nutrition = {'calories': 0, 'carbs': 0, 'fat': 0, 'protein': 0}

        # 提取数量信息
        portion_dict_new = dict()
        for portion in food['foodPortions']:
            portion_dict_new[portion['portionDescription']] = portion['gramWeight']
        nutrition['portions'] = portion_dict_new

        # 提取营养信息
        for nutrient in food_nutrients:
            nutrient_name = nutrient['nutrient']['name']
            nutrient_amount = nutrient.get('amount', 0)  # 使用get方法，防止"amount"键不存在
            if nutrient_name == 'Energy':
                nutrition['calories'] = nutrient_amount
            elif nutrient_name == 'Carbohydrate, by difference':
                nutrition['carbs'] = nutrient_amount
            elif nutrient_name == 'Total lipid (fat)':
                nutrition['fat'] = nutrient_amount
            elif nutrient_name == 'Protein':
                nutrition['protein'] = nutrient_amount
        # 将提取的营养值添加到字典中
        nutrition_values[description] = nutrition
    with open('fdc_survey_nutrition.json', 'w', encoding='utf-8') as file:
        json.dump(nutrition_values, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    recipes = load_recipes()
    with open('recipes (6).json', 'r', encoding='utf-8') as file:
        recipes_new = json.load(file)
    recipes_normed = normalize_and_concat_new_recipes(recipes, recipes_new)
    with open('recipes_normed.json', 'w', encoding='utf-8') as file:
        json.dump(recipes_normed, file, indent=4, ensure_ascii=False)
    print()