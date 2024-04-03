
class Player:
    VERSION = "Default Python folding player (special version)"

    def betRequest(self, game_state):
        my_index = game_state["in_action"]
        my_player = game_state["players"][my_index]
        my_stack = my_player["stack"]

        return my_stack

    def showdown(self, game_state):
        pass

