#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IR-OBIR映射关系SVG生成器
从C++生成的数据文件中读取映射关系，生成SVG向量图和标注
"""

import json
import sys
import os
from typing import Dict, List, Any

class IR_OBIR_RelationSVGGenerator:
    def __init__(self):
        self.node_radius = 15
        self.level_height = 60
        self.node_spacing = 50
        self.column_width = 200
        
    def read_mapping_data(self, mapping_file: str) -> Dict[str, Any]:
        """从C++生成的映射文件中读取IR-OBIR映射关系"""
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f"映射文件 {mapping_file} 不存在")
        except json.JSONDecodeError:
            raise ValueError(f"映射文件 {mapping_file} 格式错误")
    
    def read_annotation_data(self, annotation_file: str) -> List[Dict[str, Any]]:
        """从C++生成的标注文件中读取标注信息"""
        try:
            with open(annotation_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('annotations', [])
        except FileNotFoundError:
            raise FileNotFoundError(f"标注文件 {annotation_file} 不存在")
        except json.JSONDecodeError:
            raise ValueError(f"标注文件 {annotation_file} 格式错误")
    
    def calculate_layout(self, mapping_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算映射关系的布局坐标"""
        ir_nodes = mapping_data.get('ir_nodes', [])
        obir_nodes = mapping_data.get('obir_nodes', [])
        mappings = mapping_data.get('mappings', [])
        
        # 计算IR节点布局（左列）
        ir_layout = {}
        for i, node in enumerate(ir_nodes):
            x = 50
            y = 50 + i * self.level_height
            ir_layout[node['id']] = {
                'x': x,
                'y': y,
                'label': node.get('label', str(node['id'])),
                'type': 'ir'
            }
        
        # 计算OBIR节点布局（右列）
        obir_layout = {}
        for i, node in enumerate(obir_nodes):
            x = 50 + self.column_width
            y = 50 + i * self.level_height
            obir_layout[node['id']] = {
                'x': x,
                'y': y,
                'label': node.get('label', str(node['id'])),
                'type': 'obir'
            }
        
        return ir_layout, obir_layout, mappings
    
    def generate_svg(self, ir_layout: Dict[str, Any], obir_layout: Dict[str, Any], mappings: List[Dict[str, Any]]) -> str:
        """生成映射关系SVG字符串"""
        # 计算SVG尺寸
        all_nodes = {**ir_layout, **obir_layout}
        max_x = max(node['x'] for node in all_nodes.values()) + 100
        max_y = max(node['y'] for node in all_nodes.values()) + 50
        min_x = min(node['x'] for node in all_nodes.values()) - 50
        min_y = min(node['y'] for node in all_nodes.values()) - 50
        
        width = max_x - min_x
        height = max_y - min_y
        
        svg = f'''<svg width="{width}" height="{height}" viewBox="{min_x} {min_y} {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#666"/>
    </marker>
  </defs>
  <g transform="translate({-min_x}, {-min_y})">'''
        
        # 绘制映射连线
        for mapping in mappings:
            ir_node = ir_layout.get(mapping['ir_id'])
            obir_node = obir_layout.get(mapping['obir_id'])
            if ir_node and obir_node:
                # 计算连线路径（贝塞尔曲线）
                x1, y1 = ir_node['x'], ir_node['y']
                x2, y2 = obir_node['x'], obir_node['y']
                mid_x = (x1 + x2) / 2
                
                svg += f'''
    <path d="M{x1},{y1} Q{mid_x},{y1} {x2},{y2}" 
          stroke="#42b983" stroke-width="2" fill="none" marker-end="url(#arrowhead)"/>
    <text x="{mid_x}" y="{y1-10}" text-anchor="middle" 
          font-family="Arial" font-size="10" fill="#666">{mapping.get('label', '')}</text>'''
        
        # 绘制IR节点（左列）
        for node_id, node in ir_layout.items():
            svg += f'''
    <circle cx="{node['x']}" cy="{node['y']}" r="{self.node_radius}" 
            fill="#1976d2" stroke="#333" stroke-width="2"/>
    <text x="{node['x']}" y="{node['y'] + 5}" text-anchor="middle" 
          font-family="Arial" font-size="11" fill="#333">{node['label']}</text>'''
        
        # 绘制OBIR节点（右列）
        for node_id, node in obir_layout.items():
            svg += f'''
    <circle cx="{node['x']}" cy="{node['y']}" r="{self.node_radius}" 
            fill="#7b1fa2" stroke="#333" stroke-width="2"/>
    <text x="{node['x']}" y="{node['y'] + 5}" text-anchor="middle" 
          font-family="Arial" font-size="11" fill="#333">{node['label']}</text>'''
        
        # 添加列标题
        svg += f'''
    <text x="50" y="30" text-anchor="middle" 
          font-family="Arial" font-size="14" font-weight="bold" fill="#1976d2">IR-Tree</text>
    <text x="{50 + self.column_width}" y="30" text-anchor="middle" 
          font-family="Arial" font-size="14" font-weight="bold" fill="#7b1fa2">OBIR-Tree</text>'''
        
        svg += '''
  </g>
</svg>'''
        
        return svg
    
    def generate_from_files(self, mapping_file: str, annotation_file: str) -> Dict[str, Any]:
        """从数据文件生成SVG和标注"""
        # 读取映射数据
        mapping_data = self.read_mapping_data(mapping_file)
        ir_layout, obir_layout, mappings = self.calculate_layout(mapping_data)
        svg_content = self.generate_svg(ir_layout, obir_layout, mappings)
        
        # 读取标注数据
        annotations = self.read_annotation_data(annotation_file)
        
        return {
            'svg': svg_content,
            'annotations': annotations
        }

def main():
    """主函数 - 用于命令行调用"""
    if len(sys.argv) != 3:
        print("用法: python gen_IR_OBIR_relation_svg.py <mapping_file> <annotation_file>")
        sys.exit(1)
    
    mapping_file = sys.argv[1]
    annotation_file = sys.argv[2]
    generator = IR_OBIR_RelationSVGGenerator()
    
    try:
        result = generator.generate_from_files(mapping_file, annotation_file)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 