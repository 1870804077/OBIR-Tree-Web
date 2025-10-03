#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IR-Tree逻辑路径SVG生成器
用于生成显示IR-Tree逻辑路径的SVG图像，突出显示查询路径
"""

import json
import os
import sys
from typing import Dict, List, Tuple, Optional

def load_logic_path_data(data_file: str) -> Dict:
    """加载逻辑路径数据"""
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到数据文件 {data_file}")
        return {}
    except json.JSONDecodeError as e:
        print(f"错误: JSON解析失败 {e}")
        return {}

def calculate_node_position(level: int, index: int, total_nodes: int, width: int, height: int) -> Tuple[int, int]:
    """计算节点位置"""
    x = 50 + (width - 100) * index / max(1, total_nodes - 1)
    y = 50 + (height - 100) * level / 3  # 假设最多4层
    return int(x), int(y)

def generate_svg(tree_data: Dict, logic_path: List[str], width: int = 800, height: int = 600) -> str:
    """生成SVG图像"""
    # 提取树结构
    nodes = tree_data.get('nodes', [])
    edges = tree_data.get('edges', [])
    
    # 创建节点位置映射
    node_positions = {}
    level_nodes = {}
    
    # 按层级组织节点
    for node in nodes:
        level = node.get('level', 0)
        if level not in level_nodes:
            level_nodes[level] = []
        level_nodes[level].append(node)
    
    # 计算每个节点的位置
    for level, level_node_list in level_nodes.items():
        for i, node in enumerate(level_node_list):
            x, y = calculate_node_position(level, i, len(level_node_list), width, height)
            node_positions[node['id']] = (x, y)
    
    # 生成SVG内容
    svg_content = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#666" />
    </marker>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge> 
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  
  <!-- 背景 -->
  <rect width="{width}" height="{height}" fill="#f8f9fa" stroke="#dee2e6" stroke-width="1"/>
  
  <!-- 标题 -->
  <text x="{width//2}" y="30" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="#333">
    IR-Tree逻辑路径展示
  </text>
  
  <!-- 绘制边 -->
  <g id="edges">'''
    
    # 绘制边
    for edge in edges:
        start_id = edge.get('from')
        end_id = edge.get('to')
        
        if start_id in node_positions and end_id in node_positions:
            x1, y1 = node_positions[start_id]
            x2, y2 = node_positions[end_id]
            
            # 检查是否在逻辑路径中
            is_in_path = (start_id in logic_path and end_id in logic_path)
            
            stroke_color = "#ff6b6b" if is_in_path else "#666"
            stroke_width = "3" if is_in_path else "1"
            
            svg_content += f'''
    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke_color}" stroke-width="{stroke_width}" marker-end="url(#arrowhead)"/>'''
    
    svg_content += '''
  </g>
  
  <!-- 绘制节点 -->
  <g id="nodes">'''
    
    # 绘制节点
    for node in nodes:
        node_id = node['id']
        if node_id in node_positions:
            x, y = node_positions[node_id]
            name = node.get('name', node_id)
            level = node.get('level', 0)
            
            # 检查是否在逻辑路径中
            is_in_path = node_id in logic_path
            
            # 节点样式
            if is_in_path:
                fill_color = "#ff6b6b"
                stroke_color = "#d63031"
                stroke_width = "3"
                filter_attr = 'filter="url(#glow)"'
            else:
                fill_color = "#74b9ff"
                stroke_color = "#0984e3"
                stroke_width = "2"
                filter_attr = ""
            
            # 节点大小根据层级调整
            radius = 25 - level * 3
            
            svg_content += f'''
    <circle cx="{x}" cy="{y}" r="{radius}" fill="{fill_color}" stroke="{stroke_color}" stroke-width="{stroke_width}" {filter_attr}/>'''
            
            # 节点标签
            font_size = 12 - level * 1
            svg_content += f'''
    <text x="{x}" y="{y + 5}" text-anchor="middle" font-family="Arial, sans-serif" font-size="{font_size}" fill="white" font-weight="bold">{name}</text>'''
    
    svg_content += '''
  </g>
  
  <!-- 图例 -->
  <g id="legend" transform="translate(20, {height - 80})">
    <rect x="0" y="0" width="200" height="60" fill="white" stroke="#ccc" stroke-width="1" rx="5"/>
    <text x="10" y="20" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="#333">图例:</text>
    <circle cx="30" cy="35" r="8" fill="#74b9ff" stroke="#0984e3" stroke-width="2"/>
    <text x="45" y="40" font-family="Arial, sans-serif" font-size="11" fill="#333">普通节点</text>
    <circle cx="30" cy="50" r="8" fill="#ff6b6b" stroke="#d63031" stroke-width="3" filter="url(#glow)"/>
    <text x="45" y="55" font-family="Arial, sans-serif" font-size="11" fill="#333">逻辑路径节点</text>
  </g>
</svg>'''
    
    return svg_content

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python gen_IR_logic_path_svg.py <数据文件>")
        sys.exit(1)
    
    data_file = sys.argv[1]
    
    # 加载数据
    tree_data = load_logic_path_data(data_file)
    if not tree_data:
        sys.exit(1)
    
    # 获取逻辑路径
    logic_path = tree_data.get('logic_path', [])
    
    # 生成SVG
    svg_content = generate_svg(tree_data, logic_path)
    
    # 输出SVG
    print(svg_content)

if __name__ == "__main__":
    main() 