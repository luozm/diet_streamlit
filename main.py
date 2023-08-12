import streamlit as st
import json
import translators as ts
#from thefuzz import process


# 常见食材的营养值（每100克）
NUTRITION_VALUES = {
    '龙利鱼柳': {'calories': 90, 'carbs': 0, 'fat': 1, 'protein': 19},
    '香菇': {'calories': 22, 'carbs': 3, 'fat': 0, 'protein': 3},
    # 其他食材的营养值可以按照需要添加
}


def extract_unique_ingredients():
    # 提取所有不重复的食材
    user_unique_ingredients = set()

    # 遍历所有食谱并提取食材
    for recipe in load_recipes():
        user_unique_ingredients.update(recipe['ingredients_detailed']['fresh_ingredient'].keys())
    return user_unique_ingredients


# 读取食谱数据
def load_recipes():
    with open('recipes_normed.json', 'r', encoding='utf-8') as file:
        return json.load(file)


# 保存食谱数据
def save_recipes(recipes):
    with open('recipes_normed.json', 'w', encoding='utf-8') as file:
        json.dump(recipes, file, ensure_ascii=False, indent=4)


# 计算食谱的营养值
def calculate_nutrition(recipe):
    nutrition = {'calories': 0, 'carbs': 0, 'fat': 0, 'protein': 0}
    for ingredient, details in recipe['ingredients_detailed']['fresh_ingredient'].items():
        weight = details.get('weight', 0)
        if ingredient in NUTRITION_VALUES:
            for key in nutrition.keys():
                nutrition[key] += NUTRITION_VALUES[ingredient][key] * weight / 100
    return nutrition


# 显示食谱
def display_recipes(recipes):
    for recipe in recipes:
        st.subheader(recipe['name'])
        nutrition = calculate_nutrition(recipe)
        st.write("主料：", ", ".join(recipe['ingredients_detailed']['fresh_ingredient'].keys()))
        st.write(
            f"热量: {nutrition['calories']} kcal | 碳水: {nutrition['carbs']} g | 脂肪: {nutrition['fat']} g | 蛋白质: {nutrition['protein']} g")
        with st.expander('详情', expanded=False):
            st.write('配料:', ', '.join(recipe['ingredients']))
            # Constructing the Markdown string with step numbers
            instructions_md = "\n".join([f"{idx + 1}. {step}" for idx, step in enumerate(recipe['instructions'])])
            # Displaying the instructions with step numbers in Streamlit
            st.write('做法:')
            st.markdown(instructions_md)



# 搜索食谱
def search_recipes():
    search_query = st.text_input('Search by name or ingredient')
    found_recipes = load_recipes()
    if search_query:
        found_recipes = [recipe for recipe in load_recipes() if search_query.lower() in recipe['name'].lower() or any(search_query.lower() in ingredient.lower() for ingredient in recipe['ingredients'])]
    return found_recipes


# 添加新食谱
def add_recipe():
    with st.expander('添加新食谱', expanded=False):
        name = st.text_input('Name')
        ingredients = st.text_area('Ingredients (comma separated)')
        instructions = st.text_area('Instructions')
        if st.button('Add Recipe'):
            new_recipe = {
                'id': str(len(load_recipes()) + 1),
                'name': name,
                'ingredients': ingredients.split(','),
                'instructions': instructions
                # 其他信息可以根据需要添加
            }
            recipes = load_recipes()
            recipes.append(new_recipe)
            save_recipes(recipes)
            st.success('Recipe added successfully!')


# 主函数
def main():
    st.title('健康减脂食谱')
    found_recipes = search_recipes()
    add_recipe()
    display_recipes(found_recipes)


if __name__ == '__main__':
    # calculate_nutrition_from_FDC_survey()

    # with open('fdc_foundation_nutrition.json', 'r', encoding='utf-8') as file:
    #     FDC_foundation = json.load(file)
    # ingredients_set = extract_unique_ingredients()
    # # translations
    # ingredients_en2cn = {}
    # ingredients_cn2en = {}
    # for ingredient in ingredients_set:
    #     translation = ts.translate_text(ingredient, from_language='zh-Hans', to_language='en')
    #     ingredients_en2cn[translation] = ingredient
    #     ingredients_cn2en[ingredient] = translation
    # # matching
    # FDC_names = list(FDC_foundation.keys())
    # matched_ingredients = {}
    # for ingredient in ingredients_set:
    #     ingredient_en = ingredients_cn2en[ingredient]
    #     name_matched, score = process.extractOne(ingredient_en, FDC_names)
    #     if score > 90:  # 你可以根据需要调整匹配阈值
    #         matched_ingredients[ingredient] = name_matched
    # nutrition_info = [FDC_foundation[match] for match in matched_ingredients.values()]

    main()
