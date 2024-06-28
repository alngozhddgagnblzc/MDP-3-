import cv2
from ultralytics import YOLO
import numpy as np
import time

# 한글 식재료 이름 매핑 딕셔너리
ingredient_mapping = {
    "cabbage": "상추",
    "radish": "무"
}

def load_model(model_path):
    """
    모델 로드 함수
    :param model_path: 모델 파일 경로
    :return: 로드된 모델
    """
    model = YOLO(model_path)
    return model

def preprocess_frame(frame, target_size=(640, 640)):
    """
    프레임 전처리 함수
    :param frame: 캡처된 프레임
    :param target_size: 모델 입력 크기
    :return: 전처리된 프레임
    """
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb, target_size)  # 모델 입력 크기에 맞춤
    return frame_resized

def detect_ingredients(model, frame):
    """
    식재료 인식 함수
    :param model: 로드된 모델
    :param frame: 전처리된 프레임
    :return: 식재료 인식 결과 리스트
    """
    results = model(frame)
    ingredients = []
    for result in results:
        for r in result.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = r
            ingredient_name_en = model.names[int(class_id)]
            ingredient_name_ko = ingredient_mapping.get(ingredient_name_en, "Unknown")
            ingredients.append({
                "name": ingredient_name_ko,
                "score": score
            })
    return ingredients

def capture_frame(camera_index=0):
    """
    웹캠에서 프레임을 캡처하는 함수
    :param camera_index: 웹캠 인덱스
    :return: 캡처된 프레임
    """
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        raise ValueError("웹캠을 열 수 없습니다.")
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        raise ValueError("프레임을 캡처할 수 없습니다.")
    
    return frame

def AI_on(model_path):
    """
    식재료 인식 메인 함수
    :param model_path: 모델 파일 경로
    :return: 인식된 식재료 이름 리스트
    """
    model = load_model(model_path)
    
    frame = capture_frame()
    
    start_time = time.time()
    
    frame_resized = preprocess_frame(frame)
    ingredients = detect_ingredients(model, frame_resized)
    
    for ingredient in ingredients:
        print(f"인식된 식재료: {ingredient['name']}, 신뢰도: {ingredient['score']:.2f}")
    
    end_time = time.time()
    print(f"처리 시간: {end_time - start_time:.2f}초")
    
    return [ingredient['name'] for ingredient in ingredients]
