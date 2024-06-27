from flask import Flask, jsonify, Response, request
import pymysql
import json
app = Flask(__name__)
from AI import AI_on


# 마리아DB 연결
conn = pymysql.connect(
    host='192.168.137.75',
    user='root',
    password='12345678',
    database='MDP',
    charset='utf8mb4'
)


model_path = '/home/pi/myflaskapp/venv/0627best.pt'

def get_all_have_ingredients():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM have_ingre")
    all_have_ingredients = cursor.fetchall()
    cursor.close()
    return all_have_ingredients

def get_all_recipes():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipe")
    all_recipes = cursor.fetchall()
    cursor.close()
    return all_recipes

def get_matching_recipes(have_ingredients):
    cursor = conn.cursor()
    query = """
        SELECT recipe_id, recipe_name
        FROM recipe
        WHERE (ingre_1 IN %s OR ingre_1 IS NULL)
        AND (ingre_2 IN %s OR ingre_2 IS NULL)
        AND (ingre_3 IN %s OR ingre_3 IS NULL)
        AND (ingre_4 IN %s OR ingre_4 IS NULL)
        AND (ingre_5 IN %s OR ingre_5 IS NULL)
    """
    cursor.execute(query, (have_ingredients, have_ingredients, have_ingredients, have_ingredients, have_ingredients))
    matching_recipes = cursor.fetchall()
    cursor.close()
    return matching_recipes

def get_table_data(table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT COLUMN_NAME FROM information_schema.columns WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = 'MDP'")
    columns = cursor.fetchall()
    column_names = [column[0] for column in columns]
    column_names_str = ', '.join(column_names)
    cursor.execute(f"SELECT {column_names_str} FROM {table_name}")
    data = cursor.fetchall()
    cursor.close()
    result = []
    for row in data:
        item = {column_names[i]: row[i] for i in range(len(column_names))}
        result.append(item)
    return result


def get_all_ingredients(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM ingre")
            all_ingredients = cursor.fetchall()  # 모든 재료 정보를 가져옴
            return all_ingredients
    except pymysql.Error as e:
        print(f"Error during query execution: {e}")
        return None

def save_matching_ingredients(ingredients, all_ingredients):
    try:
        cursor = conn.cursor()
        for camera_ingredient in ingredients:
            for ingre_id, ingre_name in all_ingredients:
                if camera_ingredient == ingre_name:
                    # have_ingre 테이블에서 중복 여부 확인
                    cursor.execute("SELECT COUNT(*) FROM have_ingre WHERE have_in_id = %s", (ingre_id,))
                    count = cursor.fetchone()[0]
                    if count == 0:
                        # 중복이 아닐 경우에만 삽입
                        cursor.execute("INSERT INTO have_ingre (have_in_id, have_in_name) VALUES (%s, %s)", (ingre_id, ingre_name))
                        print(f"일치하는 재료를 저장했습니다: {ingre_name}")
                    else:
                        print(f"이미 존재하는 재료입니다: {ingre_name}")
                    break
        conn.commit()
    except pymysql.Error as e:
        print(f"Error during insertion: {e}")
    finally:
        cursor.close()

@app.route('/data_comparison')
def data_comparison():
    all_have_ingredients = get_all_have_ingredients()
    have_ingredients_ids = [row[0] for row in all_have_ingredients]

    matching_recipes = get_matching_recipes(have_ingredients_ids)
    result = [{'recipe_id': recipe_id, 'recipe_name': recipe_name} for recipe_id, recipe_name in matching_recipes]

    return Response(json.dumps({'matching_recipes': result}, ensure_ascii=False).encode('utf-8'), mimetype='application/json; charset=utf-8')

@app.route('/food')
def get_food():
    data = get_table_data('food')
    return Response(json.dumps({'foods': data}, ensure_ascii=False).encode('utf-8'), mimetype='application/json; charset=utf-8')

@app.route('/recipe')
def get_recipe():
    data = get_table_data('recipe')
    return Response(json.dumps({'recipes': data}, ensure_ascii=False).encode('utf-8'), mimetype='application/json; charset=utf-8')

@app.route('/ingre')
def get_ingredient():
    data = get_table_data('ingre')
    return Response(json.dumps({'ingredients': data}, ensure_ascii=False).encode('utf-8'), mimetype='application/json; charset=utf-8')

@app.route('/save_have_ingre', methods=['GET', 'POST'])
def save_have_ingre():
    try:   
        example_ingredients = AI_on(model_path)
        
        # 데이터베이스에서 모든 재료 가져오기
        all_ingredients = get_all_ingredients(conn)

        # 예시 재료 리스트와 데이터베이스의 재료 비교하여 일치하는 재료 저장하기
        if all_ingredients:
            save_matching_ingredients(example_ingredients, all_ingredients)
        
        # 유효한 응답 반환
        return jsonify({"message": "Matching ingredients processed successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
