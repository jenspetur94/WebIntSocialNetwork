from numpy import linalg as LA
import numpy as np
from user import User
from gap import Gap

def main():
    A = np.mat("3 2; 1 0")
    print("A :", A)
    print("Eigenvalues :", np.linalg.eigvals(A))
    eigenvalue,eigenvector = np.linalg.eig(A)
    print("Eigenvector:", eigenvector)
    f = open("friendships.reviews.txt", "r")

    a = f.readlines()

    user_list = []
    length = len(a)
    nextId = 1
    for x in range(0, length, 5):
        name = a[x][6:].strip()
        friendsString = a[x+1][9:]
        friends = friendsString.split()
        summary = a[x+2][9:]
        review = a[x+3][8:]
        id = nextId
        user_list.append(User(id, name, friends, summary, review))
        nextId += 1
    
    adjacencyMatrix = CreateAdjacencyMatrix(user_list)

    laplacianMatrix = Laplacian(adjacencyMatrix)
    eigVector = CalculateEigenVector(laplacianMatrix)
    CutAtGaps(eigVector)
    print('hello')



# [1, 5, 10, 100, 105, 109, 200, 205, 230] = eigVector
# n = 3
# 10 og 100, 109 og 200, 205 og 230
# Cluster 10 > og < 100
def CutAtGaps(eigVector):
    orderedEigVector = eigVector.sort()
    length = len(orderedEigVector)
    maxdifference = [Gap(-1, -1, -1), Gap(-1, -1, -1), Gap(-1, -1, -1)]
    for x in range(0, (length - 1)):
        head = orderedEigVector[x]
        tail = orderedEigVector[x+1]
        distance = orderedEigVector[x-1] - orderedEigVector[x]
        for y in range(0,2):
            if(maxdifference[y].distance < distance):
                maxdifference[y].distance = distance
                maxdifference[y].head = head
                maxdifference[y].tail = tail
                break


    print(maxdifference)

def CreateAdjacencyMatrix(users):
    length = len(users)
    adjacencyMatrix = [[0 for x in range(length+1)] for y in range(length+1)]
    print(len(adjacencyMatrix))
    for user in users:
        if(user.id % 1000 == 0):
            print(user.id)
        for friend in user.friends:
            for userfriend in users:
                if userfriend.username == friend:
                    adjacencyMatrix[user.id][userfriend.id] = 1
                    break
    return adjacencyMatrix

def Diagonal(adjacencyMatrix):
    length = len(adjacencyMatrix)
    diagonalMatrix = [0 for x in range(length+1)]
    for x in range(0, length):
        temp = 0
        for y in range(0, length):
            temp = temp + adjacencyMatrix[x][y]
        diagonalMatrix[x] = temp
    print(diagonalMatrix)
    return diagonalMatrix

def Laplacian(adjacencyMatrix):
    diagonalMatrix = Diagonal(adjacencyMatrix) 
    length = len(adjacencyMatrix)
    laplacianMatrix = [[0 for x in range(length+1)] for y in range(length+1)]
    for x in range(0, length):
        for y in range(0, length):
            if x == y:
                laplacianMatrix[x][y] = diagonalMatrix[x]
            else :
                laplacianMatrix[x][y] = -1 * adjacencyMatrix[x][y]
    return laplacianMatrix

def CalculateEigenVector(laplacianMatrix):
    eigenvalue,eigenvector = np.linalg.eig(laplacianMatrix)
    return eigenvector

if __name__ == "__main__":
    main()
