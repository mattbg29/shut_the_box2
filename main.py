import random


def create_dict_states():
    """
    create a dictionary with every possible box state (represented as a string of
    0s and 1s) and every possible roll as the keys and the values and optimal action
    as values
    :return: dict state
    """
    dict_state = {}

    for i in range(512):
        for j in range(2, 13):
            dict_state[int_to_bin(i), j] = {'V_last': 0, 'V_cur': 0, 'action': []}

    return dict_state


def update_dict_state(dict_state, gamma):
    roll_options = {
        2: [[2]],
        3: [[2,1], [3]],
        4: [[3,1], [4]],
        5: [[4,1], [3,2], [5]],
        6: [[4,2], [5,1], [6]],
        7: [[4,3], [5,2], [6,1], [7]],
        8: [[5,3], [6,2], [7,1], [8]],
        9: [[5,4], [6,3], [7,2], [8,1], [9]],
        10: [[6,4], [7,3], [8,2], [9,1]],
        11: [[6,5], [7,4], [8,3], [9,2]],
        12: [[7,5], [8,4], [9,3]]
    }

    roll_odds = {
        2: 1/36,
        3: 2/36,
        4: 3/36,
        5: 4/36,
        6: 5/36,
        7: 6/36,
        8: 5/36,
        9: 4/36,
        10: 3/36,
        11: 2/36,
        12: 1/36
    }

    # for every combination of box state and roll
    for box, roll in dict_state.keys():

        # options is the possible actions given the roll
        options = roll_options[roll]

        optimal_q = float("-inf")
        optimal_action = []

        # for each possible action
        for cur_option in options:
            cur_box = box
            found_action = True
            # for each number in the box to put down for this option
            for number in cur_option:
                box_idx = number - 1

                # if the number is not yet put down, put it down
                new_box = ''
                for i in range(len(cur_box)):
                    if i == box_idx:
                        if cur_box[i] == '0':
                            new_box += '1'
                        # if there is a number we cannot put down, then this action fails;
                        # break out of this and try another action
                        else:
                            found_action = False
                            break
                    else:
                        new_box += cur_box[i]
                cur_box = new_box

            # if we found an action that works
            if found_action:
                # if there is an action that reaches the optimal state, we assign a reward of
                # +1 and assign this action to the state
                if cur_box == '111111111':
                    dict_state[box, roll]['V_cur'] = 1
                    dict_state[box, roll]['action'] = optimal_action
                    optimal_q = float('inf')

                # otherwise, assign a reward of 0 and update the box state to reflect the
                # percent odds of future states from this state, as determined by the
                # odds of future rolls and what states that leads to; we keep track of the
                # best q_value throughout this process
                else:
                    roll_now = 2
                    q_value_now = 0
                    for key, odds in roll_odds.items():
                        q_value_now += odds*dict_state.get((cur_box, roll_now))['V_last']
                        roll_now += 1
                    q_value_now *= gamma
                    if q_value_now > optimal_q:
                        optimal_q = q_value_now
                        optimal_action = cur_option

        # if we never updated optimal_q, then we must have lost the game
        if optimal_q == float('-inf'):
            dict_state[box, roll]['V_cur'] = -1
            dict_state[box, roll]['action'] = []
        elif optimal_q < float('inf'):
            dict_state[box, roll]['V_cur'] = optimal_q
            dict_state[box, roll]['action'] = optimal_action

    return dict_state


def int_to_bin(integer):
    binary = bin(integer)[2:]
    zeroes_to_add = 9 - len(binary)
    zeroes = ''
    for i in range(zeroes_to_add):
        zeroes += '0'
    return zeroes + binary


def value_iteration_stb():
    epsilon = 8e-102

    dict_state = create_dict_states()

    while True:

        dict_state = update_dict_state(dict_state, 0.8)

        max_error = 0
        for key, item in dict_state.items():
            error_now = abs(item.get('V_cur') - item.get('V_last'))
            if error_now > max_error:
                max_error = error_now
        #print(max_error)
        print(count_odds(dict_state))
        if max_error < epsilon:
            return dict_state

        # update our state dictionary by setting 'V_last' equal to V_cur and proceed to the next iteration
        for key, value in dict_state.items():
            value['V_last'] = value['V_cur']


