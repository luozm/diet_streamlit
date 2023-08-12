import streamlit as st
import json
#import translators as ts
from translatepy.translators.google import GoogleTranslate
gtranslate = GoogleTranslate()


def extract_unique_ingredients():
    # 提取所有不重复的食材
    user_unique_ingredients = set()

    # 遍历所有食谱并提取食材
    for recipe in load_recipes():
        user_unique_ingredients.update(recipe['ingredients_detailed']['fresh_ingredient'].keys())
    return user_unique_ingredients


# 读取标准食材数据
@st.cache_data
def load_fdc_nutrition():
    with open('fdc_survey_nutrition.json', 'r', encoding='utf-8') as file:
        return json.load(file)


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
    if 'ingredient_matches' not in st.session_state:
        get_matches()
    matches = st.session_state['ingredient_matches']
    fdc_nutrition = load_fdc_nutrition()
    nutrition = {'calories': 0, 'carbs': 0, 'fat': 0, 'protein': 0}
    ingredients_colored = []
    for ingredient, details in recipe['ingredients_detailed']['fresh_ingredient'].items():
        weight = details.get('weight', 0)
        if ingredient in matches:
            if matches[ingredient] != "Unable to match":
                ingredients_colored.append(ingredient)
                for key in nutrition.keys():
                    nutrition[key] += fdc_nutrition[matches[ingredient]][key] * weight / 100
            else:
                ingredients_colored.append(f":red[{ingredient}]")
        else:
            ingredients_colored.append(f":red[{ingredient}]")
    return nutrition, ingredients_colored


# 显示食谱
def display_recipes(recipes):
    for recipe in recipes:
        st.subheader(recipe['name'])
        nutrition, ingredients_colored = calculate_nutrition(recipe)
        st.write("主料：", ", ".join(ingredients_colored))
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


def save_matches(matches):
    st.session_state['ingredient_matches'] = matches
    with open('ingredient_matches.json', 'w', encoding='utf-8') as file:
        json.dump(matches, file, ensure_ascii=False, indent=4)
    st.success("匹配已成功保存！")


def get_matches():
    # 尝试从本地文件加载
    try:
        with open('ingredient_matches.json', 'r', encoding='utf-8') as file:
            cached_matches = json.load(file)
    except FileNotFoundError:
        cached_matches = {}
    st.session_state['ingredient_matches'] = cached_matches


def match_ingredients():
    st.title("手动匹配食材")

    # 提取食谱中的独特食材
    unique_ingredients = extract_unique_ingredients()
    fdc_nutrition = load_fdc_nutrition()
    fdc_nutrition_names_lower = [item for item in fdc_nutrition.keys()]

    # 获取当前匹配
    if 'ingredient_matches' not in st.session_state:
        get_matches()
    matches = st.session_state['ingredient_matches']

    # 找到未匹配的食材
    unmatched_ingredients = [ingredient for ingredient in unique_ingredients if ingredient not in matches]

    # 如果还有未匹配的食材
    if unmatched_ingredients:
        st.info(f"剩余未匹配食材数量：{len(unmatched_ingredients)}")
        # 显示第一个未匹配的食材
        ingredient_to_match = unmatched_ingredients[0]
        translation = gtranslate.translate(ingredient_to_match, "English")
        # translation = ts.translate_text(ingredient_to_match, from_language='zh-Hans', to_language='en')
        # 搜索框
        search_term = st.text_input(f"搜索并选择 {ingredient_to_match} (英文：{translation}):", value=translation, help="可同时搜索多个关键词，用英文逗号隔开")
        search_list = search_term.split(",")
        # 显示与搜索词匹配的食材
        temp_full_list = fdc_nutrition_names_lower
        for temp_search_term in search_list:
            matching_ingredients = [item for item in temp_full_list if temp_search_term.strip().lower() in item.lower()]
            temp_full_list = matching_ingredients

        # 选择食材
        selected_match = st.selectbox(f"选择匹配的 {ingredient_to_match}:", sorted(temp_full_list)+["Unable to match"])

        # 提交按钮
        if st.button("保存匹配"):
            matches[ingredient_to_match] = selected_match
            # 保存匹配到缓存和本地文件
            save_matches(matches)
            st.experimental_rerun()
    else:
        st.info("所有食材都已匹配！")


# 主函数
def main():
    page = st.sidebar.selectbox("选择页面", ["管理食谱", "手动匹配食材"])
    if page == "管理食谱":
        st.title('健康减脂食谱')
        found_recipes = search_recipes()
        add_recipe()
        display_recipes(found_recipes)
    elif page == "手动匹配食材":
        match_ingredients()


if __name__ == '__main__':

    main()
