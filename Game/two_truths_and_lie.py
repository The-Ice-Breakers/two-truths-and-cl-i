import random
import time
import asyncio

class Player:
    """
    Class for player instances
      Stores:
        - websocket player is connected through
        - player name
        
      Tracks:
        - 2T&L statements for each round of the game
        - current game store
    """
    def __init__(self, name:str="Player", websocket=None):
        self.selection = None
        self.name = name
        self.score = 0
        self.websocket = websocket
        self.statements={}
    def __str__(self):
        return f"Player: {self.name}\nScore:{self.score}"

class Game:
    def __init__(self):
        self.queue = []
        self.players = []
        self.playersGone=[]

    async def addPlayer(self, websocket, broadcast):
        await websocket.send_text("What is your name?")
        name = await websocket.receive_text()
        player = Player(name, websocket)
        self.players.append(player)

        await self.play(broadcast)
        print(player) 
        
        print(f"Current players: {self.players}")

    def newRound(self):
        self.playersGone = []
        self.players = self.players + self.queue

    async def askStatement(self):
        
        for player in self.players:
            await player.websocket.send_text("Enter 2 true facts and 1 lie")
            player.statements= {}
            for _ in range(0, 1):
                await player.websocket.send_text("Enter a truth:")
                truth = await player.websocket.receive_text()
                player.statements[truth] = True
            # await player.websocket.send_text("Enter a lie:")
            # false = await player.websocket.receive_text()
            # player.statements[false] = False


    # def checkAnswer(self, statements, player, answer):
    #     if statements[answer] == False:
    #         print(player.name + " ✓")
    #     else: 
    #         print(player.name + " X")

    def removePlayer(self, websocket):
        for player in self.players:
            if player.websocket == websocket:
                self.players.remove(player)
        print(f"Current players: {self.players}")
    
    async def play(self, broadcast):
        while 2 <= len(self.players):
            self.newRound()
            await self.askStatement()
            # while len(self.playersGone) != len(self.players):
            #     choices = [x for x in self.players if x not in self.playersGone]
            #     asking = random.choice(choices)
            #     self.playersGone.append(asking)
            #     print(asking.statements)
            #     statementsDict = asking.statements
            #     statements = list(statementsDict.keys())
            #     random.shuffle(statements)

            #     for player in self.players:
            #         if player != asking:
            #             print("1. " + statements[0])
            #             print("2. " + statements[1])
            #             print("3. " + statements[2])
            #             print(player.name + f" guess {asking.name}'s lie by inputing the corresponding number:")
            #             answer = input("> ")
            #             self.checkAnswer(statementsDict, player, statements[int(answer)-1])
            # t = 60
            # print(f"Next round starting in {t} seconds")
            # while t:
            #     mins, secs = divmod(t, 60)
            #     timer = '{:02d}:{:02d}'.format(mins, secs)
            #     print(timer, end="\r")
            #     time.sleep(1)
            #     t -= 1
            # print("New Round Starting...")
            # self.play()
        


    


if __name__ == '__main__':
    game = Game()
    game.addPlayer()
    game.addPlayer()
    game.play()