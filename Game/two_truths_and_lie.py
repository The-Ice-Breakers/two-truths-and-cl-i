import random
import time

class Player:
    def __init__(self, name="Player", websocket=None):
        self.selection = None
        self.name = name
        self.websocket = websocket
        self.statements={}

class Game:
    def __init__(self):
        self.queue = []
        self.players = []
        self.playersGone=[]

    def addPlayer(self, websocket, name):
        player = Player(name, websocket)
        self.players.append(player)
        self.play()
        return player

    def newRound(self):
        self.playersGone = []
        self.players = self.players + self.queue

    def askStatement(self):
        for player in self.players:
            player.statements= {}
            print("Enter 2 true facts and 1 lie")
            for _ in range(0, 2):
                truth = input("Truth: ")
                player.statements[truth] = True
            false = input("False: ")
            player.statements[false] = False



    def checkAnswer(self, statements, player, answer):
        if statements[answer] == False:
            print(player.name + " ✓")
        else: 
            print(player.name + " X")

    def removePlayerByWebSocket(self, websocket):
        for player in self.players:
            if player.websocket == websocket:
                self.players.remove(player)
    
    def play(self):
        if len(self.players) < 2:
            self.newRound()
            self.askStatement()
            while len(self.playersGone) != len(self.players):
                choices = [x for x in self.players if x not in self.playersGone]
                asking = random.choice(choices)
                self.playersGone.append(asking)
                print(asking.statements)
                statementsDict = asking.statements
                statements = list(statementsDict.keys())
                random.shuffle(statements)

                for player in self.players:
                    if player != asking:
                        print("1. " + statements[0])
                        print("2. " + statements[1])
                        print("3. " + statements[2])
                        print(player.name + f" guess {asking.name}'s lie by inputing the corresponding number:")
                        answer = input("> ")
                        self.checkAnswer(statementsDict, player, statements[int(answer)-1])
            t = 60
            print(f"Next round starting in {t} seconds")
            while t:
                mins, secs = divmod(t, 60)
                timer = '{:02d}:{:02d}'.format(mins, secs)
                print(timer, end="\r")
                time.sleep(1)
                t -= 1
            print("New Round Starting...")
            self.play()
        else:
            self.play()


if __name__ == '__main__':
    game = Game()
    game.addPlayer()
    game.addPlayer()
    game.play()