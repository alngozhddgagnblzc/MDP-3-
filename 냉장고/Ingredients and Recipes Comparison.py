#냉장고 내부 식재료와 레시피에 필요한 식재료를 비교하여 식재료가 모두 일치하는 레시피 출력 코드
import pymysql

# 데이터베이스 연결
conn = pymysql.connect(
    host='192.168.137.99',
    user='root',
    password='12341234',
    database='test_good',
    charset='utf8mb4'
)

def get_all_have_ingredients():
    # have_ingre 테이블의 모든 재료를 가져오는 함수
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM have_ingre")
    all_have_ingredients = cursor.fetchall()
    cursor.close()
    return all_have_ingredients

def get_all_recipes():
    # recipe 테이블의 모든 레시피를 가져오는 함수
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recipe WHERE in_id_1 IS NOT NULL AND in_id_2 IS NOT NULL AND in_id_3 IS NOT NULL AND in_id_4 IS NOT NULL AND in_in_5 IS NOT NULL")
    all_recipes = cursor.fetchall()
    cursor.close()
    return all_recipes

def get_matching_recipes(have_ingredients):
    # have_ingre 테이블의 재료와 recipe 테이블의 재료를 비교하여 모두 일치하는 레시피를 가져오는 함수
    cursor = conn.cursor()
    # have_ingre에 있는 모든 재료가 포함된 recipe 가져오기
    query = """
        SELECT re_id, food_id
        FROM recipe
        WHERE (in_id_1 IN %s OR in_id_1 IS NULL)
        AND (in_id_2 IN %s OR in_id_2 IS NULL)
        AND (in_id_3 IN %s OR in_id_3 IS NULL)
        AND (in_id_4 IN %s OR in_id_4 IS NULL)
        AND (in_in_5 IN %s OR in_in_5 IS NULL)
    """
    cursor.execute(query, (have_ingredients, have_ingredients, have_ingredients, have_ingredients, have_ingredients))
    matching_recipes = cursor.fetchall()
    cursor.close()
    return matching_recipes

def main():
    # have_ingre 테이블 데이터 출력
    print("have_ingre 테이블 데이터:")
    all_have_ingredients = get_all_have_ingredients()
    for row in all_have_ingredients:
        print(row)

    # recipe 테이블 데이터 출력
    print("\nrecipe 테이블 데이터:")
    all_recipes = get_all_recipes()
    for row in all_recipes:
        print(row)

    # have_ingre 테이블 데이터 가져오기
    cursor = conn.cursor()
    cursor.execute("SELECT have_in_id FROM have_ingre")
    have_ingredients = [row[0] for row in cursor.fetchall()]
    cursor.close()

    # 일치하는 레시피 가져오기
    matching_recipes = get_matching_recipes(have_ingredients)
    
    if matching_recipes:
        print("\n일치하는 레시피:")
        for re_id, food_id in matching_recipes:
            print(f"{re_id}: {food_id}")
    else:
        print("\n일치하는 레시피가 없습니다.")

if __name__ == "__main__":
    main()
