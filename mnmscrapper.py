from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
import urllib.parse
import pickle
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep
import pytz
import re
import sys
import networkx as nx
import matplotlib.pyplot as plt
urlbase="https://www.meneame.net/user/"
limit=8000
zone=pytz.timezone('CET')
nodeList = {}
targetList = list()
adjMatrix = None
pos = {}
betCent = {}
eigenCentral = {}
closenessCentral = {}
degreeCentral = {}
Gfriends = nx.DiGraph()

class userEdge:
    def __init__(self,voter,user):
        self.voter = voter
        self.target = user
        self.heat = 0
        self.value = 0
    def update(self,vote):
        if vote == "green": 
            self.value += 1
        elif vote == "red":
            self.value -= 1
        self.heat = self.heat + 1
    def getHeat(self):
        return self.heat
    def getUser(self):
        return self.target
    def toString(self):
        return self.voter + " " + self.target + " " + str(self.heat) + " " + str(self.value) 

class userNode:
    def __init__(self,username):
        self.user=username
        self.profile = urlbase + username
        self.data = {}
        self.voteComment = {}
        self.voteNote = {}

def loadDefaults():
    global nodeList
    print("Reading and building initial node lists with seed")
    f=open("./lusersclean")
    line = f.readline()
    initGraphUsers = 1
    while (line):
        newLuser=line.strip()
        if newLuser in nodeList:
            print("User " + newLuser + " already exists")
        else:
            myNode=userNode(newLuser)
            nodeList[newLuser]=myNode
            initGraphUsers +=1
        line=f.readline()
    f.close()
    print("Graph initiated with " + str(initGraphUsers) + " users")

def checkProfiles():
    #Encapsulation for bulk getProfile
    global nodeList
    print("Checking profiles and loading metadata")
    for i in nodeList.keys():
        getProfile(i)
        print(nodeList[i].data)
        sleep(2)

def getProfile(user):
    global nodeList
    try:
        print("processing " + user)
        html = urlopen(urlbase+ urllib.parse.quote(user + "/profile"))
    except HTTPError as e:
        print(e)
    except URLError:
        print("Server down or incorrect domain")
    else:
        userdata = {}
        page = BeautifulSoup(html.read(),"html5lib")
        # userstats = page.find(id="container").find_all('div',class_="contents-body")
        table = page.find('table', attrs={'class':'table table-condensed'})
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            fila = row.find_all('th')
            fila = [ele.text.strip() for ele in fila]
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            userdata[fila[0]]=cols[0]
        nodeList[user].data=userdata
        

def do_Backup():
    global nodeList
    global pos
    global betCent
    global degreeCentral
    global closenessCentral
    global eigenCentral
    with open('backup.pk1', 'wb') as output:
        pickle.dump(nodeList,output,pickle.HIGHEST_PROTOCOL)
    with open('pos.pk1', 'wb') as output:
        pickle.dump(pos,output,pickle.HIGHEST_PROTOCOL)
    with open('betweenness.pk1', 'wb') as output:
        pickle.dump(betCent,output,pickle.HIGHEST_PROTOCOL)
    with open('eigencentral.pk1', 'wb') as output:
        pickle.dump(eigenCentral,output,pickle.HIGHEST_PROTOCOL)
    with open('closenesscentral.pk1', 'wb') as output:
        pickle.dump(closenessCentral,output,pickle.HIGHEST_PROTOCOL)
    with open('degreecentral.pk1', 'wb') as output:
        pickle.dump(degreeCentral,output,pickle.HIGHEST_PROTOCOL)

def do_Restore(wtr):
    
    if wtr is 'nodes':
        with open('/home/dcasal/mnm/backup.pk1', 'rb') as input:
            nodeList = pickle.load(input)
            return nodeList
    if wtr is 'pos':
        with open('pos.pk1', 'rb') as input:
            pos = pickle.load(input)
            return pos
    if wtr is 'btw':
        with open('betweenness.pk1', 'rb') as input:
            betCent = pickle.load(input)
            return betCent
    if wtr is 'eigen':
        with open('eigencentral.pk1', 'rb') as input:
            eigenCentral = pickle.load(input)
            return eigenCentral
    if wtr is 'closeness':
        with open('closenesscentral.pk1', 'rb') as input:
            closenessCentral = pickle.load(input)
            return closenessCentral
    if wtr is 'degree':
        with open('degreecentral.pk1', 'rb') as input:
            degreeCentral = pickle.load(input)
            return degreeCentral


