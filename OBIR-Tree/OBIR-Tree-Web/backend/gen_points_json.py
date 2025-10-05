import os
import json

# 假设脚本在 backend 目录下，data.txt 在 ../public/mock/data.txt
DATA_TXT_PATH = os.path.join(os.path.dirname(__file__), '../public/mock/10.txt')
POINTS_JSON_PATH = os.path.join(os.path.dirname(__file__), '../public/mock/points.json')

points = []
with open(DATA_TXT_PATH, 'r', encoding='utf-8') as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) >= 3:
            try:
                lng = float(parts[1])
                lat = float(parts[2])
                points.append({'lng': lng, 'lat': lat})
            except ValueError:
                continue

with open(POINTS_JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(points, f, ensure_ascii=False, indent=2)

print(f"已生成 {POINTS_JSON_PATH}，共 {len(points)} 个点") 