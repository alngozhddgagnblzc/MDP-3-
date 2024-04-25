#냉장고 내부 식재료 저장 코드
import pymysql

# 데이터베이스 연결
conn = pymysql.connect(
    host='192.168.137.99',
    user='root',
    password='12341234',
    database='test_good',
    charset='utf8mb4'
)

def get_camera_ingredients():
    # 카메라로 찍은 재료 리스트를 가져오는 함수
    # 구현해야 함
    camera_ingredients = ['돼지고기', '마늘', '대파', '두부', '치킨']  # 예시 데이터
    return camera_ingredients

def get_all_ingredients():
    # 데이터베이스의 모든 재료를 가져오는 함수
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ingre")
    all_ingredients = cursor.fetchall()  # 모든 재료 정보를 가져옴
    cursor.close()
    return all_ingredients

def save_matching_ingredients(camera_ingredients, all_ingredients):
    # 카메라로 찍은 재료 리스트와 데이터베이스의 재료 리스트를 비교하여 일치하는 재료를 저장하는 함수
    cursor = conn.cursor()
    for camera_ingredient in camera_ingredients:
        for ingre_id, ingre_name in all_ingredients:
            if camera_ingredient == ingre_name:
                # have_ingre 테이블에 저장
                cursor.execute("INSERT INTO have_ingre (have_in_id, have_in_name) VALUES (%s, %s)", (ingre_id, ingre_name))
    conn.commit()
    cursor.close()
    if cursor.rowcount > 0:
        print("일치하는 재료를 저장했습니다.")
    else:
        print("일치하는 재료가 없습니다.")

def main():
    camera_ingredients = get_camera_ingredients()
    all_ingredients = get_all_ingredients()
    save_matching_ingredients(camera_ingredients, all_ingredients)

if __name__ == "__main__":
    main()