def getEdgeVotedComments(user):
    global nodeList
    myUrl = urlbase +  urllib.parse.quote(nodeList[user].user + "/shaken_comments") + "?page="
    limit = 100
    print("Comments voted by "+ user)
    for i in range(1,limit):
        try:
            html = urlopen(myUrl +str(i))
        except HTTPError as e:
            print(e)
        except URLError:
            print("Server down or incorrect domain")
        else:
            page = BeautifulSoup(html.read(),"html5lib")
            votedList = page.find('ol',attrs={'class':'comments-list'})
            if votedList is None:
                print("no more comments to process")
                break
            else:
                listItems = votedList.find_all('li')
                #print(listItems[0])
                try:
                    for j in range(len(listItems)):
                        votedGuy = listItems[j].find('div',class_='comment-header').find('a',class_='username').getText()
                        voteResult= listItems[j].find('div',class_='box')["style"].split(';')[0].split(':')[1].strip()
                        if votedGuy in nodeList[user].voteComment.keys():
                            nodeList[user].voteComment[votedGuy].update(voteResult)
                        else:
                            newEdge = userEdge(user,votedGuy)
                            newEdge.update(voteResult)
                            nodeList[user].voteComment[votedGuy] = newEdge
                except AttributeError:
                    print("object empty for user " + user )
                print("page %s of comments completed." %i)
        sleep(1)

def getEdgeVotedNotes(user):
    global nodeList
    myUrl = urlbase +  urllib.parse.quote(nodeList[user].user + "/notes_votes") + "?page="
    limit = 1000
    print("Notes voted by " + user)
    for i in range(1,limit):
        try:
            html = urlopen(myUrl + str(i))
        except HTTPError as e:
            print(e)
        except URLError:
            print("Server down or incorrect domain")
        except ValueError as e:
            print(e)
        else:
            page = BeautifulSoup(html.read(),"html5lib")
            votedList = page.find('ol',attrs={'class':'comments-list'})
            if votedList is None:
                print("no more notes to process")
                break
            else:
                listItems = votedList.find_all('li')
                #print(listItems[0])
                for j in range(len(listItems)):
                    try:
                        votedGuy = listItems[j].find('div',class_='comment-header').find('a',class_='username').getText()
                        voteResultUp = listItems[j].find('i',class_='fa fa-arrow-circle-up')
                        voteResultDown = listItems[j].find('i',class_='fa fa-arrow-circle-down')
                        voteResult = None
                        if voteResultUp is None:
                            if voteResultDown is None:
                                break
                            else:
                                voteResult = 'red'
                        else:
                            voteResult = 'green'
                        if votedGuy in nodeList[user].voteComment.keys():
                            nodeList[user].voteComment[votedGuy].update(voteResult)
                        else:
                            newEdge = userEdge(user,votedGuy)
                            newEdge.update(voteResult)
                            nodeList[user].voteComment[votedGuy] = newEdge
                    except AttributeError:
                        print("object empty for user " + user )
                        
            print("page %s of notes completed." %i)
                
def dump_edges():
    output1 = "output1.csv"
    f1 = open(output1, 'w')
    f1 = open(output1, 'w')
    f1.write("voter|voted|abs_votes|realvalue\n")
    for i in nodeList.keys():
        for j in nodeList[i].voteComment.keys():
            txttofile=nodeList[i].voteComment[j].voter + "|" + nodeList[i].voteComment[j].target + "|" + str(nodeList[i].voteComment[j].heat) + "|" + str(nodeList[i].voteComment[j].value)
            f1.write(txttofile+"\n")

    f1.close()

def findPos(user):
    foundPos = -1
    i = 0
    while (foundPos == -1) and i < len(targetList):
        if targetList[i] == user:
            foundPos = i
        i+=1
    return foundPos

def genMatrix(size):
    global adjMatrix
    adjMatrix = []
    mySize = 10
    # First of all, let's generate the di-graph with a matrix full of 0s
    row = []
    for i in range(size):
        row = []
        for j in range(size):
            row.append(0)
        row[i] = 1
        adjMatrix.append(row)
    return adjMatrix

def friendOrFoe(user1,user2):
    global nodeList
    myGuessing=0
    whereUser1 = findPos(user1)
    whereUser2 = findPos(user2)
    # the idea is to have a -1 to 1 value. -1 means nemesis, 1 means bestie, ally should be between 0.25 to 0.8.
    # values nearby 0 values is "neutral", foe between -0.8 to -0.25
    # http://snap.stanford.edu/class/cs224w-readings/brzozowskl08friendsandfoes.pdf
    # ideally voting values from both users each other should be similar. It can be checked later.
    if user1 not in nodeList.keys():
        return -3
    if user2 not in nodeList[user1].voteComment.keys():
        return -2
    else:
        myGuessing = nodeList[user1].voteComment[user2].value / nodeList[user1].voteComment[user2].getHeat()
    return myGuessing


