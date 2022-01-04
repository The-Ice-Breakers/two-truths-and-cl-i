import re
from collections import Counter
import random

class Parser:
    def __init__(self):
        self.played = Counter()
        self.MAX_INPUTS = 3
        
    
    async def check_has_played_old(self,string, websocket, client_id) -> str:
        """
        Input:
        - string
        - websocket
        - client_id \n
        Output:
        - returns string if player has not sent in max number of inputs yet
        - returns empty string if player has already given their inputs
        """
        if self.played[client_id] >= self.MAX_INPUTS:
            await websocket.send_text('Wait Your Turn')
            return ""
        else:
            self.played.update((client_id,))
            return f'#{client_id}:{string}{self.played[client_id]}>'

    def check_has_played(self,max_inputs:int,client_id:str) -> bool:
        if self.played[client_id] >= max_inputs:
            return False
        else:
            return True

    async def gather_inputs(self,string,websocket,client_id):
        if not self.check_has_played(client_id):
            await websocket.send_text('Wait Your Turn!')
            return ''
        else:
            self.played.update((client_id,))
            return f'#{client_id}:{string}{self.played[client_id]}>'



    def get_client_inputs(self,mega_string):
        """
        Inputs:
        - Giant string containing all inputs
        Output:
        - List containing Lists of strings grouped by user in the order those strings were submitted
        """
        grouped_inputs = []
        for player in self.played:
            player_grouped_inputs = re.match(f'#{player}:\\w*>')
            assert len(player_grouped_inputs) == 3
            player_grouped_inputs[0] = {player_grouped_inputs[0]:True}
            player_grouped_inputs[1] = {player_grouped_inputs[1]:True}
            player_grouped_inputs[2] = {player_grouped_inputs[2]:False}
            random.shuffle(player_grouped_inputs)
            grouped_inputs.append(player_grouped_inputs)
        return grouped_inputs



    @staticmethod
    async def help(websocket):
        await websocket.send_text("""
Commands:
? Help
! Guess
> Next
$ Show scores
2 Send text to everyone
@ Change truths and lie
Use this format: (truth, truth, lie)
""")


    @staticmethod
    async def changeTL(websocket, string, client_id):
        pattern = r"[^,\s][^\,]*[^,\s]*"
        truths_and_lie = re.findall(pattern, string)
        if len(truths_and_lie) == 3:
            truths_lie_client = {truths_and_lie[0]:True, truths_and_lie[1]:True, truths_and_lie[2]:False, "user": client_id}
            await websocket.send_text("Your statements have been updated and added to the queue.")
            return truths_lie_client
        else:
            await websocket.send_text("Invalid format: (truth, truth, lie)")



class RoundManager():
    def __init__(self,MAX_INPUTS):
        self.input_counter = Counter()
        self.MAX_INPUTS = MAX_INPUTS

    def check_has_finished(self, client_id:str) -> bool:
        if self.input_counter[client_id] >= self.MAX_INPUTS:
            return False
        else:
            return True

    def update_input_count(self, client_id:str) -> None:
        self.input_counter.update((client_id,))

    def reset_input_count(self):
        self.input_counter.clear()