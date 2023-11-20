import sys
import os
import tkinter as tk
import time
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageFilter
from threading import Thread

from .config import *
from .utils import algorithm, Board, A_STAR, BFS, DFS, UCS, Greedy, BEAM_SEARCH, Hill_Climbing


class EightPuzzle(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title('8-Puzzle Game')
        self.geometry('950x750')
        self.resizable(False, False)
        self.iconbitmap('src/assets/images/app.ico')
        self.protocol('WM_DELETE_WINDOW', lambda: os._exit(0))

        self.container = tk.Frame(self)
        self.container.pack(side='top', fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.show_frame(PuzzlePage, **BASIC_FRAME_PROPERTIES)

    def show_frame(self, page, *args, **kwargs):
        frame = page(self.container, self, *args, **kwargs)
        frame.grid(row=0, column=0, sticky='nsew')
        frame.tkraise()


class PuzzlePage(tk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.controller = controller

        self.moves = 0
        self.board = []

        self.available_algorithms = [
            algorithm('A*', A_STAR),
            algorithm('BFS', BFS),
            algorithm('DFS', DFS),
            algorithm('UCS', UCS),
            algorithm('Greedy', Greedy),
            algorithm('BEAM_SEARCH', BEAM_SEARCH),
            algorithm('Hill Climbing', Hill_Climbing),

        ]
        
        self.frame_algorithms = tk.Frame(self, **BASIC_FRAME_PROPERTIES)
        self.frame_algorithms.pack(side='right', fill='y',padx=10, pady=200)

        self.create_algorithm_buttons()
        
        self.algorithm_index = 0
        self.algorithm = self.available_algorithms[0]

        self.current_board_state = tuple(range(9))
        self.goal_board_state = tuple(range(9))
        self.saved_board_state = tuple(range(9))

        self.tile_images = [ImageTk.PhotoImage(Image.open(
            f'src/assets/images/tile_{n}.png')) for n in range(9)]

        self.is_stopped = False
        self.is_solving = False
        self.is_done = False

        self.display_widgets()
        
        self.label_time = tk.Label(self.frame_puzzle, text='Time: 0.0000 second(s)', **TEXT_LABEL_PROPERTIES)
        self.label_time.grid(row=0, column=3, sticky='ew', padx=10, pady=5)
    
    def update_time_label(self, time_elapsed):
        # Định dạng thời gian với 4 chữ số thập phân
        time_string = f"Time: {time_elapsed:.4f} second(s)"
        self.label_time.configure(text=time_string)

        
        
    def create_algorithm_buttons(self):
        for alg in self.available_algorithms:
            button = tk.Button(self.frame_algorithms, text=alg.name,
                               command=lambda alg=alg: self.set_algorithm(alg),
                               **ALGORITHMS_BUTTON_PROPERTIES)
            button.pack(pady=10)
            
    def set_algorithm(self, algorithm):
        self.algorithm = algorithm
        self.label_subheading.configure(text=f'{self.algorithm.name} algorithm')
        self.reset_board()
    
    def update_time_label(self, time_elapsed):
        self.label_time.configure(text=f'Time: {round(time_elapsed, 4)} second(s)')

    def display_widgets(self):
        # Title section
        self.frame_title = tk.Frame(self, **BASIC_FRAME_PROPERTIES)
        self.frame_title.pack(pady=25)

        self.label_heading = tk.Label(
            self.frame_title, text='8-Puzzle Game', **HEADING_LABEL_PROPERTIES)
        self.label_heading.pack()

        self.label_subheading = tk.Label(
            self.frame_title, text=f'{self.algorithm.name} algorithm', **SUBHEADING_LABEL_PROPERTIES)
        self.label_subheading.pack()

        # Puzzle section
        self.frame_puzzle = tk.Frame(self, **BASIC_FRAME_PROPERTIES)
        self.frame_puzzle.pack(padx=10, pady=10)
        # Replace with the path to your image file
        image = Image.open("src/assets/images/landmark81.png")
        image = image.resize((100, 100))  # Resize the image to 50x50
        img = ImageTk.PhotoImage(image)

        self.image_label = tk.Label(self.frame_puzzle, image=img)
        self.image_label.image = img  # Important to keep a reference
        self.image_label.grid(row=2, column=4, padx=10, pady=10)
        # Button section
        self.frame_buttons = tk.Frame(self, **BASIC_FRAME_PROPERTIES)
        self.frame_buttons.pack(pady=20)
        
        self.button_solve = tk.Button(self.frame_buttons, text='solve',
                                      command=lambda: self.solve_board(), **PRIMARY_BUTTON_PROPERTIES)
        self.button_solve.grid(row=0, column=0, padx=10, pady=10)

        self.button_shuffle = tk.Button(self.frame_buttons, text='shuffle',
                                        command=lambda: self.shuffle_board(), **PRIMARY_BUTTON_PROPERTIES)
        self.button_shuffle.grid(row=0, column=2, padx=10, pady=10)

        # import images
        self.button_image = tk.Button(self.frame_buttons, text='Image',
                                      command=lambda: self.load_image(), **PRIMARY_BUTTON_PROPERTIES)
        self.button_image.grid(row=0, column=4, padx=10, pady=10)

        self.label_moves = tk.Label(
            self.frame_puzzle, text=f'Moves: {self.moves}', **TEXT_LABEL_PROPERTIES)
        self.label_moves.grid(row=0, column=0, sticky='w', padx=10, pady=5)

        self.label_status = tk.Label(
            self.frame_puzzle, text=f'Playing...', **TEXT_LABEL_PROPERTIES)
        self.label_status.grid(row=0, column=1, sticky='e', padx=10, pady=5)
        
        # self.label_time = tk.Label(
        #     self.frame_puzzle, text=f'Time:', **TEXT_LABEL_PROPERTIES)
        # self.label_time.grid(row=0, column=3, sticky='ew', padx=10, pady=5)

        self.separator = ttk.Separator(self.frame_puzzle, orient='horizontal')
        self.separator.grid(row=1, columnspan=4, sticky='ew', pady=10)

        self.frame_board = tk.Frame(
            self.frame_puzzle, **BASIC_FRAME_PROPERTIES)
        self.frame_board.grid(row=2, columnspan=2)

        self.initialize_board()
        self.shuffle_board()

        self.controller.bind('<Up>', lambda event: self.transform_keys('D'))
        self.controller.bind('<Down>', lambda event: self.transform_keys('U'))
        self.controller.bind('<Left>', lambda event: self.transform_keys('R'))
        self.controller.bind('<Right>', lambda event: self.transform_keys('L'))

    def initialize_board(self):
        for index in range(9):
            self.board.append(
                tk.Button(self.frame_board, **TILE_BUTTON_PROPERTIES))
            self.board[index].grid(
                row=index // 3, column=index % 3, padx=5, pady=5)

    def populate_board(self, state, delay_time=0):
        for tile_index, tile_value in enumerate(state):
            self.board[tile_index].configure(
                image=self.tile_images[tile_value],
                text=tile_value,
                state='normal',
                command=lambda tile_index=tile_index: self.transform_click(
                    tile_index)
            )

            if tile_value == 0:
                self.board[tile_index].configure(state='disabled')

        self.current_board_state = state
        # Replace with the path to your image file
        image = Image.open("src/assets/images/landmark81.png")
        image = image.resize((300, 300))  # Resize the image to 50x50
        img = ImageTk.PhotoImage(image)

        self.image_label = tk.Label(self.frame_puzzle, image=img)
        self.image_label.image = img  # Important to keep a reference
        self.image_label.grid(row=2, column=3, padx=50, pady=10)
        time.sleep(delay_time)

    def solve_board(self):
        if not self.is_solving:
            self.reset_board()
            self.solution_thread = Thread(target=self.run_solution)
            self.solution_thread.start()

    def run_solution(self):
        self.is_stopped = False
        self.is_solving = True
        self.is_done = False
        self.update_status('Solving...')

        print('\nFinding solution...')

        path_to_goal, nodes_expanded, max_search_depth, time_elapsed = Board.solve(
            self.current_board_state, self.algorithm.func)

        self.controller.after(0, self.update_time_label, time_elapsed)
        
        if not self.is_stopped:
            print(
                f'Done in {round(time_elapsed, 4)} second(s) with {len(path_to_goal)} moves using {self.algorithm.name}')
            print(
                f'Has a max search depth of {max_search_depth} and nodes expanded of {nodes_expanded}')
            print('Actions:', *path_to_goal)
        else:
            print('Stopped')

        if path_to_goal:
            print('\nMoving board...')
            self.update_status('Moving...')

            delay_time = 0.01
            time.sleep(delay_time)

            for action in path_to_goal:
                if self.is_stopped:
                    print('Stopped')
                    self.update_status('Playing...')
                    break
                else:
                    self.transform_state(action, delay_time=0.01)
            else:
                print('Done board animation')
                self.update_status('Solved!')
                self.is_done = True

            self.is_solving = False

        else:
            self.is_solving = False
            self.update_status('Playing...')

    def reset_board(self):
        self.stop_solution()
        self.update_moves(0)
        self.update_status('Playing...')
        self.populate_board(state=self.saved_board_state)

    def shuffle_board(self):
        
        self.saved_board_state = Board.create_solvable_state()
        self.reset_board()

    def stop_solution(self):
        if self.is_solving and not self.is_stopped:
            self.is_stopped = True
        self.is_done = False

    # Load images
    # def load_image(self):
    #     image_path = filedialog.askopenfilename(
    #         filetypes=[('Image Files', '*.png;*.jpg;*.jpeg')])
    #     image = Image.open(image_path)
    #     image = image.resize((300, 300))
    #     piece_size = image.size[0] // 3
    #     self.tile_images = []
    #     main = image
    #     main_path = f'src/assets/images/landmark81.png'
    #     main.save(main_path)
    #     for i in range(3):
    #         for j in range(3):
    #             if i == 0 and j == 0:
    #                 tk_piece = ImageTk.PhotoImage(
    #                     Image.open('src/assets/images/tile_0.png'))
    #             else:
    #                 left = j * piece_size
    #                 upper = i * piece_size
    #                 right = left + piece_size
    #                 lower = upper + piece_size
    #                 piece = image.crop((left, upper, right, lower))

    #                 piece_path = f'src/assets/images/tile_{3*i+j}.png'
    #                 piece.save(piece_path)
    #                 tk_piece = ImageTk.PhotoImage(piece)
    #             self.tile_images.append(tk_piece)
    #     self.reset_board()

    def load_image(self):
        image_path = filedialog.askopenfilename(
            filetypes=[('Image Files', '*.png;*.jpg;*.jpeg')])
        image = Image.open(image_path)
        image = image.resize((300, 300))
        piece_size = image.size[0] // 3
        self.tile_images = []

        # Create a blurred version of the original image for the puzzle tile
        main_blurred = image.copy()
        # Adjust the blur radius as needed
        main_blurred = main_blurred.filter(ImageFilter.GaussianBlur(10))

        for i in range(3):
            for j in range(3):
                left = j * piece_size
                upper = i * piece_size
                right = left + piece_size
                lower = upper + piece_size
                piece = image.crop((left, upper, right, lower))

                piece_path = f'src/assets/images/tile_{3*i+j}.png'
                piece.save(piece_path)
                tk_piece = ImageTk.PhotoImage(piece)
                self.tile_images.append(tk_piece)

        # Create the blurred puzzle tile
        main_path = 'src/assets/images/landmark81.png'
        main_blurred.save(main_path)

        self.reset_board()

    def transform_click(self, tile_index):
        possible_actions = Board.valid_actions(self.current_board_state)
        blank_index = self.current_board_state.index(0)
        tile_value = int(self.board[tile_index].cget('text'))

        for action in possible_actions:
            if not self.is_solving and not self.is_done:
                if action == 'U' and self.current_board_state[blank_index - 3] == tile_value:
                    self.transform_state(action)

                elif action == 'D' and self.current_board_state[blank_index + 3] == tile_value:
                    self.transform_state(action)

                elif action == 'L' and self.current_board_state[blank_index - 1] == tile_value:
                    self.transform_state(action)

                elif action == 'R' and self.current_board_state[blank_index + 1] == tile_value:
                    self.transform_state(action)

        if not self.is_done and self.current_board_state == self.goal_board_state:
            self.update_status('Well done!')
            self.is_done = True

    def transform_keys(self, action):
        if not self.is_solving and not self.is_done:
            if action in Board.valid_actions(self.current_board_state):
                self.transform_state(action)

        if not self.is_done and self.current_board_state == self.goal_board_state:
            self.update_status('Well done!')
            self.is_done = True

    def transform_state(self, action, delay_time=0):
        new_state = Board.transform(self.current_board_state, action)

        current_index = self.current_board_state.index(0)
        new_index = new_state.index(0)

        first_tile = self.board[current_index]
        second_tile = self.board[new_index]

        first_tile_properties = self.get_tile_property(first_tile)
        second_tile_properties = self.get_tile_property(second_tile)

        self.set_tile_property(first_tile, second_tile_properties)
        self.set_tile_property(second_tile, first_tile_properties)

        self.current_board_state = new_state

        if not self.is_done:
            self.update_moves(self.moves + 1)

        time.sleep(delay_time)

    def get_tile_property(self, tile):
        return {
            'text': tile.cget('text'),
            'background': tile.cget('background'),
            'image': tile.cget('image'),
            'state': tile.cget('state')
        }

    def set_tile_property(self, tile, properties):
        tile.configure(**properties)

    def update_moves(self, moves):
        self.moves = moves
        self.label_moves.configure(text=f'Moves: {self.moves}')

    def update_status(self, status):
        self.label_status.configure(text=status)
