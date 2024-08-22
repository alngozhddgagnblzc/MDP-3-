

from flask import Flask, jsonify, Response, request, redirect, url_for
import pymysql
import json
from AI import AI_on #인공지능 실행 함수 부분(파일명과 함수명이 일치해야 실행됨)
import serial
from serial_test import send_text, receive_text
app = Flask(__name__)
value_1 = ""
# 마리아DB 연결
conn = pymysql.connect(
    host='192.168.137.75',
    user='root',
    password='12345678',
    database='MDP',
    charset='utf8mb4'
)

ser = serial.Serial(
    port='/dev/ttyAMA0',  # 라즈베리 파이 UART 포트, '/dev/ttyS0'는 기본 UART 포트입니다.
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)
model_path = 'C:\Users\user\Desktop/0627best.pt'
saved_value = None  # 전송된 value를 저장할 변수6  8

def get_all_have_ingredients():
    """
    have_ingre 테이블에서 모든 재료의 ID를 가져오는 함수.ㄹㄹ
    """
    cursor = conn.cursor()
    cursor.execute("SELECT have_in_id FROM have_ingre")
    all_have_ingredients = cursor.fetchall()
    cursor.close()
    return all_have_ingredients

def get_all_recipes():
    """
    recipe 테이블에서 모든 레시피를 가져오는 함수.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipe")
    all_recipes = cursor.fetchall()
    return all_recipes

def get_matching_recipes(have_ingredients):
    """
    주어진 재료들을 기반으로 레시피 테이블에서 일치하는 레시피를 찾는 함수.
    """
    if not have_ingredients:
        return []
    
    cursor = conn.cursor()
    placeholders = ', '.join(['%s'] * len(have_ingredients))
    query = f"""
        SELECT recipe_id, recipe_name, ingre_1, ingre_2, ingre_3, ingre_4, ingre_5
        FROM recipe
        WHERE (ingre_1 IS NULL OR ingre_1 IN ({placeholders}))
        AND (ingre_2 IS NULL OR ingre_2 IN ({placeholders}))
        AND (ingre_3 IS NULL OR ingre_3 IN ({placeholders}))
        AND (ingre_4 IS NULL OR ingre_4 IN ({placeholders}))
        AND (ingre_5 IS NULL OR ingre_5 IN ({placeholders}))
    """
    cursor.execute(query, tuple(have_ingredients) * 5)
    matching_recipes = cursor.fetchall()
    cursor.close()
    return matching_recipes

def get_table_data(table_name):
    """
    주어진 테이블 이름을 기반으로 테이블의 데이터를 가져오는 함수.
    """
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
    """
    ingre 테이블에서 모든 재료 정보를 가져오는 함수.
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM ingre")
            all_ingredients = cursor.fetchall()  # 모든 재료 정보를 가져옴
            return all_ingredients
    except pymysql.Error as e:
        print(f"Error during query execution: {e}")
        return None

def save_matching_ingredients(ingredients, all_ingredients):
    """
    주어진 재료 목록과 데이터베이스의 재료 목록을 비교하여 일치하는 재료를 have_ingre 테이블에 저장하는 함수.
    """
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
    """
    현재 가지고 있는 재료를 기반으로 일치하는 레시피를 반환하는 엔드포인트.
    """
    all_have_ingredients = get_all_have_ingredients()
    if not all_have_ingredients:
        return jsonify({'matching_recipes': []})

    have_ingredients_ids = [row[0] for row in all_have_ingredients]

    matching_recipes = get_matching_recipes(have_ingredients_ids)
    
    # 필터링: 모든 재료가 일치하는지 확인
    filtered_recipes = []
    for recipe in matching_recipes:
        recipe_id, recipe_name, *recipe_ingredients = recipe
        recipe_ingredients = [ing for ing in recipe_ingredients if ing is not None]  # None 값을 제외
        # 레시피의 모든 재료가 현재 가진 재료 목록에 있는지 확인
        if all(ing in have_ingredients_ids for ing in recipe_ingredients):
            filtered_recipes.append({'recipe_id': recipe_id, 'recipe_name': recipe_name})
    
    return Response(json.dumps({'matching_recipes': filtered_recipes}, ensure_ascii=False).encode('utf-8'), mimetype='application/json; charset=utf-8')

@app.route('/food')
def get_food():
    """
    food 테이블의 모든 데이터를 JSON 형식으로 반환하는 엔드포인트.
    """
    data = get_table_data('food')
    return Response(json.dumps({'foods': data}, ensure_ascii=False).encode('utf-8'), mimetype='application/json; charset=utf-8')

@app.route('/recipe')
def get_recipe():
    """
    recipe 테이블의 모든 데이터를 JSON 형식으로 반환하는 엔드포인트.
    """
    data = get_table_data('recipe') 
    return Response(json.dumps({'recipes': data}, ensure_ascii=False).encode('utf-8'), mimetype='application/json; charset=utf-8')

@app.route('/ingre')
def get_ingredient():
    """
    ingre 테이블의 모든 데이터를 JSON 형식으로 반환하는 엔드포인트.
    """
    data = get_table_data('ingre')
    return Response(json.dumps({'ingredients': data}, ensure_ascii=False).encode('utf-8'), mimetype='application/json; charset=utf-8')

@app.route('/save_have_ingre', methods=['GET', 'POST'])
def save_have_ingre():
    """
    AI 모델을 통해 인식된 재료를 have_ingre 테이블에 저장하는 엔드포인트.
    """
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

# 새로운 엔드포인트 추가
@app.route('/send_data', methods=['POST'])
def receive_data():
    """
    외부로부터 데이터를 받아서 저장하는 엔드포인트.
    """
    global saved_value
    try:
        data = request.get_json()
        value = data.get('value')
        if value is not None:
            # 전송된 값을 저장
            saved_value = value
            print(f"Received value: {value}")
            return jsonify({'status': 'success', 'message': 'Data received successfully'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Invalid data received'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/recipe_explanation', methods=['GET'])
def get_recipe_explanation():
    """
    저장된 값을 기반으로 recipe_explanation 테이블에서 데이터를 조회하여 반환하는 엔드포인트.
    
    Returns:
    Response: 조회된 데이터를 JSON 형식으로 반환
    """
    
    send_text("nice")
    print("전송 성공")
    
    global saved_value
    if saved_value is None:
        return jsonify({'status': 'error', 'message': 'No value received'}), 400
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM recipe_explanation WHERE recipe_ex_id = %s', (saved_value,))
        rows = cursor.fetchall()
        cursor.close()

        if rows:
            # 데이터베이스에서 가져온 행을 JSON 형식으로 변환
            return Response(json.dumps({'status': 'success', 'data': rows}, ensure_ascii=False).encode('utf-8'), mimetype='application/json; charset=utf-8')
        else:
            return jsonify({'status': 'error', 'message': 'No matching records found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

