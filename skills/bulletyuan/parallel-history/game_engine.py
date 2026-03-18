#!/usr/bin/env python3
"""
平行历史游戏引擎
管理游戏状态、历史推演、结局评价
"""

import json
import os
from datetime import datetime
from pathlib import Path

class ParallelHistoryGame:
    def __init__(self):
        self.skill_dir = Path(__file__).parent
        self.data_file = self.skill_dir / "historical_data.json"
        self.saves_dir = self.skill_dir / "saves"
        self.saves_dir.mkdir(exist_ok=True)
        
        # 加载历史数据
        with open(self.data_file, 'r', encoding='utf-8') as f:
            self.historical_data = json.load(f)
    
    def get_start_points(self):
        """获取所有历史起点"""
        return self.historical_data['start_points']
    
    def get_faction_info(self, start_point_id, faction_id):
        """获取阵营详细信息"""
        start_point = self.historical_data['start_points'].get(start_point_id)
        if not start_point:
            return None
        
        for faction in start_point['factions']:
            if faction['id'] == faction_id:
                return faction
        return None
    
    def create_game(self, player_name, start_year, faction_id):
        """创建新游戏"""
        start_point_id = f"year_{start_year}"
        start_point = self.historical_data['start_points'].get(start_point_id)
        
        if not start_point:
            return None
        
        faction = self.get_faction_info(start_point_id, faction_id)
        if not faction:
            return None
        
        game_state = {
            "game_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "player_name": player_name,
            "start_year": start_year,
            "current_year": start_year,
            "faction": {
                "id": faction['id'],
                "name": faction['name'],
                "emoji": faction['emoji']
            },
            "political_life": {
                "total_years": 20,
                "remaining_years": 20,
                "current_round": 1,
                "rounds_played": 0
            },
            "organizations": [],
            "legacy": {
                "points": 0,
                "achievements": [],
                "historical_impact": []
            },
            "events": [],
            "mode": "political_life",
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 保存游戏
        self.save_game(game_state)
        return game_state
    
    def save_game(self, game_state):
        """保存游戏"""
        save_file = self.saves_dir / f"{game_state['game_id']}.json"
        with open(save_file, 'w', encoding='utf-8') as f:
            json.dump(game_state, f, ensure_ascii=False, indent=2)
    
    def load_game(self, game_id):
        """加载游戏"""
        save_file = self.saves_dir / f"{game_id}.json"
        if not save_file.exists():
            return None
        
        with open(save_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def process_round(self, game_state, years_to_advance, player_action):
        """处理回合"""
        # 更新年份
        game_state['current_year'] += years_to_advance
        game_state['political_life']['remaining_years'] -= years_to_advance
        game_state['political_life']['rounds_played'] += 1
        
        # 记录事件
        event = {
            "year": game_state['current_year'],
            "round": game_state['political_life']['rounds_played'],
            "description": f"第{game_state['political_life']['rounds_played']}回合",
            "player_action": player_action,
            "consequence": "待推演"
        }
        game_state['events'].append(event)
        
        # 检查是否进入观察者模式
        if game_state['political_life']['remaining_years'] <= 0:
            if game_state['organizations']:
                game_state['mode'] = 'observer'
            else:
                game_state['mode'] = 'ended'
                game_state['status'] = 'no_legacy'
        
        # 更新时间戳
        game_state['updated_at'] = datetime.now().isoformat()
        
        # 保存
        self.save_game(game_state)
        
        return game_state
    
    def evaluate_legacy(self, game_state):
        """评价政治遗产"""
        if not game_state['organizations']:
            return "pillar_of_shame", "未建立任何政治遗产"
        
        # 简化评价逻辑
        total_influence = sum(org.get('influence', 0) for org in game_state['organizations'])
        
        if total_influence >= 100:
            return "glory_hall", "政治遗产影响深远，名垂青史"
        elif total_influence >= 50:
            return "historical_judgment", "政治遗产褒贬不一，功过相抵"
        else:
            return "pillar_of_shame", "政治遗产迅速消散，被历史遗忘"

if __name__ == "__main__":
    # 测试
    game = ParallelHistoryGame()
    print("历史起点:", list(game.get_start_points().keys()))
