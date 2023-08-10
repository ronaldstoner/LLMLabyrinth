import os
import time 
from textwrap import dedent
import shutil
import random
from langchain.llms import GPT4All

# Function to clear the console
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# Function to print centered text
def center_text(text):
    terminal_width = shutil.get_terminal_size().columns
    for line in text.split('\n'):
        centered_text = line.center(terminal_width)
        print(centered_text)

ascii_art = '''

 _      _     ___  ___ _           _                _       _   _     
| |    | |    |  \/  || |         | |              (_)     | | | |    
| |    | |    | .  . || |     __ _| |__  _   _ _ __ _ _ __ | |_| |__  
| |    | |    | |\/| || |    / _` | '_ \| | | | '__| | '_ \| __| '_ \ 
| |____| |____| |  | || |___| (_| | |_) | |_| | |  | | | | | |_| | | |
\_____/\_____/\_|  |_/\_____/\__,_|_.__/ \__, |_|  |_|_| |_|\__|_| |_|
                                          __/ |                       
                                         |___/                          

'''

subtitle = "An AI generated text-based adventure game."
subtitle_2 = "Your game is now generating..."

class Game():
    directions = {"n": [-1, 0], "s": [1, 0], "e": [0, 1], "w": [0, -1]}  # Direction vectors
    dir_full_names = {"n": "North", "s": "South", "e": "East", "w": "West"}  # Direction full names
    items = ["matches", "gas", "lamp"]
    room_desc = {}
    room_items = {}

    room_themes = ["mysterious", "spooky", "sombre", "abandoned", "enchanting", "bizarre", "rustic", "futuristic", "vintage", "tropical", "arctic", "underwater", "celestial", "royal", "minimalist", "urban", "industrial", "floral", "gothic", "fairytale", "western", "post-apocalyptic", "medieval", "Asian-inspired", "jungle", "space", "victorian", "pirate", "exotic", "farmhouse", "ocean", "desert", "rainforest", "cave", "nautical", "alpine", "beach", "magic", "jazz", "steampunk"]

    def __init__(self, llm):
        self.llm = llm
        self.current_position = [2, 2]  # Starting at the center of the map.
        self.current_room = self.get_room_id(self.current_position)
        self.inventory = []
        self.last_room = None
        self.command = ""

        # Print opening screen/intro
        clear()
        center_text(ascii_art)
        center_text(subtitle)
        center_text(subtitle_2)
        time.sleep(5) # Wait for 5 seconds
        clear()

        # Place items in rooms
        for i in range(5):
            for j in range(5):
                room = self.get_room_id([i,j])
                self.place_items(room)

    def get_room_id(self, position):
        """ Generate a unique room ID based on map coordinates """
        return f"room_{position[0]}_{position[1]}"

    def generate_room_description(self, room):
        if room not in self.room_desc:
            # Only generate a new description if the room hasn't been visited before.
            theme = random.choice(self.room_themes)
            mood_list = ["cheerful", "mournful", "tranquil", "chaotic", "serene", "eerie", "tense", "mystical"]
            size_list = ["spacious", "compact", "vast", "tiny", "roomy", "cramped", "immense", "cosy"]
            weather_list = ["stormy", "sunny", "rainy", "foggy", "windy", "snowy", "cloudy", "starlit"]

            modifier_dict = {"mood": random.choice(mood_list), "size": random.choice(size_list), "weather": random.choice(weather_list)}

            # Randomly choose a modifier
            modifier = random.choice(list(modifier_dict.keys()))

            prompt = f"Describe a scene in a {modifier_dict[modifier]} {theme} room."
 
            #prompt = f"Describe a scene in a {theme} room."
            room_desc_subsequent = self.llm(prompt)
            room_title = f"A {theme.title()} Room"
            self.room_desc[room] = (room_title, room_desc_subsequent)

    """
    This method randomly assigns items to rooms at the start of the game.
    """
    def place_items(self, room):
        self.room_items[room] = []
        
        for item in self.items:
            if item not in [item for sublist in self.room_items.values() for item in sublist] and random.uniform(0, 1) < 0.1:
                self.room_items[room].append(item)

    def run(self):
        while True:
            self.current_room = self.get_room_id(self.current_position)
            self.generate_room_description(self.current_room) 
            
            if self.current_room != self.last_room:
                title, desc = self.room_desc[self.current_room]
                print(f"\n\033[1m{title}\033[0m")
                print(desc)

            if self.room_items[self.current_room]:
                bolded_items = [f"\033[1m{item}\033[0m" for item in self.room_items[self.current_room]] 
                print(f"\nYou see {', '.join(bolded_items)} in the room.")

            self.print_possible_directions()
            self.command = input(">").lower()
            self.process_command(self.command)
            self.last_room = self.current_room  # update last_room at the end of running a command

    def print_possible_directions(self):
        possible_directions = []

        for direction, delta in self.directions.items():
            next_position = [sum(x) for x in zip(self.current_position, delta)]
            if all(0 <= i < 5 for i in next_position):
                possible_directions.append(f"{self.dir_full_names[direction]}")
        print("\nPossible directions: ", ', '.join(possible_directions))

    def print_inventory(self):
        print("\nInventory:")
        if not self.inventory:
            print("No items in the inventory.")
        else:
            for item in self.inventory:
                print(f"- \033[1m{item}\033[0m")

    def process_command(self, command):
        if command in self.directions:
            self.move_room(command)
        elif command.startswith("pick up") or command.startswith("get") or command.startswith("g"):
            item = command.split(" ")[-1]
            if item in self.room_items[self.current_room]:
                print(f"\nYou have picked up \033[1m{item}\033[0m!")
                self.inventory.append(item)
                self.room_items[self.current_room].remove(item)
                if len(self.inventory) == len(self.items):
                    print("\nYou have all the items! Now, \033[1mcombine\033[0m them to win the game.")
            else:
                print(f"\nCannot find {item} in the room.")
        elif command == "i" or command == "inv" or command == "inventory":
            self.print_inventory()
        elif command == "l" or command == "look":
            self.look()
        elif command.startswith("combine") or command.startswith("c"):
            items = command.split(" ")[1:]
            if set(items) == set(self.inventory) and len(items) == len(self.items):
                print("\nCongratulations, you've won!")
                exit(0)
            else:
                print("You cannot combine these items.")
        elif command == "q" or command == "quit" or command == "exit":
            print("\nYou have left your adventure.")
            exit(0)
        else:
            print("Unknown command")

    def look(self):
        title, desc = self.room_desc[self.current_room]
        print(f"\n\033[1m{title}\033[0m")
        print(desc)
    
    def move_room(self, direction):
        next_position = [sum(x) for x in zip(self.current_position, self.directions[direction])]
        if all(0 <= i < 5 for i in next_position):
            self.current_position = next_position
        else:
            print(f"You cannot go {self.dir_full_names[direction]} from here.")

if __name__ == "__main__":
    model_path = 'models/ggml-gpt4all-j-v1.3-groovy.bin' # replace with your model path
    llm = GPT4All(model=model_path, max_tokens=512, backend='gptj', n_batch=16, verbose=False)
    Game(llm).run()
