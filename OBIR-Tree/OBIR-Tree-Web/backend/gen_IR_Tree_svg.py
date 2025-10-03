#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IR-Tree SVG生成器
从C++生成的数据文件中读取IR-Tree结构，生成SVG向量图
"""

import json
import sys
import os
from typing import Dict, List, Any

class IRTreeSVGGenerator:
    def __init__(self):
        self.node_radius = 20
        self.level_height = 80
        self.node_spacing = 60
        
    def read_tree_data(self, data_file: str) -> Dict[str, Any]:
        """从C++生成的数据文件中读取IR-Tree结构"""
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f"数据文件 {data_file} 不存在")
        except json.JSONDecodeError:
            raise ValueError(f"数据文件 {data_file} 格式错误")
    
    def calculate_layout(self, tree_data: Dict[str, Any]) -> Dict[str, Any]:
        """计算树形布局的坐标"""
        nodes = tree_data.get('nodes', [])
        edges = tree_data.get('edges', [])
        
        # 按层级组织节点
        levels = {}
        for node in nodes:
            level = node.get('level', 0)
            if level not in levels:
                levels[level] = []
            levels[level].append(node)
        
        # 计算每个节点的坐标
        layout = {}
        for level, level_nodes in levels.items():
            y = level * self.level_height + 50
            total_width = (len(level_nodes) - 1) * self.node_spacing
            start_x = 400 - total_width / 2  # 居中
            
            for i, node in enumerate(level_nodes):
                x = start_x + i * self.node_spacing
                layout[node['id']] = {
                    'x': x,
                    'y': y,
                    'label': node.get('label', str(node['id'])),
                    'type': node.get('type', 'node')
                }
        
        return layout, edges
    
    def generate_svg(self, layout: Dict[str, Any], edges: List[Dict[str, Any]]) -> str:
        """生成SVG字符串"""
        # 计算SVG尺寸
        max_x = max(node['x'] for node in layout.values()) + 50
        max_y = max(node['y'] for node in layout.values()) + 50
        min_x = min(node['x'] for node in layout.values()) - 50
        min_y = min(node['y'] for node in layout.values()) - 50
        
        width = max_x - min_x
        height = max_y - min_y
        
        # 确保viewBox从0开始，避免负坐标
        svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#666"/>
    </marker>
  </defs>
  <g transform="translate({-min_x}, {-min_y})">'''
        
        # 绘制边
        for edge in edges:
            from_node = layout.get(edge['from'])
            to_node = layout.get(edge['to'])
            if from_node and to_node:
                svg += f'''
    <line x1="{from_node['x']}" y1="{from_node['y']}" x2="{to_node['x']}" y2="{to_node['y']}" 
          stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>'''
        
        # 绘制节点
        for node_id, node in layout.items():
            # 根据节点类型选择颜色
            if node['type'] == 'root':
                fill_color = '#42b983'
            elif node['type'] == 'leaf':
                fill_color = '#ff6b6b'
            else:
                fill_color = '#4ecdc4'
            
            svg += f'''
    <circle cx="{node['x']}" cy="{node['y']}" r="{self.node_radius}" 
            fill="{fill_color}" stroke="#333" stroke-width="2"/>
    <text x="{node['x']}" y="{node['y'] + 5}" text-anchor="middle" 
          font-family="Arial" font-size="12" fill="#333">{node['label']}</text>'''
        
        svg += '''
  </g>
</svg>'''
        
        return svg
    
    def generate_from_file(self, data_file: str) -> str:
        """从数据文件生成SVG"""
        tree_data = self.read_tree_data(data_file)
        layout, edges = self.calculate_layout(tree_data)
        return self.generate_svg(layout, edges)

def main():
    """主函数 - 用于命令行调用"""
    if len(sys.argv) != 2:
        print("用法: python gen_IR_Tree_svg.py <data_file>")
        sys.exit(1)
    
    data_file = sys.argv[1]
    generator = IRTreeSVGGenerator()
    
    try:
        svg_content = generator.generate_from_file(data_file)
        print(svg_content)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 