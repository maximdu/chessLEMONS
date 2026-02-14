from compression.zstd import ZstdFile

def get_next_game(file: ZstdFile):
    game = []
    while True:
        if line := file.readline().decode().strip():
            game.append(line)
        if line.startswith('1.'):
            return game

def is_include_game(game):
    movetext = game[-1]
    with_eval = '%eval' in movetext
    with_clk = '%clk' in movetext
    with_elo = any(tag.startswith('[WhiteElo') for tag in game) and any(tag.startswith('[BlackElo') for tag in game)
    return with_eval and with_clk and with_elo

def get_next_game_with_eval(file):
    while True:
        if is_include_game(game := get_next_game(file)):
            return game


# ------------------------------------------------------------------

from itertools import pairwise


def get_tag(tag):
    key, _, value = tag.strip('[]').partition(' ')
    value = value.strip('"')
    return key, value

def tags_to_dict(tags):
    tags = [get_tag(i) for i in tags]
    tags = dict(tags)
    return tags

def transform_tags(tags):
    tags['WhiteElo'] = int(tags['WhiteElo'])
    tags['BlackElo'] = int(tags['BlackElo'])
    tags['MeanElo'] = (tags['WhiteElo'] + tags['BlackElo']) / 2
    tags['DiffElo'] = (tags['WhiteElo'] - tags['BlackElo']) / 2
    return tags

def parse_game(game):
    *tags, movetext = game
    tags = tags_to_dict(tags)
    tags = transform_tags(tags)
    tokens = movetext.replace('[', '').replace(']', '').split()
    evals = parse_eval(tokens)
    time = get_seconds(tokens)
    moves = get_only_moves(tokens)
    return tags, {'moves': moves, 'time': time, **evals}

def time_to_seconds(time):
    hours, minutes, seconds = time.split(':')
    hours, minutes, seconds = int(hours), int(minutes), int(seconds)
    time_in_seconds = (hours * 60 * 60) + (minutes * 60) + (seconds * 1)
    return time_in_seconds

def get_seconds(tokens):
    time = get_search(tokens, '%clk')
    time = [time_to_seconds(i) for i in time]
    return time

def parse_eval(tokens):
    evals = get_search(tokens, '%eval')
    evals = [parse_single_eval(i) for i in evals]
    eval_types, eval_values = unpack_pairs(evals)
    return {'eval_types': eval_types, 'eval_values': eval_values}

def get_search(tokens, search_for):
    return [
        next_token
        for token, next_token in pairwise(tokens)
        if token == search_for
    ]

def get_only_moves(tokens):
    return [
        token
        for token, next_token in pairwise(tokens)
        if next_token == '{' and token != '}'
    ]

def unpack_pairs(pairs):
    list_1, list_2 = zip(*pairs)
    list_1, list_2 = list(list_1), list(list_2)
    return list_1, list_2

def parse_single_eval(ev):
    if ev.startswith('#'):
        eval_type = 'mate'
        eval_value =  int(ev.strip('#'))
    else:
        eval_type = 'cp'
        eval_value =  int(float(ev)*100)
    return eval_type, eval_value

# def parse_timecontrol(t):
#     start, _, increment = t.partition('+')
#     start, increment = int(start), int(increment)
#     return start*60, increment


# ------------------------------------------------------------------
# parsing moves

def parse_san_move(move, move_number):
    is_take = 'x' in move
    move = move.replace('x', '').replace('=', '').replace('+', '').replace('#', '').replace('?', '').replace('!', '')

    if move == 'O-O' and (move_number%2==1):
        return ('R', 'f1', '', False)
    if move == 'O-O' and (move_number%2!=1):
        return ('r', 'f8', '', False)
    if move == 'O-O-O' and (move_number%2==1):
        return ('R', 'd1', '', False)
    if move == 'O-O-O' and (move_number%2!=1):
        return ('R', 'd8', '', False)

    if move[0].isupper():
        piece = move[0]
        move = move[1:]
    else:
        piece = 'p'

    piece = piece.upper() if (move_number%2==1) else piece.lower()

    if move[-1].isupper():
        promotion_to = move[-1]
        move = move[:-1]
    else:
        promotion_to = ''
    promotion_to = promotion_to.upper() if (move_number%2==1) else promotion_to.lower()

    move_to = move[-2:]

    return (piece, move_to, promotion_to, is_take)



# ------------------------------------------------------------------

def get_starting_board():
    FILES = 'abcdefgh'
    PIECES = 'rnbqkbnr'
    WHITE_PAWN = 'P'
    BLACK_PAWN = 'p'

    board = {}
    for file, piece in zip(FILES, PIECES):
        board[f'{file}8'] = piece.lower()
        board[f'{file}7'] = BLACK_PAWN
        board[f'{file}2'] = WHITE_PAWN
        board[f'{file}1'] = piece.upper()

    piece_count = {}
    for piece in board.values():
        piece_count[piece] = piece_count.get(piece, 0) + 1

    return board, piece_count


def get_material_from_moves(moves):
    moves = [parse_pgn_move(move, move_number) for move_number, move in enumerate(moves, start=1)]
    states = []
    board, piece_count = get_starting_board()
    states.append(dict(piece_count))
    for piece, move_to, promotion_to, is_take in moves:

        if piece == 'P' and move_to[1] == '4' and not is_take:
            board[f'{move_to[0]}3'] = 'P'
        if piece == 'p' and move_to[1] == '5' and not is_take:
            board[f'{move_to[0]}6'] = 'p'

        if is_take:
            piece_taken = board[move_to]
            piece_count[piece_taken] -= 1

        board[move_to] = piece

        if promotion_to:
            board[move_to] = promotion_to
            piece_count[piece] -= 1
            piece_count[promotion_to] += 1

        states.append(dict(piece_count))
    return states
