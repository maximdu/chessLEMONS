import numpy as np

def eval_to_white_win_p(eval_type, eval_int, a=259.54124776, b=17.29404148):
    if eval_type == 'cp':
        return 1 / (1 + np.exp((-eval_int+b)/a))
    elif eval_type == 'mate':
        return int(eval_int > 0)
    else:
        raise Exception(f"Bad eval: {eval_type} {eval_int}")

def win_p_to_one_hot_bin(win_probability, k=10):
    eval_bin = np.digitize(win_probability, bins=np.linspace(0, 1, k+1)) - 1
    one_hot = np.zeros(k+1)
    one_hot[eval_bin] = 1
    return one_hot

def elo_to_one_hot(elo):
    elo_bin = np.digitize(elo, np.linspace(1200, 2200, 6))
    one_hot = np.zeros(6+1)
    one_hot[elo_bin] = 1
    return one_hot

def elo_diff_to_one_hot(diff):
    diff_bin = np.digitize(diff, bins=[-100, -25, 25, 100]) 
    one_hot = np.zeros(5)
    one_hot[diff_bin] = 1
    return one_hot

def move_number_to_one_hot(move_number):
    digit = np.digitize(move_number, [10, 20, 30, 40, 50])
    one_hot = np.zeros(6)
    one_hot[digit] = 1
    return one_hot











    
    