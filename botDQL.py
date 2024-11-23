import minesweeper as ms
import model
import numpy as np
import random
import matplotlib.pyplot as plt
import pygame
import torch
import torch.optim as optim

class bot_DQL():
  def __init__(self,game,input_dim,output_dim,epsilon):
    self.game = game
    self.input_dim = input_dim
    self.output_dim = output_dim
    self.model_ = model.DQN(self.input_dim,self.output_dim)
    
    self.grid_size = input_dim
    self.grid_len = int(input_dim / 6)

    self.won = 0
    self.lost = 0
    self.num_episodes = 200
    self.epsilon_min = 0.001
    self.epsilon_decay = 0.99
    self.epsilon = epsilon

    
    self.num_episodes_test = 10
    self.win_test = 0
    self.lost_test = 0
    self.lr = 0.1 #learning rate
    self.gamma = 0.8
    self.alpha = 0.1
    #self.optimizer = optim.Adam(params=self.model_.parameters(),lr=self.lr)
    self.optimizer = optim.SGD(self.model_.parameters(),lr=self.lr)
    self.criterion = torch.nn.MSELoss()

  def start_game(self):
    self.game.pelikentta_alustus(6,6,3)
        

  def reset_game(self):
    self.recent_moves = []
    self.flag_count = 0
    self.step = 0
    self.game.nollaus()
    self.game.pelikentta_alustus(6,6,3)

  
  def train(self,screen):
    
    for episode in range(self.num_episodes):
      print(f"Episode {episode + 1} / {self.num_episodes}")
      self.reset_game()
      running = True
      state = self.get_state()
      self.epsilon = max(self.epsilon_min,self.epsilon * self.epsilon_decay)
      while running:
        
        
        action = self.choose_action(state)
        if action < self.grid_size:
          cell_index = action
        else:
          cell_index = action - self.grid_size
        x = cell_index // self.grid_len
        y = cell_index % self.grid_len
        self.execute_action(x,y,action)
        
        reward = self.calculate_reward(x,y,action)
        new_state = self.get_state()
        #print(reward)
        

        self.optimizer.zero_grad()
        q_values = self.model_(torch.FloatTensor(state).unsqueeze(0))
        target = q_values.clone().detach()
        target[0, action] = reward + self.gamma * torch.max(self.model_(torch.FloatTensor(new_state).unsqueeze(0)))
        loss = self.criterion(q_values, target)
        #print(f"Loss: {loss}")
        loss.backward()
        self.optimizer.step()

        state = new_state

        screen.fill((255, 255, 255))  # Clear the screen
        self.game.piirra_kentta(screen)  # Draw the game grid
        pygame.display.flip()
        if self.game.game_lost or self.game.win:
            running = False
         


  def test(self,screen):
    self.model_.eval()
    with torch.no_grad():
      for episode in range(self.num_episodes_test):
        print(f"Episode {episode + 1} / {self.num_episodes}")
        self.reset_game()
        running = True
        state = self.get_state()
        while running:
          
          
          q_values = self.model_(torch.FloatTensor(state).unsqueeze(0))
          action = np.argmax(q_values.detach().numpy()).item()
          print(action)
          if action < self.grid_size:
            cell_index = action
          else:
            cell_index = action - self.grid_size
          x = cell_index // self.grid_len
          y = cell_index % self.grid_len

          self.execute_action(x,y,action)
          state = self.get_state()
          screen.fill((255, 255, 255))  # Clear the screen
          self.game.piirra_kentta(screen)  # Draw the game grid
          pygame.display.flip()
          if self.game.game_lost:
            running = False
            self.win_test += 1
          if self.game.win:
            running = False
            self.lost_test += 1



  def choose_action(self,state):
    if random.random() < self.epsilon:
      action = random.randint(0,self.output_dim - 1)
    else:
      q_values = self.model_(torch.FloatTensor(state).unsqueeze(0))
      action = np.argmax(q_values.detach().numpy()).item()
    return action


  def execute_action(self,x,y,action):
    if action < self.grid_size:
      self.game.kasittele_hiiri(x,y,"vasen")
    else:
      self.game.kasittele_hiiri(x,y,"oikea")

  def is_mine(self,x,y):
      if self.game.tila["kentta"][y][x] == "x":
          return True
      return False

  def is_safe(self,x,y):
      if self.game.tila["kentta"][y][x] != "x":
          return True
      return False
  def is_unopened(self,x,y):
    if self.game.tila["pelikentta"][y][x] == " ":
      return True
    return False
  def is_flag(self,x,y):
    if self.game.tila["pelikentta"][y][x] == "f":
      return True
    return False
  
  def all_flags_cor(self):
    flagged_cells = [
            (x, y)
            for y in range(len(self.game.tila["pelikentta"]))
            for x in range(len(self.game.tila["pelikentta"][0]))
            if self.game.tila["pelikentta"][y][x] == "f"
        ]
    for (x,y) in flagged_cells:
        if not self.is_mine(x,y):
            return False
    return True


  def calculate_reward(self,x,y,action):
    if self.game.win:
      reward = 100
      print(f"Win reward: {reward}")
      self.won += 1
      return reward
    if self.game.game_lost:
      reward = -50
      print(f"Losing reward: {reward}")

      self.lost += 1
      return reward

    if action < self.grid_size:
      if self.is_unopened(x,y):
        reward = 10 
      else:
        reward = -1   
    else:
      if self.is_mine(x,y) and not self.is_flag(x,y):
        reward = 15
      elif self.is_flag(x,y):
        reward = -1
      else:
        reward = -10
      
      if self.all_flags_cor():
        reward += 20
      
    return reward

  def get_state(self):
    state = []
    for row in self.game.tila["pelikentta"]:
      for cell in row:
        if cell == " ":
          state.append(0)
        elif cell == "f":
          state.append(-1)
        elif cell == "x":
          state.append(-2)
        else:
          state.append(int(cell))
    return np.array(state)



def main():
  game = ms.Minesweeper()
  Bot = bot_DQL(game,36,36*2,epsilon=0.15)
  Bot.start_game()
  game.run_game(Bot)

if __name__ == "__main__":
  main()
  
    