def genAll():
    global nodeList
    global pos
    global betCent
    global degreeCentral
    global closenessCentral
    global eigenCentral
    # Loading initial users
    loadDefaults()
    # loading profile public data
    checkProfiles()
    for i in nodeList.keys():
        getEdgeVotedComments(i)
        getEdgeVotedNotes(i)
    print("collecting data for bottom-left matrix")
    for i in list(nodeList):
        for j in nodeList[i].voteComment.keys():
            if nodeList[i].voteComment[j].target not in nodeList.keys():
                newNode = userNode(nodeList[i].voteComment[j].target)
                nodeList[newNode.user] = newNode
                getProfile(newNode.user)
                getEdgeVotedComments(newNode.user)
                getEdgeVotedNotes(newNode.user)
    # purging non desired elements
    k = list()
    for i in nodeList.keys():
        if re.match('^-+\d',i):
            k.append(i)
    for elem in k:
        nodeList.pop(elem)
    for i in nodeList.keys():
        kk = list()
        for j in nodeList[i].voteComment.keys():
            if re.match('^-+\d',j):
                kk.append(j)
        for k in kk:
            nodeList[i].voteComment.pop(k)
    for i in nodeList.keys():
        for j in nodeList[i].voteComment.keys():
            Gfriends.add_edge(nodeList[i].user,nodeList[i].voteComment[j].target, weight=nodeList[i].voteComment[j].value)
    print("please wait, this is going to take a while. Calculating positions on the graph")
    pos = nx.spring_layout(Gfriends)
    print("Calculation of betweenness")
    betCent = nx.betweenness_centrality(Gfriends, weight='weight',normalized=True, endpoints=True)
    print("Calculation eigenvectors")
    eigenCentral= nx.eigenvector_centrality(Gfriends,  weight='weight')
    print("Calculation of centrality")
    closenessCentral= nx.closeness_centrality(Gfriends)
    print("Calculation of degree by weight")
    degreeCentral= nx.degree_centrality(Gfriends)
    print("backup, makes no sense to do it everyday")
    do_Backup()

def genericActions():
    global nodeList
    global pos
    global betCent
    global degreeCentral
    global closenessCentral
    global eigenCentral
    global Gfriends
    nodeList = do_Restore('nodes')
    for i in nodeList.keys():
        targetList.append(nodeList[i].user)
    adjMatrix = genMatrix(len(targetList))

    #we populate now the adjacency matrix. This one is considering that each Aij is referencing itself.
    for i in range(len(targetList)):
        for j in range(len(targetList)):
            if i != j :
               if targetList[j] in nodeList[targetList[i]].voteComment.keys():
                   adjMatrix[i][j] = 1

    for i in nodeList.keys():
        for j in nodeList[i].voteComment.keys():
            Gfriends.add_edge(nodeList[i].user,nodeList[i].voteComment[j].target, weight=nodeList[i].voteComment[j].value)

    pos = do_Restore('pos')
    betCent = do_Restore('btw')
    degreeCentral = do_Restore('degree')
    closenessCentral = do_Restore('closeness')
    eigenCentral = do_Restore('eigen')

    print("betweeenness ")
    print(sorted(betCent, key=betCent.get, reverse=True)[:40])
    print("closeness ")
    print(sorted(closenessCentral,key=closenessCentral.get,reverse=True)[:100])
    print("degree ")
    print(sorted(degreeCentral,key=degreeCentral.get,reverse=True)[:40])
    print("eigenvector ")
    print(sorted(eigenCentral,key=eigenCentral.get,reverse=True)[:40])


def genUserGraph(withThisList):
    global Gfriends
    global betCent
    genericActions()
    node_color = [20000.0 * Gfriends.degree(v) for v in Gfriends]
    node_size = [v * 10000 for v in betCent.values()]
    plt.figure(figsize=(50,50))
    minidict = {}
    minilist = []
    for i in withThisList:
        minilist.append(i)
        for j in nodeList[i].voteComment.keys():
            if j not in minidict.keys():
                minidict[j] = nodeList[i].voteComment[j].value
    print(sorted(minidict,key=minidict.get,reverse=True)[:20])
    for elem in sorted(minidict,key=minidict.get,reverse=True)[:20]:
        minilist.append(elem)
    #kkkk = Gfriends.subgraph(sorted(eigenCentral,key=eigenCentral.get,reverse=True)[:35])
    kkkk = Gfriends.subgraph(minilist)
    nx.draw_networkx(kkkk, pos = pos)
    if len(withThisList) == 1:
        plt.savefig(withThisList[0] + ".png")
    else:
        plt.savefig("userGraphReport.png")


genericActions()
print(nx.info(Gfriends))

print(str(friendOrFoe('Charles_Dexter_Ward','JavierB')))
print(str(friendOrFoe('JavierB','Charles_Dexter_Ward')))

#node_color = [20000.0 * Gfriends.degree(v) for v in Gfriends]
#node_size = [v * 10000 for v in betCent.values()]
#plt.figure(figsize=(50,50))
#nx.draw_networkx(Gfriends, pos=pos, node_color=node_color, node_size=node_size)

#plt.savefig("mñm.png")




#print(len(nodeList))

#do_Backup()