def play_stb():
    dict_state = value_iteration_stb()

    restart = 1

    while restart == 1:
        box = '000000000'

        while True:
            roll1 = random.randint(1, 6)
            roll2 = random.randint(1, 6)
            roll_total = roll1 + roll2
            optimal_action = dict_state.get((box, roll_total))['action']
            q_value = dict_state.get((box, roll_total))['V_last']
            print(box, roll_total)
            if q_value == 1:
                restart = int(input('You win. Restart?'))
                break
            elif not optimal_action:
                print(box, roll_total)
                print('You lose.')
                break
            else:
                print('Optimal action: ' + str(optimal_action))
                for number in optimal_action:
                    box_idx = number - 1
                    new_box = ''
                    for i in range(len(box)):
                        if i == box_idx:
                            new_box += '1'
                        else:
                            new_box += box[i]
                    box = new_box


def count_odds(dict_state):

    wins = 0
    plays = 0

    while plays < 100000:
        box = '000000000'

        while True:
            roll1 = random.randint(1, 6)
            roll2 = random.randint(1, 6)
            roll_total = roll1 + roll2
            optimal_action = dict_state.get((box, roll_total))['action']
            q_value = dict_state.get((box, roll_total))['V_last']
            if q_value == 1:
                plays += 1
                wins += 1
                break
            elif not optimal_action:
                plays += 1
                break
            else:
                for number in optimal_action:
                    box_idx = number - 1
                    new_box = ''
                    for i in range(len(box)):
                        if i == box_idx:
                            new_box += '1'
                        else:
                            new_box += box[i]
                    box = new_box
    return wins / plays


def optimal_play():
    roll_options = {
        2: [[2]],
        3: [[2,1], [3]],
        4: [[3,1], [4]],
        5: [[3,2], [4,1], [5]],
        6: [[4,2], [5,1], [6]],
        7: [[4,3], [5,2], [6,1], [7]],
        8: [[5,3], [6,2], [7,1], [8]],
        9: [[5,4], [6,3], [7,2], [8,1], [9]],
        10: [[6,4], [7,3], [8,2], [9,1]],
        11: [[6,5], [7,4], [8,3], [9,2]],
        12: [[7,5], [8,4], [9,3]]
    }

    wins = 0
    plays = 0
    while plays < 100000:
        box = '000000000'

        while True:
            if box == '111111111':
                wins += 1
                plays += 1
                break
            roll1 = random.randint(1, 6)
            roll2 = random.randint(1, 6)
            roll_total = roll1 + roll2

            actions = roll_options[roll_total]
            lost = False
            for action in reversed(actions):
                lost = False
                cur_box = box
                for number in action:
                    if not lost:
                        box_idx = number - 1
                        new_box = ''
                        for i in range(len(cur_box)):
                            if i == box_idx and cur_box[i] == '0':
                                new_box += '1'
                            elif i == box_idx:
                                lost = True
                            else:
                                new_box += cur_box[i]
                        if not lost:
                            cur_box = new_box
                if not lost:
                    break
            if lost:
                plays += 1
                break
            box = cur_box
    return wins / plays


def optimal_vs_value():
    roll_options = {
        2: [[2]],
        3: [[2,1], [3]],
        4: [[3,1], [4]],
        5: [[3,2], [4,1], [5]],
        6: [[4,2], [5,1], [6]],
        7: [[4,3], [5,2], [6,1], [7]],
        8: [[5,3], [6,2], [7,1], [8]],
        9: [[5,4], [6,3], [7,2], [8,1], [9]],
        10: [[6,4], [7,3], [8,2], [9,1]],
        11: [[6,5], [7,4], [8,3], [9,2]],
        12: [[7,5], [8,4], [9,3]]
    }

    dict_state = value_iteration_stb()

    agree = 0
    disagree = 0

    for box, roll in dict_state.keys():
        optimal_action = dict_state.get((box, roll))['action']

        if optimal_action:
            actions = roll_options[roll]
            chosen_action = []
            for action in reversed(actions):
                chosen_action = action
                lost = False
                cur_box = box
                for number in action:
                    if not lost:
                        box_idx = number - 1
                        new_box = ''
                        for i in range(len(cur_box)):
                            if i == box_idx and cur_box[i] == '0':
                                new_box += '1'
                            elif i == box_idx:
                                lost = True
                            else:
                                new_box += cur_box[i]
                        if not lost:
                            cur_box = new_box
                if not lost:
                    break
            if optimal_action != chosen_action:
                print(box, roll, optimal_action, chosen_action, sep="|")
                disagree += 1
            else:
                agree += 1

    print(agree, disagree)


print('Percentage win by always picking the largest value:')
print(optimal_play())

print('Percentage win with each iteration of Value Iteration, followed by the differences between the two policies:')
optimal_vs_value()
