import chess
import pygame
from chess import engine
from pygame import mixer

pygame.init()

# window
screen_size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
pygame.display.set_caption("ChessPy")
win = pygame.display.set_mode(screen_size)
board_surface = pygame.Surface((600, 600))
FPS = 60
clock = pygame.time.Clock()
pieces_dict = {}
Square_size = 600 // 8

# colours
magenta = (214, 2, 112)
blue = (0, 56, 168)
lavender = (155, 79, 150)
pastel_blue = (208, 242, 221)
white = (255, 255, 255)
black = (0, 0, 0)
light_colours = [pygame.Color('cornsilk2'), (196, 196, 196), magenta, (245, 169, 184), (33, 177, 255), (254, 244, 51)]
dark_colours = [pygame.Color('chartreuse4'), (97, 97, 97), blue, (91, 205, 250), (255, 216, 0), (154, 89, 207)]
background_colour = [pastel_blue, (142, 142, 142), lavender, white, (255, 33, 240,), white]
themes = ['Default', 'Gray Scale', 'More', 'Truth', 'Equal', 'Interstitial']
piece_variants = ['classic', 'neo', 'wood']

# settings
colour_mode = 0
Undo = True
piece_mode = 0
Music = True
VFX = True
Volume = 20

# images
main_menu_bg = pygame.image.load('Images/Backgrounds/bg_image_night_sized.jpeg').convert()
game_bg = pygame.image.load('Images/Backgrounds/wood_bg.png').convert()
undo_button_img = pygame.image.load('Images/Buttons/undo_button.png').convert()
undo_button_img.set_colorkey(white)
reset_button_img = pygame.image.load('Images/Buttons/reset_button.png').convert()
reset_button_img.set_colorkey(white)
back_button_img = pygame.image.load('Images/Buttons/back_button.png').convert()
back_button_img.set_colorkey(white)

# font
font_30 = pygame.font.Font('Fonts/Pixellettersfull-BnJ5.ttf', 30)
font_50 = pygame.font.Font('Fonts/Pixellettersfull-BnJ5.ttf', 50)
font_70 = pygame.font.Font('Fonts/Pixellettersfull-BnJ5.ttf', 70)
font_100 = pygame.font.Font('Fonts/Pixellettersfull-BnJ5.ttf', 100)
font_150 = pygame.font.Font('Fonts/Pixellettersfull-BnJ5.ttf', 150)

# misc
board = chess.Board()
RanksToRows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
RowsToRanks = {v: k for k, v in RanksToRows.items()}
FilesToCols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
ColsToFiles = {v: k for k, v in FilesToCols.items()}
player = True  # default True: player is white
# Sounds
'''
hall of the mountain king
vivaldi summer 3rd moment
vivaldi winter 1st moment
'''


