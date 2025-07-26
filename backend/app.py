#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端API服务器
提供IR-Tree SVG生成接口
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import sys
from gen_IR_Tree_svg import IRTreeSVGGenerator
from gen_IR_OBIR_relation_svg import IR_OBIR_RelationSVGGenerator
from gen_IR_logic_path_svg import generate_svg as generate_logic_path_svg
from gen_OBIR_Tree_realtime_svg import OBIRTreeRealtimeSVGGenerator

app = Flask(__name__)
CORS(app)

# 数据目录
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

@app.route('/api/ir-tree-svg', methods=['POST'])
def ir_tree_svg():
    """生成IR-Tree SVG"""
    try:
        data = request.get_json()
        data_file = data.get('dataFile', 'ir_tree_data.json')
        file_path = os.path.join(DATA_DIR, data_file)
        
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': f'数据文件不存在: {data_file}'})
        
        # 生成SVG
        generator = IRTreeSVGGenerator()
        svg_content = generator.generate_from_file(file_path)
        
        return jsonify({'success': True, 'svg': svg_content})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/ir-obir-relation-svg', methods=['POST'])
def ir_obir_relation_svg():
    """生成IR-OBIR关系SVG和标注"""
    try:
        data = request.get_json()
        mapping_file = data.get('mappingFile', 'ir_obir_mapping.json')
        annotation_file = data.get('annotationFile', 'ir_obir_annotations.json')
        
        mapping_path = os.path.join(DATA_DIR, mapping_file)
        annotation_path = os.path.join(DATA_DIR, annotation_file)
        
        if not os.path.exists(mapping_path):
            return jsonify({'success': False, 'error': f'映射文件不存在: {mapping_file}'})
        
        if not os.path.exists(annotation_path):
            return jsonify({'success': False, 'error': f'标注文件不存在: {annotation_file}'})
        
        # 生成SVG和标注
        generator = IR_OBIR_RelationSVGGenerator()
        result = generator.generate_from_files(mapping_path, annotation_path)
        
        return jsonify({
            'success': True, 
            'svg': result['svg'],
            'annotations': result['annotations']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/ir-logic-path-svg', methods=['POST'])
def ir_logic_path_svg():
    """生成IR-Tree逻辑路径SVG"""
    try:
        data = request.get_json()
        data_file = data.get('dataFile', 'ir_logic_path_data.json')
        file_path = os.path.join(DATA_DIR, data_file)
        
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': f'数据文件不存在: {data_file}'})
        
        # 加载数据
        with open(file_path, 'r', encoding='utf-8') as f:
            tree_data = json.load(f)
        
        # 获取逻辑路径
        logic_path = tree_data.get('logic_path', [])
        
        # 生成SVG
        svg_content = generate_logic_path_svg(tree_data, logic_path)
        
        return jsonify({'success': True, 'svg': svg_content})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/query-results', methods=['POST'])
def query_results():
    """获取查询结果"""
    try:
        data = request.get_json()
        query = data.get('query', 'OBIR-Tree查询')
        top_k = data.get('topK', 5)
        
        # 模拟从C++后端获取的查询结果
        # 这里应该调用C++代码获取真实的查询结果
        mock_results = [
            {
                "title": "北京大学本部（燕园校区）",
                "description": "位于北京市海淀区颐和园路5号，是北京大学的主校区，环境优美，拥有未名湖、博雅塔等著名景观，包含文理学院、工学院等多个院系。",
                "relevance": 95,
                "location": "北京市海淀区颐和园路5号",
                "distance": 0.2,
                "type": "教育机构"
            },
            {
                "title": "北京大学医学部",
                "description": "位于北京市海淀区学院路38号，是北京大学的医学教育中心，拥有多个附属医院和医学研究机构，在医学教育领域享有盛誉。",
                "relevance": 92,
                "location": "北京市海淀区学院路38号",
                "distance": 1.5,
                "type": "教育机构"
            },
            {
                "title": "北京大学昌平校区",
                "description": "位于北京市昌平区沙河高教园区，是北京大学的新校区，主要承担部分本科教育和科研工作，设施现代化，环境优美。",
                "relevance": 88,
                "location": "北京市昌平区沙河高教园区",
                "distance": 25.0,
                "type": "教育机构"
            },
            {
                "title": "北京大学深圳研究生院",
                "description": "位于深圳市南山区深圳湾，是北京大学在深圳设立的研究生教育机构，专注于前沿科技研究和高端人才培养。",
                "relevance": 85,
                "location": "深圳市南山区深圳湾",
                "distance": 2000.0,
                "type": "教育机构"
            },
            {
                "title": "北京大学图书馆",
                "description": "位于燕园校区内，是北京大学的主要图书馆，藏书丰富，为师生提供良好的学习环境，是亚洲最大的大学图书馆之一。",
                "relevance": 82,
                "location": "北京市海淀区颐和园路5号",
                "distance": 0.1,
                "type": "图书馆"
            }
        ]
        
        # 限制返回结果数量
        results = mock_results[:top_k]
        
        # 保存搜索参数到search_query.json，供C++后端读取
        try:
            search_query_path = os.path.join(DATA_DIR, 'search_query.json')
            with open(search_query_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'query': query,
                    'lng': data.get('lng'),
                    'lat': data.get('lat'),
                    'topK': top_k
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f'写入search_query.json失败: {e}', file=sys.stderr)

        return jsonify({
            'success': True,
            'results': results,
            'query': query,
            'total': len(results),
            'timestamp': '2024-01-15 14:30:25'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/obir-tree-realtime', methods=['POST'])
def obir_tree_realtime():
    """OBIR-Tree实时路径展示API"""
    try:
        data = request.get_json()
        current_file = data.get('currentFile', 'obir_tree_current.json')
        previous_file = data.get('previousFile', 'obir_tree_previous.json')
        
        current_path = os.path.join(DATA_DIR, current_file)
        previous_path = os.path.join(DATA_DIR, previous_file) if previous_file else None
        
        if not os.path.exists(current_path):
            return jsonify({'success': False, 'error': f'当前数据文件不存在: {current_file}'})
        
        generator = OBIRTreeRealtimeSVGGenerator()
        result = generator.generate_from_files(current_path, previous_path)
        
        if result['success']:
            return jsonify({
                'success': True,
                'svg': result['svg'],
                'differences': result['differences'],
                'current_nodes': result['current_nodes'],
                'previous_nodes': result['previous_nodes']
            })
        else:
            return jsonify({'success': False, 'error': result['error']})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'ok',
        'message': 'IR-Tree SVG API服务正常运行'
    })

if __name__ == '__main__':
    print("启动Flask服务器...")
    print(f"数据目录: {DATA_DIR}")
    print(f"数据目录存在: {os.path.exists(DATA_DIR)}")
    
    # 检查数据文件
    data_files = ['ir_tree_data.json', 'ir_obir_mapping.json', 'ir_obir_annotations.json', 'ir_logic_path_data.json']
    for file in data_files:
        file_path = os.path.join(DATA_DIR, file)
        print(f"数据文件 {file}: {'存在' if os.path.exists(file_path) else '不存在'}")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 