import minesweeper
import numpy as np
import random
from collections import defaultdict
import matplotlib.pyplot as plt
import pygame

"""
Teaching bot to play minesweeper game using Q-learning
"""

class Minesweeper_Bot:

    def __init__(self,game,epsilon):
        self.game = game

        self.actions = ["vasen", "oikea"]

        self.recent_moves = []
        self.flagged_cell = []
        self.flag_count = self.game.pelitiedot["Miinat"]
        self.step = 0
        self.unrevealed_squares = None

        self.num_episodes = 5000
        self.num_episodes_test = 100

        
        self.reward_lose = -50
        self.reward_win = 100
        self.basic_reward = 10
        self.reward_cor_mine = 10

        self.alpha = 0.1  # Learning rate
        self.gamma = 0.8 # Future reward discount factor
        self.epsilon = epsilon  # Exploration rate

        
        
        self.won = 0
        self.lost = 0
        self.won_test = 0
        self.lost_test = 0
        self.Q_table = defaultdict(lambda: np.zeros(2))
        

    def start_game(self):
        self.game.pelikentta_alustus(6,6,3)
        

    def reset_game(self):
        self.recent_moves = []
        self.flag_count = 0
        self.step = 0
        self.game.nollaus()
        self.game.pelikentta_alustus(6,6,3)



    
    def train(self,screen):
        """Bot makes a single move and updates the Q-table."""
        episode = 0
        while episode < self.num_episodes:
          print(f"Episode {episode + 1} / {self.num_episodes}")
          self.reset_game()
          running = True
          while running:
            coord = self.choose_coord()

            """if self.flag_count < self.game.pelitiedot["Miinat"]:"""

            x,y = coord
            state = self.get_surrounding_state(x,y)
            action = self.select_action(state)
            if action == 1:
                self.flag_count += 1
            reward = self.perform_action(x,y,action)
            new_state = self.get_surrounding_state(x,y)  # Get the new state after the action
            self.update_q_table(state,action,reward,new_state)
                  
                
            """else:
                flag_coord = self.choose_flag()
                x,y = flag_coord
                state = self.get_surrounding_state(x,y)
                action = self.select_action(state)
                reward = self.perform_action(x,y,action)
                new_state = self.get_surrounding_state(x,y)  # Get the new state after the action
                self.update_q_table(state,action,reward,new_state)"""

                
            screen.fill((255, 255, 255))  # Clear the screen
            self.game.piirra_kentta(screen)  # Draw the game grid
            pygame.display.flip()
            if self.game.game_lost:
                episode += 1
                running = False
            if self.game.win:
                episode += 1
                running = False 

    def test(self,screen):
        
        self.epsilon = 0
        self.training = False
        episode = 0
        while episode < self.num_episodes_test:
          self.reset_game()
          running = True
          print(f"Testing episode: {episode+1} / {self.num_episodes_test}")
          while running:
   
            coord = self.choose_coord() 
            x,y = coord
            state = self.get_surrounding_state(x,y)
            #state = self.get_state()
            action = self.select_action(state)
            self.perform_action_test(x,y,action)
            self.step += 1


            screen.fill((255, 255, 255))  # Clear the screen
            self.game.piirra_kentta(screen)  # Draw the game grid
            pygame.display.flip()
            if self.game.game_lost:
                episode += 1
                self.lost_test += 1
                running = False
            if self.game.win:
                episode += 1
                self.won_test += 1
                running = False      


    
    def is_mine(self,x,y):
        if self.game.tila["kentta"][y][x] == "x":
            return True
        return False

    def is_safe(self,x,y):
        if self.game.tila["kentta"][y][x] != "x":
            return True
        return False
    
    def is_flagged(self,x,y):
        if self.game.tila["kentta"][y][x] == "f":
            return True
        return False
    
    def perform_action(self,x,y,action_idx):
        self.game.kasittele_hiiri(x,y,self.actions[action_idx])
    
        if self.game.win:
            reward = self.reward_win
            self.won += 1
            return reward
        if self.game.game_lost:
            reward = self.reward_lose
            self.lost += 1
            return reward

        if action_idx == 0:    
            reward = self.basic_reward
                
        elif action_idx == 1:
            if self.is_flagged(x,y):
                self.flag_count += 1
                reward = 0
            else:
                self.flag_count -= 1
                if self.is_mine(x,y):
                    reward = self.reward_cor_mine
                else:
                    reward = -10
        if self.flag_count == 0 and not self.game.game_lost:
            reward -= 5
        return reward
        
        
        
    
    def perform_action_test(self,x,y,action):
        """Performing an action for testing the q-table"""
        self.game.kasittele_hiiri(x,y,self.actions[action])
        #time.sleep(0.5)
    
    def update_q_table(self, state, action_idx, reward, new_state):
        """Update the Q-table based on the action taken and the new state."""

        best_next_action = np.argmax(self.Q_table[new_state])
        td_target = reward + self.gamma * self.Q_table[new_state][best_next_action]
        td_delta = td_target - self.Q_table[state][action_idx]
        self.Q_table[state][action_idx] += self.alpha * td_delta
    

    def choose_coord(self):
        """Choosing coordinates that the bot will do action to"""
        self.unrevealed_squares = [
            (x, y)
            for y in range(len(self.game.tila["pelikentta"]))
            for x in range(len(self.game.tila["pelikentta"][0]))
            if self.game.tila["pelikentta"][y][x] == " "
        ]
        best_cell = []
        
        if self.unrevealed_squares:
            if np.random.uniform() < self.epsilon:
                return random.choice(self.unrevealed_squares)
            else:
                best_q = -100000
                for coord in self.unrevealed_squares:
                    x,y = coord
                    surrounding_state = self.get_surrounding_state(x, y)
                    q_values = self.Q_table.get(surrounding_state, [0] * 2)
                    if np.max(q_values) > best_q:
                        best_q = np.max(q_values)
                        best_cell = [coord]
                    elif np.max(q_values) == best_q:
                        best_cell.append(coord)
                return random.choice(best_cell)
        

    def select_action(self, state):
        
        if np.random.uniform() < self.epsilon:
            action_index = random.choice([0, 1]) #Explore
            #print("Random move")
        else:
            action_index = np.argmax(self.Q_table[state])  # Exploit
        
        
        return action_index


    def get_surrounding_state(self, x, y):
        """State representation includes current cell status and surrounding info"""
        board = self.game.tila["pelikentta"]
        surrounding_states = []
        remaining_flags = self.flag_count

        for dx in range(-1, 2):  # -1, 0, 1 for x direction
            for dy in range(-1, 2):  # -1, 0, 1 for y direction
                if dx == 0 and dy == 0:
                    continue  # Skip the current cell itself
                new_x, new_y = x + dx, y + dy
                # Check if the new coordinates are within the bounds of the board
                if 0 <= new_x < len(board[0]) and 0 <= new_y < len(board):
                    surrounding_states.append(board[new_y][new_x])

        # Add the current cell's status and remaining flags to the state
        return (tuple(surrounding_states), remaining_flags)





    def visualize_q_values(self):
        """Visualize the Q-table as a heatmap for each action."""

        # Initialize heatmaps for each action
        left_click_q_values = []
        flag_q_values = []
        states = list(self.Q_table.keys())

        for state in states:
            left_click_q_values.append(self.Q_table[state][0])  # Q-value for 'vasen' (left-click)
            flag_q_values.append(self.Q_table[state][1])       # For "oikea" (flag)

        # Populate the heatmaps with Q-values from the Q-table

        # Left click heatmap
        plt.figure(figsize=(10, 6))

        # Plot for left-click Q-values
        plt.scatter(range(len(left_click_q_values)), left_click_q_values, label="Left-click (Action 0)", color='blue', marker='o')

        # Plot for flag Q-values
        plt.scatter(range(len(flag_q_values)), flag_q_values, label="Flag (Action 1)", color='red', marker='x')

        # Add titles and labels
        plt.title("Q-Values for Each State-Action Pair")
        plt.xlabel("State Index")
        plt.ylabel("Q-Value")
        plt.legend()  # Add a legend to differentiate actions
        plt.show()


def main():
    game = minesweeper.Minesweeper()
    Bot = Minesweeper_Bot(game,epsilon=0.15)
    Bot.start_game()
    game.run_game(Bot)
    
    

if __name__ == "__main__":
    main()