def load():
    # load sprites
    pieces = ['wP', 'wR', 'wB', 'wN', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        piece_img = pygame.image.load("pieces/" + piece_variants[piece_mode] + '/' + piece + ".png")
        pieces_dict[piece] = pygame.transform.scale(piece_img, (Square_size, Square_size))


class Sounds:
    def __init__(self):
        if Music or VFX:
            mixer.init()
        if not Music and not VFX:
            mixer.quit()
        self.vol = Volume / 100

    def music_play(self, music, duration=-1, play=True):
        if Music:
            mixer.music.load(music)
            mixer.music.set_volume(self.vol)
            if play:
                mixer.music.play(duration)

    def rewind_music(self):
        mixer.music.rewind()

    def sound_play(self, sound):
        if VFX:
            play_sound = mixer.Sound(sound)
            play_sound.set_volume(self.vol)
            mixer.Sound.play(play_sound)

    def stop_music(self):
        mixer.music.stop()

    def unload_music(self):
        mixer.music.unload()

    def transition(self, music, duration):
        # duration is in milliseconds
        mixer.music.fadeout(duration)
        self.unload_music()
        self.music_play(music)


class Board:
    def __init__(self, move, move_uci, sound):
        self.sound = sound
        self.move_is_legal = False
        self.game_over = False
        self.legal = board.legal_moves
        # print(move_uci)
        # print(move)
        for i in self.legal:
            if move_uci == str(i):
                self.move_is_legal = True
                board.push_san(move)
                # print(board)
                # print(board.legal_moves)
                if board.is_check():
                    self.sound = 'Sounds/VFX/move-check.wav'
                Sounds().sound_play(self.sound)
            else:
                pass
        self.insufficient_material = board.is_insufficient_material()
        self.mate = board.is_checkmate()
        self.stale = board.is_stalemate()

        if self.mate or self.stale:
            self.game_over = True
        else:
            self.game_over = False

    def undo(self):
        board.pop()
        # print(board)


class Slider:
    def __init__(self, surface, lenght, width, x, y, lenght_scale=1):
        self.surface = surface
        self.clicked = False
        self.maximum_lenght = lenght
        self.lenght = lenght
        self.width = width
        self.scale = lenght_scale
        self.x = x
        self.y = y
        self.slider_rect = pygame.Rect(x - 10, y - 20, (lenght * self.scale) + 25, width + 40)

    def draw_slider(self, lenght_var):
        self.lenght = lenght_var
        slider_surface = pygame.Surface((self.lenght * self.scale, self.width))
        slider_surface.fill((255, 255, 255))
        slider_head = pygame.Surface((20, 50))
        slider_head.fill((110, 110, 110))
        pos = pygame.mouse.get_pos()
        if self.slider_rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                if 0 <= pos[0] - self.x <= self.maximum_lenght * self.scale:
                    self.lenght = (pos[0] - self.x) // self.scale
            if pygame.mouse.get_pressed()[0] == 1:
                self.clicked = False
        pygame.draw.rect(win, (0, 0, 0), self.slider_rect)
        self.surface.blit(slider_surface, (self.x, self.y + 1))
        self.surface.blit(slider_head, (self.x + (self.lenght * self.scale) - 10, self.y + (self.width / 2) - 24))
        return self.lenght


class Button:
    # Creating a button
    def __init__(self, surface, x, y, image, scale=1):
        image_width = image.get_width()
        image_height = image.get_height()
        self.image = pygame.transform.scale(image, (int(image_width * scale), int(image_height * scale)))
        self.image_rect = image.get_rect(topleft=(x, y))
        self.surface = surface
        self.clicked = False

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.image_rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                # return true if button is pressed
                action = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        self.surface.blit(self.image, (self.image_rect.x, self.image_rect.y))
        return action


class MainMenu:
    def __init__(self):
        background = pygame.transform.scale(main_menu_bg, screen_size)
        win.blit(background, (0, 0))

        main_txt = font_150.render('ChessPy', True, white)
        single_player_txt = font_70.render('Single player', True, white)
        multi_player_txt = font_70.render('Multi player', True, white)
        settings_txt = font_70.render('Settings', True, white)
        quit_txt = font_70.render('Quit', True, white)

        global player
        player = True

        # button instances
        single_player_button = Button(win, 143, 400, single_player_txt, 1)
        multi_player_button = Button(win, 156, 500, multi_player_txt, 1)
        settings_button = Button(win, 206, 600, settings_txt, 1)
        quit_button = Button(win, 250, 700, quit_txt, 1)

        run = True
        win.blit(main_txt, (92, 200))

        while run:

            engine_play = Button.draw(single_player_button)
            multi_play = Button.draw(multi_player_button)
            is_settings = Button.draw(settings_button)
            is_exit = Button.draw(quit_button)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
            if engine_play:
                run = False
                SinglePlayer()
            if multi_play:
                run = False
                GameWindow(False)
            if is_settings:
                run = False
                Settings()
            if is_exit:
                run = False
            clock.tick(FPS)
            pygame.display.update()


class Settings:
    def __init__(self):
        self.surface = win
        self.background = pygame.transform.scale(main_menu_bg, screen_size)
        self.overlay = pygame.Surface(screen_size)
        self.overlay.fill(black)
        self.overlay.set_alpha(200)
        self.surface.blit(self.background, (0, 0))
        self.surface.blit(self.overlay, (0, 0))
        piece_txt = font_70.render(f'Pieces:           ', True, white)
        self.piece_button = Button(self.surface, 200, 400, piece_txt, 1)

        theme_txt = font_70.render(f'Theme:               ', True, white)
        self.theme_button = Button(self.surface, 200, 300, theme_txt, 1)

        self.undo_txt = font_70.render(f'Allow undo:      ', True, white)
        self.undo_button = Button(self.surface, 200, 200, self.undo_txt, 1)

        self.true_txt = font_70.render('True', True, white)
        self.false_txt = font_70.render('False', True, white)
        self.corner_txt = font_30.render('Press [esc] to go back', True, white)
        self.vol_txt = font_70.render('Volume:', True, white)
        music_txt = font_70.render(f'Music:      ', True, white)
        self.music_button = Button(self.surface, 800, 200, music_txt, 1)

        vfx_txt = font_70.render(f'VFX:        ', True, white)
        self.vfx_button = Button(self.surface, 805, 300, vfx_txt, 1)
        self.slider = Slider(self.surface, 100, 15, 1000, 425, 2)
        self.buttons()

    def buttons(self):
        global Music
        global VFX
        global colour_mode
        global piece_mode
        global Undo
        global Volume
        run = True
        button_pressed = False
        while run:
            self.surface.blit(self.corner_txt, (50, 50))
            is_music = Button.draw(self.music_button)
            is_undo = Button.draw(self.undo_button)
            is_theme = Button.draw(self.theme_button)
            is_piece = Button.draw(self.piece_button)
            is_vfx = Button.draw(self.vfx_button)
            volume = Slider.draw_slider(self.slider, Volume)
            Volume = volume
            self.surface.blit(self.vol_txt, (800, 400))
            volume_percent_txt = font_30.render((str(volume) + '%'), True, white)
            volume_percent_txt_bg = pygame.Surface((50, 30))
            volume_percent_txt_bg.fill((0, 0, 0))

            self.surface.blit(volume_percent_txt_bg, (1220, 417))
            self.surface.blit(volume_percent_txt, (1220, 417))
            # allow/forbid the use of undo
            if Undo:
                self.surface.blit(self.true_txt, (500, 200))
            else:
                self.surface.blit(self.false_txt, (500, 200))
            if is_undo:
                is_undo = False
                button_pressed = True
                Undo = not Undo

            if is_music:
                Music = not Music
                button_pressed = True

            if Music:
                self.surface.blit(self.true_txt, (970, 200))
            else:
                self.surface.blit(self.false_txt, (970, 200))

            if is_vfx:
                VFX = not VFX
                button_pressed = True

            if VFX:
                self.surface.blit(self.true_txt, (970, 300))
            else:
                self.surface.blit(self.false_txt, (970, 300))

            # choose theme
            if is_theme:
                button_pressed = True
                if colour_mode < len(themes) - 1:
                    colour_mode += 1
                else:
                    colour_mode = 0

            self.surface.blit(font_70.render(themes[colour_mode], True, white), (500, 302))
            colours = [pygame.Color(light_colours[colour_mode]), pygame.Color(dark_colours[colour_mode])]
            for row in range(2):
                for col in range(2):
                    colour = colours[(row + col) % 2]
                    pygame.draw.rect(self.surface, colour, pygame.Rect(
                        400 + (row * (Square_size // 3)), 310 + (col * (Square_size // 3)),
                        Square_size // 3, Square_size // 3))

            # choose piece style
            if is_piece:
                button_pressed = True
                if piece_mode < len(piece_variants) - 1:
                    piece_mode += 1
                else:
                    piece_mode = 0
            load()
            self.surface.blit(pieces_dict['wK'], (400, 400))
            self.surface.blit(pieces_dict['bK'], (500, 400))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                        MainMenu()

            clock.tick(FPS)
            pygame.display.update()

            if button_pressed:
                button_pressed = False
                self.surface.blit(self.background, (0, 0))
                self.surface.blit(self.overlay, (0, 0))


class SinglePlayer:
    def __init__(self):
        self.surface = win
        self.background = pygame.transform.scale(main_menu_bg, screen_size)
        self.surface.blit(self.background, (0, 0))
        self.overlay = pygame.Surface(screen_size)
        self.overlay.fill(black)
        self.overlay.set_alpha(200)
        self.surface.blit(self.overlay, (0, 0))
        self.play_colour_txt = font_100.render('Play as: ', True, white)
        self.difficulty_txt = font_100.render('Difficulty level: ', True, white)
        self.lvl_slider = Slider(self.surface, 130, 15, 650, 360, 2)

        self.play_as_white = Button(self.surface, 420, 200, pieces_dict['wK'], 1)
        self.play_as_black = Button(self.surface, 520, 200, pieces_dict['bK'], 1)

        self.depth = 12  # default 12
        self.gw = GameWindow
        self.buttons()

    def buttons(self):
        global player
        run = True
        colour_chosen = False
        engine_lvl = 0
        while run:
            self.surface.blit(self.play_colour_txt, (120, 200))
            self.surface.blit(self.difficulty_txt, (120, 325))
            lvl = Slider.draw_slider(self.lvl_slider, engine_lvl)
            engine_lvl = lvl
            lvl_chosen = ((12 + (engine_lvl // 15)) // 2) * 2
            self.depth = lvl_chosen
            lvl_indicate = (lvl // 24)
            lvl_display = font_100.render(str(lvl_indicate), True, white)
            self.surface.blit(lvl_display, (1020, 325))

            play_white = Button.draw(self.play_as_white)
            play_black = Button.draw(self.play_as_black)

            if play_white:
                player = True
                colour_chosen = True

            elif play_black:
                player = False
                colour_chosen = True

            if colour_chosen:
                run = False
                GameWindow(True, player, self.depth)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        MainMenu()
                        run = False
            clock.tick(FPS)
            pygame.display.update()

            self.surface.blit(self.background, (0, 0))
            self.surface.blit(self.overlay, (0, 0))


class GameState:
    def __init__(self):
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]

        self.invert_board = self.board[::-1]

        self.white_turn = True
        self.moves = []
        self.castle_white_kingside = False
        self.castle_white_queenside = False
        self.castle_black_kingside = False
        self.castle_black_queenside = False
        self.moves_castle = []
        self.legal = board.legal_moves
        self.close_window = False
        self.run_promote_menu = False
        self.prmt_confirm = '--'
        self.s = Sounds()
        self.is_endgame = False
        self.wQ_captured, self.bQ_captured = False, False
        self.music_transition = 0  # could be used for multiple transitions

    def move(self, move):  # registers the move
        if move.is_engine:
            self.engine_move(move)

        else:
            turn = ('w' if self.white_turn else 'b')
            if move.piece_moved[0] == turn:
                self.castling(move)
                if (move.piece_moved == 'wP' and move.endrow == 0) or (move.piece_moved == 'bP' and move.endrow == 7):
                    self.run_promote_menu = True
                else:
                    self.piece_notation(move)
                    if self.board[move.startrow][move.startcol] != '--' and self.b.move_is_legal:
                        # checks if the player clicked on a blank square and if it's their turn
                        self.board[move.startrow][move.startcol] = '--'  # set start square as blank
                        self.board[move.endrow][move.endcol] = move.piece_moved  # move the piece to end square
                        self.white_turn = not self.white_turn  # swap turns
                        self.moves.append(move)

                        if move.piece_captured == 'wQ':
                            self.wQ_captured = True

                        if move.piece_captured == 'bQ':
                            self.bQ_captured = True

                self.enpassant()

        if len(self.moves) > 50 or (self.wQ_captured and self.bQ_captured and len(self.moves) >= 20):
            self.is_endgame = True

        if self.is_endgame and self.music_transition == 0:
            self.music_transition += 1
            self.s.unload_music()
            self.s.music_play('Sounds/Music/endgame music.ogg')

    def engine_move(self, move):
        self.castling(move)
        self.enpassant()
        if (move.piece_moved == 'wP' and move.endrow == 0) or (move.piece_moved == 'bP' and move.endrow == 7):
            self.moves.append(move)
            if move.engine_prmt != '--':
                self.board[move.endrow][move.endcol] = move.engine_prmt
                self.board[move.startrow][move.startcol] = '--'
                self.moves.append(move)
        else:
            self.board[move.startrow][move.startcol] = '--'  # set start square as blank
            self.board[move.endrow][move.endcol] = move.piece_moved  # move the piece to end square
            self.moves.append(move)

            if move.piece_captured == 'wQ':
                self.wQ_captured = True

            if move.piece_captured == 'bQ':
                self.bQ_captured = True

    def piece_notation(self, move):
        if move.piece_moved != '--' and not self.castle:
            if move.piece_captured == '--':
                sound = 'Sounds/VFX/move-self.wav'
                if move.piece_moved != 'wP' and 'bP':
                    # chess notation
                    self.notation = move.PieceNameToPieces[move.piece_moved] + move. \
                        rank_file(move.startrow, move.startcol) + move.rank_file(move.endrow, move.endcol)
                    # uci notation for chess.board
                    self.uci = move.rank_file(move.startrow, move.startcol) + move.rank_file(move.endrow, move.endcol)
                if move.piece_moved == 'wP' or move.piece_moved == 'bP':
                    self.notation = ColsToFiles[move.startcol] + move.rank_file(move.endrow, move.endcol)
                    self.uci = move.rank_file(move.startrow, move.startcol) + move.rank_file(move.endrow, move.endcol)
                self.b = Board(self.notation, self.uci, sound)

            if move.piece_captured != '--':
                sound = 'Sounds/VFX/capture.wav'
                if move.piece_moved != 'wP' and 'bP':
                    self.notation = move.PieceNameToPieces[move.piece_moved] + \
                                    move.rank_file(move.startrow, move.startcol) + 'x' + \
                                    move.rank_file(move.endrow, move.endcol)
                    self.uci = move.rank_file(move.startrow, move.startcol) + move.rank_file(move.endrow, move.endcol)
                if move.piece_moved == 'wP' or move.piece_moved == 'bP':
                    self.notation = ColsToFiles[move.startcol] + 'x' + move.rank_file(move.endrow, move.endcol)
                    self.uci = move.rank_file(move.startrow, move.startcol) + move.rank_file(move.endrow, move.endcol)
                self.b = Board(self.notation, self.uci, sound)

        if move.piece_moved != '--' and self.run_promote_menu:
            sound = 'Sounds/VFX/promote.wav'
            piece_uci = self.prmt_confirm[1]
            self.uci = self.uci + piece_uci.lower()
            self.notation = self.notation + '=' + piece_uci
            self.b = Board(self.notation, self.uci, sound)
            self.run_promote_menu = False

        if move.piece_moved != '--' and self.castle:
            sound = 'Sounds/VFX/castle.wav'
            if self.castle_piece_check == 'white_kingside':
                self.notation = 'O-O'
                self.uci = 'e1g1'
            if self.castle_piece_check == 'black_kingside':
                self.notation = 'O-O'
                self.uci = 'e8g8'
            if self.castle_piece_check == 'white_queenside':
                self.notation = 'O-O-O'
                self.uci = 'e1c1'
            if self.castle_piece_check == 'black_queenside':
                self.notation = 'O-O-O'
                self.uci = 'e8c8'
            self.castle = False
            self.b = Board(self.notation, self.uci, sound)

        else:
            pass

    def enpassant(self):
        if len(self.moves) >= 3:
            previous_move = self.moves[-2]
            move = self.moves[-1]
            if previous_move.piece_moved == 'bP' and previous_move.startrow == 1 and previous_move.endrow == 3:
                if move.piece_moved == 'wP' and move.startrow == 3 and move.endrow == 2 and \
                        move.endcol == previous_move.endcol and (move.startcol == previous_move.startcol + 1 or
                                                                 move.startcol == previous_move.startcol - 1):
                    self.board[previous_move.endrow][previous_move.endcol] = '--'

            if previous_move.piece_moved == 'wP' and previous_move.startrow == 6 and previous_move.endrow == 4:
                if move.piece_moved == 'bP' and move.startrow == 4 and move.endrow == 5 and \
                        move.endcol == previous_move.endcol and (move.startcol == previous_move.startcol + 1 or
                                                                 move.startcol == previous_move.startcol - 1):
                    self.board[previous_move.endrow][previous_move.endcol] = '--'

    def pawn_promotion(self, move):
        surface = win
        promotion_menu = pygame.Surface((600, 600))
        promotion_menu.fill(black)
        promotion_menu.set_alpha(200)
        surface.blit(promotion_menu, (468, 132))

        prmt_white_queen = Button(surface, 433 + Square_size, 428 - (Square_size // 2), pieces_dict['wQ'], 1)
        prmt_white_rook = Button(surface, 433 + (Square_size * 3), 428 - (Square_size // 2),
                                 pieces_dict['wR'], 1)
        prmt_white_knight = Button(surface, 433 + (Square_size * 5), 428 - (Square_size // 2),
                                   pieces_dict['wN'], 1)
        prmt_white_bishop = Button(surface, 433 + (Square_size * 7), 428 - (Square_size // 2),
                                   pieces_dict['wB'], 1)

        prmt_black_queen = Button(surface, 433 + Square_size, 428 - (Square_size // 2), pieces_dict['bQ'], 1)
        prmt_black_rook = Button(surface, 433 + (Square_size * 3), 428 - (Square_size // 2),
                                 pieces_dict['bR'], 1)
        prmt_black_knight = Button(surface, 433 + (Square_size * 5), 428 - (Square_size // 2),
                                   pieces_dict['bN'], 1)
        prmt_black_bishop = Button(surface, 433 + (Square_size * 7), 428 - (Square_size // 2),
                                   pieces_dict['bB'], 1)
        run = True
        if self.white_turn:
            while run:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.prmt_confirm = 'wQ'
                            self.close_window = True
                            run = False
                        if event.key == pygame.K_z:
                            run = False
                            return True
                # 468, 132
                white_queen_button = Button.draw(prmt_white_queen)
                white_rook_button = Button.draw(prmt_white_rook)
                white_knight_button = Button.draw(prmt_white_knight)
                white_bishop_button = Button.draw(prmt_white_bishop)
                if white_queen_button:
                    self.prmt_confirm = 'wQ'
                    run = False
                if white_rook_button:
                    self.prmt_confirm = 'wR'
                    run = False
                if white_knight_button:
                    self.prmt_confirm = 'wN'
                    run = False
                if white_bishop_button:
                    self.prmt_confirm = 'wB'
                    run = False
                clock.tick(FPS)
                pygame.display.update()

        else:
            while run:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.prmt_confirm = 'bQ'
                            self.close_window = True
                            run = False
                        if event.key == pygame.K_z:
                            run = False
                            return True

                black_queen_button = Button.draw(prmt_black_queen)
                black_rook_button = Button.draw(prmt_black_rook)
                black_knight_button = Button.draw(prmt_black_knight)
                black_bishop_button = Button.draw(prmt_black_bishop)
                if black_queen_button:
                    self.prmt_confirm = 'bQ'
                    run = False
                if black_rook_button:
                    self.prmt_confirm = 'bR'
                    run = False
                if black_knight_button:
                    self.prmt_confirm = 'bN'
                    run = False
                if black_bishop_button:
                    self.prmt_confirm = 'bB'
                    run = False
                clock.tick(FPS)
                pygame.display.update()

        if self.prmt_confirm != '__' and self.board[move.startrow][move.startcol] != '--':
            self.board[move.startrow][move.startcol] = '--'
            self.board[move.endrow][move.endcol] = self.prmt_confirm
            self.s.sound_play('Sounds/VFX/promote.wav')
            self.piece_notation(move)
            self.moves.append(move)
            self.white_turn = not self.white_turn
            return False

        clock.tick(FPS)
        pygame.display.update()

    def castling(self, move):
        for i in self.legal:
            if self.board[7][5] == '--' and self.board[7][6] == '--' and str(i) == 'e1g1':
                self.castle_white_kingside = True
            if self.board[7][1] == '--' and self.board[7][2] == '--' and self.board[7][3] == '--' and str(i) == 'e1c1':
                self.castle_white_queenside = True
            if self.board[0][5] == '--' and self.board[0][6] == '--' and str(i) == 'e8g8':
                self.castle_black_kingside = True
            if self.board[0][1] == '--' and self.board[0][2] == '--' and self.board[0][3] == '--' and str(i) == 'e8c8':
                self.castle_black_queenside = True
        self.castle = False
        self.castle_piece_check = ''
        if self.castle_white_kingside and move.piece_moved == 'wK' and move.endcol == 6:
            self.board[7][6] = 'wK'
            self.board[7][5] = 'wR'
            self.board[7][7] = '--'
            self.castle_white_kingside = False
            self.castle_piece_check = 'white_kingside'
            self.castle = True
            self.moves_castle.append(self.castle_piece_check)

        if self.castle_white_queenside and move.piece_moved == 'wK' and move.endcol == 2:
            self.board[7][2] = 'wK'
            self.board[7][3] = 'wR'
            self.board[7][0] = '--'
            self.castle_white_queenside = False
            self.castle_piece_check = 'white_queenside'
            self.castle = True
            self.moves_castle.append(self.castle_piece_check)

        if self.castle_black_kingside and move.piece_moved == 'bK' and move.endcol == 6:
            self.board[0][6] = 'bK'
            self.board[0][5] = 'bR'
            self.board[0][7] = '--'
            self.castle_black_kingside = False
            self.castle_piece_check = 'black_kingside'
            self.castle = True
            self.moves_castle.append(self.castle_piece_check)

        if self.castle_black_queenside and move.piece_moved == 'bK' and move.endcol == 2:
            self.board[0][2] = 'bK'
            self.board[0][3] = 'bR'
            self.board[0][0] = '--'
            self.castle_black_queenside = False
            self.castle_piece_check = 'black_queenside'
            self.castle = True
            self.moves_castle.append(self.castle_piece_check)

        if move.piece_moved == 'wK':
            self.castle_white_queenside = False
            self.castle_white_kingside = False

        if move.piece_moved == 'bK':
            self.castle_black_queenside = False
            self.castle_black_kingside = False

        if move.piece_moved == 'wR' and move.startcol == 7:
            self.castle_white_kingside = False

        if move.piece_moved == 'wR' and move.startcol == 0:
            self.castle_white_queenside = False

        if move.piece_moved == 'bR' and move.startcol == 7:
            self.castle_black_kingside = False

        if move.piece_moved == 'bR' and move.startcol == 0:
            self.castle_black_queenside = False

    def undo_move(self):  # reverses the last move
        # print('undo')
        if Undo:  # checks is undo is allowed by the player, not implemented yet
            if len(self.moves) > 0 and len(board.move_stack) > 0:
                self.undo_enpassant()
                move = self.moves.pop()
                self.board[move.startrow][move.startcol] = move.piece_moved
                self.board[move.endrow][move.endcol] = move.piece_captured
                self.white_turn = not self.white_turn
                self.b.undo()
                if self.castle_piece_check != '':
                    self.undo_castling()

    def undo_castling(self):
        if len(self.moves_castle) >= 1:
            self.moves_castle.pop(-1)
        if self.castle_piece_check == 'white_kingside':
            self.castle_white_kingside = True
            self.board[7][5] = '--'
            self.board[7][7] = 'wR'
        if self.castle_piece_check == 'white_queenside':
            self.castle_white_queenside = True
            self.board[7][3] = '--'
            self.board[7][0] = 'wR'
        if self.castle_piece_check == 'black_kingside':
            self.castle_black_kingside = True
            self.board[0][5] = '--'
            self.board[0][7] = 'bR'
        if self.castle_piece_check == 'black_queenside':
            self.castle_black_queenside = True
            self.board[0][3] = '--'
            self.board[0][0] = 'bR'
        else:
            pass
        if len(self.moves_castle) >= 1:
            self.castle_piece_check = self.moves_castle[-1]

    def undo_enpassant(self):
        if len(self.moves) >= 3:
            previous_move = self.moves[-2]
            move = self.moves[-1]
            if previous_move.piece_moved == 'bP' and previous_move.startrow == 1 and previous_move.endrow == 3:
                if move.piece_moved == 'wP' and move.startrow == 3 and move.endrow == 2 and \
                        (move.startcol == previous_move.startcol + 1 or move.startcol == previous_move.startcol - 1):
                    self.board[previous_move.endrow][previous_move.endcol] = 'bP'

            if previous_move.piece_moved == 'wP' and previous_move.startrow == 6 and previous_move.endrow == 4:
                if move.piece_moved == 'bP' and move.startrow == 4 and move.endrow == 5 and \
                        (move.startcol == previous_move.startcol + 1 or move.startcol == previous_move.startcol - 1):
                    self.board[previous_move.endrow][previous_move.endcol] = 'wP'

    def reset(self):
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]
        self.invert_board = self.board[::-1]
        board.reset()
        self.white_turn = True
        self.moves = []
        self.castle_white_kingside = False
        self.castle_white_queenside = False
        self.castle_black_kingside = False
        self.castle_black_queenside = False
        self.moves_castle = []
        self.legal = board.legal_moves
        self.close_window = False
        self.run_promote_menu = False
        self.prmt_confirm = '__'


class MoveList:
    pieces = ['wP', 'wR', 'wB', 'wN', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    PieceNameToPieces = {}

    for k in pieces:
        v = k[1]
        PieceNameToPieces[k] = v

    def __init__(self, startsq, endsq, boardstate, is_engine=False, engine_pmrt='--'):
        self.startrow = startsq[0]
        self.startcol = startsq[1]
        self.endrow = endsq[0]
        self.endcol = endsq[1]
        self.piece_moved = boardstate[self.startrow][self.startcol]
        self.piece_captured = boardstate[self.endrow][self.endcol]
        self.is_engine = is_engine
        self.engine_prmt = engine_pmrt

    def rank_file(self, r, c):
        return ColsToFiles[c] + RowsToRanks[r]


class GameWindow:
    def __init__(self, engine_mode, player_mode=True, depth=12):
        self.gs = GameState()
        self.m = MoveList
        self.square_selected = ()
        self.s = Sounds()
        self.surface = win

        self.undo_button = Button(self.surface, 1200, 550, undo_button_img, 1)
        self.reset_button = Button(self.surface, 1200, 350, reset_button_img, 1)
        self.back_button = Button(self.surface, 1200, 150, back_button_img, 1)

        self.undo_bg = pygame.Surface((251, 133))
        self.undo_bg.fill(background_colour[colour_mode])
        self.back_bg = pygame.Surface((251, 133))
        self.back_bg.fill(background_colour[colour_mode])
        self.reset_bg = pygame.Surface((251, 133))
        self.reset_bg.fill(background_colour[colour_mode])

        self.clk = False
        self.clicks = []
        self.prmt_pieces = ['q', 'r', 'b', 'n']
        self.engine_mode = engine_mode  # True: Single player, False: Multi player
        self.run = True
        self.depth = depth  # default value at 12
        self.player = player_mode  # True = white, False = black, default white
        self.game_loop()

    def game_loop(self):
        self.s.music_play('Sounds/Music/idle bg music.ogg', -1)
        self.s.sound_play('Sounds/VFX/game-start.wav')
        self.surface.blit(pygame.transform.scale(game_bg, screen_size), (0, 0))
        self.surface.blit(self.undo_bg, (1200, 550))
        self.surface.blit(self.reset_bg, (1200, 350))
        self.surface.blit(self.back_bg, (1200, 150))
        is_exit = False

        draw(board_surface, self.gs, self.square_selected)
        pygame.display.update()

        self.run = True

        while self.run:
            is_undo_button = Button.draw(self.undo_button)
            is_reset_button = Button.draw(self.reset_button)
            is_back_button = Button.draw(self.back_button)
            win.blit(board_surface, (468, 132))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.s.stop_music()
                    self.run = False
                # Key ui
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.s.stop_music()
                        self.gs.reset()
                        self.run = False
                        is_exit = True
                        MainMenu()

                    if event.key == pygame.K_r:
                        self.gs.reset()
                    if event.key == pygame.K_z:
                        self.gs.undo_move()
                        if self.engine_mode:
                            self.gs.undo_move()

                # Mouse ui
                if event.type == pygame.MOUSEBUTTONDOWN:  # checking for clicks
                    if self.engine_mode and self.gs.white_turn == self.player:
                        self.user_move()
                    else:
                        self.user_move()

            if self.clk:
                self.clk = False
                continue

            if is_undo_button:
                is_undo_button = False
                self.gs.undo_move()
                if self.engine_mode:
                    self.gs.undo_move()

            if is_reset_button:
                self.s.rewind_music()
                self.gs.reset()

            if is_back_button:
                self.s.stop_music()
                self.gs.reset()
                self.run = False
                MainMenu()
                break

            draw(board_surface, self.gs, self.square_selected)
            clock.tick(FPS)
            pygame.display.update()

            if board.is_game_over():
                self.s.stop_music()
                self.s.sound_play('Sounds/VFX/game-end.wav')
                self.run = False
                is_exit = True
                self.end_screen()
                mixer.music.stop()

            if self.gs.run_promote_menu:
                self.run = False
                undo_confirm = self.gs.pawn_promotion(self.move)
                if undo_confirm:
                    self.gs.undo_move()
                self.run = True

            if not self.gs.run_promote_menu:
                if self.engine_mode and self.player != self.gs.white_turn and not is_exit:
                    self.engine_init()

    def user_move(self):
        if player:
            location = (pygame.mouse.get_pos()[0] - 468, pygame.mouse.get_pos()[1] - 132)
        else:
            location = (pygame.mouse.get_pos()[0] - 468, 600 - (pygame.mouse.get_pos()[1] - 132))
        if 600 >= location[0] >= 0 and 600 >= location[1] >= 0:
            column = location[0] // Square_size
            row = location[1] // Square_size
            # checking for repeat clicks
            if self.square_selected == (row, column):
                self.square_selected = ()
                self.clicks = []  # if click is repeat, clear previous click
            else:
                # Player selects a square
                self.square_selected = (row, column)
                self.clicks.append(self.square_selected)

            if len(self.clicks) == 2:
                # second click moves the piece
                self.move = self.m(self.clicks[0], self.clicks[1], self.gs.board, False)
                self.gs.move(self.move)
                self.square_selected = ()
                self.clicks = []
                self.clk = True
                if self.gs.close_window:
                    self.run = False

        draw(board_surface, self.gs, self.square_selected)
        clock.tick(FPS)
        pygame.display.update()

    def end_screen(self):
        surface = win
        end_menu = pygame.Surface((420, 420))
        end_menu.fill(black)
        rect = end_menu.get_rect(topleft=(558, 222))
        win.blit(end_menu, (558, 222))
        main_txt = font_100.render('ChessPy', True, white)
        surface.blit(main_txt, (630, 242))

        play_again_txt = font_50.render('Play Again', True, white)
        quit_txt = font_50.render('Quit', True, white)
        main_menu_txt = font_50.render('Main Menu', True, white)
        chk_mate_txt_txt = font_50.render('checkmate', True, white)
        winner_txt = font_50.render(('Black ' if self.gs.white_turn else 'White ') + 'won by', True, white)
        draw_txt = font_50.render('Draw by', True, white)
        stalemate_txt = font_50.render('stalemate', True, white)

        play_again_button = Button(surface, 679, 450, play_again_txt, 1)
        main_menu_button = Button(surface, 676, 500, main_menu_txt, 1)
        quit_button = Button(surface, 734, 550, quit_txt, 1)
        run = True

        while run:
            if board.is_checkmate():
                surface.blit(winner_txt, (655, 350))
                surface.blit(chk_mate_txt_txt, (680, 380))
            if board.is_stalemate():
                surface.blit(draw_txt, (680, 350))
                surface.blit(stalemate_txt, (680, 380))

            is_play_again = Button.draw(play_again_button)
            is_main_menu = Button.draw(main_menu_button)
            is_quit = Button.draw(quit_button)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False

            if is_play_again:
                self.gs.reset()
                run = False
                if self.engine_mode and self.player:
                    GameWindow(True, True, self.depth)

                if self.engine_mode and not self.player:
                    GameWindow(True, False, self.depth)

                else:
                    GameWindow(False)

            if is_main_menu:
                self.gs.reset()
                run = False
                MainMenu()

            if is_quit:
                run = False
            clock.tick(FPS)
            pygame.display.update()

    def engine_make_move(self, depth):
        chess_engine = engine.SimpleEngine.popen_uci(
            "engine/stockfish_14.1_win_x64_popcnt/stockfish_14.1_win_x64_popcnt.exe")

        result = chess_engine.play(board, engine.Limit(depth=depth))
        engine_move = str(result.move)
        b = self.engine_notation(engine_move)
        board.push(result.move)
        # print(result.move)
        # print(board)
        # print(board.legal_moves)
        chess_engine.quit()
        return b

    def engine_notation(self, engine_move):
        startrow, startcol = (RanksToRows[engine_move[1]], FilesToCols[engine_move[0]])
        start_sq = (startrow, startcol)
        endrow, endcol = (RanksToRows[engine_move[3]], FilesToCols[engine_move[2]])
        end_sq = (endrow, endcol)
        if engine_move[-1] in self.prmt_pieces:
            prmt_piece = ('b' if self.player else 'w') + engine_move[-1].upper()
            move = MoveList(start_sq, end_sq, self.gs.board, True, prmt_piece)
        else:
            move = MoveList(start_sq, end_sq, self.gs.board, True)
        self.gs.move(move)
        if player:
            return self.gs.board
        else:
            return self.gs.invert_board

    def engine_init(self):
        if self.player and not self.gs.white_turn:
            b = self.engine_make_move(self.depth)
            self.gs.white_turn = True
            self.draw_engine_move(b)
        if not self.player and self.gs.white_turn:
            b = self.engine_make_move(self.depth)
            self.gs.white_turn = False
            self.draw_engine_move(b)

    def draw_engine_move(self, board_after_engine):
        draw_board(board_surface)
        draw_pieces(board_surface, board_after_engine)
        clock.tick(FPS)
        pygame.display.update()


def highlight(square_selected, game_state, surface):
    if square_selected != ():
        r, c = square_selected
        s = pygame.Surface((Square_size, Square_size))
        s.set_alpha(200)
        s.fill((243, 204, 16))
        if player:
            surface.blit(s, (c * Square_size, r * Square_size))
        else:
            surface.blit(s, (c * Square_size, 600 - ((r + 1) * Square_size)))
        row, col = RowsToRanks.get(square_selected[0]), ColsToFiles.get(square_selected[1])
        if game_state.board[r][c][0] == ('w' if game_state.white_turn else 'b'):
            s.fill((31, 1, 120))
            for i in board.legal_moves:
                legal_col, legal_row = FilesToCols.get(str(i)[2]), RanksToRows.get(str(i)[3])
                if str(i)[0] == col and str(i)[1] == row:
                    if player:
                        surface.blit(s, (legal_col * Square_size, legal_row * Square_size))
                    else:
                        surface.blit(s, (legal_col * Square_size, 600 - ((legal_row + 1) * Square_size)))


def draw(display, gs, square_selected):
    draw_board(display)
    highlight(square_selected, gs, display)
    if player:
        draw_pieces(display, gs.board)
    else:
        draw_pieces(display, gs.invert_board)
    clock.tick(FPS)
    pygame.display.update()


def draw_board(display):
    colours = [light_colours[colour_mode], dark_colours[colour_mode]]
    inverted_colours = [dark_colours[colour_mode], light_colours[colour_mode]]
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    ranks = ['1', '2', '3', '4', '5', '6', '7', '8']
    files_invert = files[::-1]
    ranks_invert = ranks[::-1]
    for row in range(8):
        for column in range(8):
            file = font_30.render(files[column] if player else files_invert[column], True, colours[(column % 2)])
            colour = colours[(row + column) % 2]
            pygame.draw.rect(display, colour, pygame.Rect(column * Square_size, row * Square_size, Square_size,
                                                          Square_size))
            display.blit(file, ((column * Square_size) + (Square_size - 15), 575))
        rank = font_30.render(ranks_invert[row] if player else ranks_invert[row], True, inverted_colours[(row % 2)])
        display.blit(rank, (5, row * Square_size))


def draw_pieces(display, board_draw):
    for row in range(8):
        for column in range(8):
            piece = board_draw[row][column]
            if piece != '--':
                # not an empty square
                display.blit(pieces_dict[piece], pygame.Rect((column * Square_size, row * Square_size, Square_size,
                                                              Square_size)))


load()
MainMenu()
