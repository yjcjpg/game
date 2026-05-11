"""
雙人對戰掃雷遊戲
兩個玩家各自在 9×6 的範圍內隱藏 15 個地雷
輪流猜測對方的地雷位置，猜中地雷可以繼續猜，否則換人
先猜完對方所有地雷的玩家獲勝
"""

import os
import sys
from typing import List, Tuple, Set
from enum import Enum

class GameState(Enum):
    SETUP = "設置地雷"
    PLAYING = "遊戲進行中"
    FINISHED = "遊戲結束"

class MinesweeperGame:
    def __init__(self):
        self.ROWS = 6
        self.COLS = 9
        self.MINES = 15
        
        # 玩家 1 和玩家 2 的地雷位置
        self.player1_mines: Set[Tuple[int, int]] = set()
        self.player2_mines: Set[Tuple[int, int]] = set()
        
        # 玩家 1 和玩家 2 的已猜測位置
        self.player1_guesses: Set[Tuple[int, int]] = set()
        self.player2_guesses: Set[Tuple[int, int]] = set()
        
        # 遊戲狀態
        self.state = GameState.SETUP
        self.current_player = 1
        self.winner = None
    
    def clear_screen(self):
        """清空終端螢幕"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_board(self, mines: Set[Tuple[int, int]], guesses: Set[Tuple[int, int]], show_mines: bool = False):
        """
        打印遊戲板
        show_mines: 是否顯示地雷位置（用於設置階段或調試）
        """
        print("    ", end="")
        for col in range(self.COLS):
            print(f" {col} ", end="")
        print()
        
        print("  +" + "-" * (self.COLS * 4 - 1) + "+")
        
        for row in range(self.ROWS):
            print(f"{row} |", end="")
            for col in range(self.COLS):
                pos = (row, col)
                
                if pos in guesses:
                    if pos in mines:
                        print(" 💣", end="")
                    else:
                        print(" ·", end="")
                elif show_mines and pos in mines:
                    print(" 💣", end="")
                else:
                    print(" ?", end="")
                print(" |" if col == self.COLS - 1 else "", end="")
            print()
        
        print("  +" + "-" * (self.COLS * 4 - 1) + "+")
    
    def setup_mines_interactive(self, player_num: int):
        """互動式設置地雷"""
        if player_num == 1:
            mines = self.player1_mines
        else:
            mines = self.player2_mines
        
        while len(mines) < self.MINES:
            self.clear_screen()
            print(f"\n========== 玩家 {player_num} - 設置地雷 ==========")
            print(f"已設置: {len(mines)}/{self.MINES} 個地雷\n")
            self.print_board(mines, set(), show_mines=True)
            
            try:
                user_input = input(f"\n輸入地雷位置 (格式: 行,列，例如: 2,3)，或輸入 'auto' 自動隨機設置: ").strip()
                
                if user_input.lower() == 'auto':
                    import random
                    while len(mines) < self.MINES:
                        row = random.randint(0, self.ROWS - 1)
                        col = random.randint(0, self.COLS - 1)
                        mines.add((row, col))
                    print(f"\n✓ 已自動設置 {self.MINES} 個地雷！")
                    input("按 Enter 繼續...")
                    break
                
                parts = user_input.split(',')
                row, col = int(parts[0].strip()), int(parts[1].strip())
                
                if not (0 <= row < self.ROWS and 0 <= col < self.COLS):
                    print(f"❌ 位置超出範圍！範圍應在 0-{self.ROWS-1} 行和 0-{self.COLS-1} 列")
                    input("按 Enter 繼續...")
                    continue
                
                if (row, col) in mines:
                    print("❌ 該位置已有地雷！")
                    input("按 Enter 繼續...")
                    continue
                
                mines.add((row, col))
                print(f"✓ 已在 ({row},{col}) 放置地雷")
                input("按 Enter 繼續...")
            
            except ValueError:
                print("❌ 輸入格式錯誤！請輸入 '行,列' 或 'auto'")
                input("按 Enter 繼續...")
    
    def setup_phase(self):
        """設置階段"""
        self.state = GameState.SETUP
        self.setup_mines_interactive(1)
        self.setup_mines_interactive(2)
    
    def print_game_status(self):
        """打印遊戲狀態"""
        self.clear_screen()
        print("\n" + "="*50)
        print(f"當前玩家: 玩家 {self.current_player}")
        print(f"玩家 1 剩餘地雷: {len(self.player1_mines) - len(self.player2_guesses)} / {self.MINES}")
        print(f"玩家 2 剩餘地雷: {len(self.player2_mines) - len(self.player1_guesses)} / {self.MINES}")
        print("="*50 + "\n")
    
    def play_turn(self):
        """執行一回合"""
        if self.current_player == 1:
            opponent_mines = self.player2_mines
            player_guesses = self.player1_guesses
            opponent_guesses = self.player2_guesses
        else:
            opponent_mines = self.player1_mines
            player_guesses = self.player2_guesses
            opponent_guesses = self.player1_guesses
        
        while True:
            self.print_game_status()
            print(f"玩家 {self.current_player} 正在查看對手的領域\n")
            self.print_board(opponent_mines, player_guesses)
            
            try:
                user_input = input(f"\n玩家 {self.current_player}，輸入猜測位置 (格式: 行,列，例如: 2,3): ").strip()
                
                parts = user_input.split(',')
                row, col = int(parts[0].strip()), int(parts[1].strip())
                
                if not (0 <= row < self.ROWS and 0 <= col < self.COLS):
                    print(f"❌ 位置超出範圍！")
                    input("按 Enter 繼續...")
                    continue
                
                if (row, col) in player_guesses:
                    print("❌ 你已經猜過這個位置了！")
                    input("按 Enter 繼續...")
                    continue
                
                player_guesses.add((row, col))
                
                if (row, col) in opponent_mines:
                    print(f"🎉 玩家 {self.current_player} 猜中地雷！可以繼續猜測\n")
                    input("按 Enter 繼續...")
                    
                    # 檢查是否獲勝
                    if len(player_guesses) == len(opponent_mines):
                        self.winner = self.current_player
                        self.state = GameState.FINISHED
                        return
                else:
                    print(f"❌ 玩家 {self.current_player} 沒有猜中，換人！\n")
                    input("按 Enter 繼續...")
                    self.switch_player()
                    return
            
            except ValueError:
                print("❌ 輸入格式錯誤！請輸入 '行,列'")
                input("按 Enter 繼續...")
    
    def switch_player(self):
        """切換當前玩家"""
        self.current_player = 3 - self.current_player
    
    def print_winner(self):
        """打印獲勝者"""
        self.clear_screen()
        print("\n" + "="*50)
        print(f"🏆 玩家 {self.winner} 獲勝！ 🏆")
        print("="*50)
        
        print(f"\n玩家 1 的地雷位置:")
        self.print_board(self.player1_mines, self.player2_guesses, show_mines=True)
        
        print(f"\n玩家 2 的地雷位置:")
        self.print_board(self.player2_mines, self.player1_guesses, show_mines=True)
        
        print(f"\n玩家 1 猜對: {len(self.player1_guesses)} 個地雷")
        print(f"玩家 2 猜對: {len(self.player2_guesses)} 個地雷")
    
    def run(self):
        """運行遊戲"""
        self.clear_screen()
        print("="*50)
        print("   歡迎來到雙人對戰掃雷遊戲！")
        print("="*50)
        print(f"\n遊戲規則：")
        print(f"- 遊戲範圍: {self.ROWS}×{self.COLS}")
        print(f"- 每個玩家有 {self.MINES} 個地雷要隱藏")
        print(f"- 輪流猜測對方的地雷位置")
        print(f"- 猜中地雷可以繼續猜測")
        print(f"- 沒有猜中則換人")
        print(f"- 先猜完對方所有地雷的玩家獲勝！\n")
        
        input("按 Enter 開始遊戲...")
        
        # 設置階段
        self.setup_phase()
        
        # 遊戲階段
        self.state = GameState.PLAYING
        while self.state == GameState.PLAYING:
            self.play_turn()
        
        # 顯示結果
        self.print_winner()

def main():
    game = MinesweeperGame()
    game.run()
    
    while True:
        play_again = input("\n想要再玩一次嗎？ (yes/no): ").strip().lower()
        if play_again in ['yes', 'y']:
            game = MinesweeperGame()
            game.run()
        else:
            print("\n感謝遊玩！再見！")
            break

if __name__ == "__main__":
    main()
