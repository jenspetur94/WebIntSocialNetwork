from numpy import linalg as LA
import numpy as np
from user import User
from gap import Gap
from review import Review

def main():
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

def main2():
    f = open("SentimentTrainingData.txt", "r")

    a = f.readlines()

    review_list = []
    length = len(a)
    print(length)
    nextId = 1
    for x in range(0, length, 9):
        productId = a[x][19:].strip()
        userId = a[x+1][15:]
        profileName = a[x+2][20:]
        helpfulness = a[x+3][20:]
        score = float(a[x+4][14:])
        time = a[x+5][13:]
        summary = a[x+6][16:]
        text = a[x+7][13:]
        review_list.append(Review(nextId, productId, userId, profileName, helpfulness, score, time, summary, text))
        nextId += 1
    
    total_reviews = len(review_list)
    review_list_1 = ReviewsWithScore(review_list, 1)
    review_list_2 = ReviewsWithScore(review_list, 2)
    review_list_3 = ReviewsWithScore(review_list, 3)
    review_list_4 = ReviewsWithScore(review_list, 4)
    review_list_5 = ReviewsWithScore(review_list, 5)

    # Counts the number of times the word x appears for each score
    result = CreateDictionaryOfWords(review_list)
    word_count_of_scoredict = result[0]
    dictionary_of_scoredict = result[1]
    number_of_reviewsdict = result[2]
    
    test_review = "My cats have been happily eating Felidae Platinum for more than two years. I just got a new bag and the shape of the food is different. They tried the new food when I first put it in their bowls and now the bowls sit full and the kitties will not touch the food. I've noticed similar reviews related to formula changes in the past. Unfortunately, I now need to find a new food that my cats will eat."
    scores = []
    for i in ["1", "2", "3", "4", "5"]:
        scores.append(PredictScore(test_review.split(), dictionary_of_scoredict[i], word_count_of_scoredict[i], number_of_reviewsdict[i], total_reviews))
    print(scores)

    tempScore = 0
    tempProbability = 0
    for i in range(0, 5):
        if scores[i] > tempProbability:
            tempProbability= scores[i]
            tempScore = i + 1
    
    print('score is: ' + str(tempScore) + ' with probability: ' + str(tempProbability))
    # 
    # single_word / word_count(score)
    # Estimate p(word | score)

def PredictScore(review_to_predict, dictionary_of_score, word_count_of_score, number_of_reviews_with_score, total_number_of_reviews):
    probability = 1
    for n in range(1, len(review_to_predict) + 1):
        word = review_to_predict[n - 1]
        probability *= n * (dictionary_of_score[word] / word_count_of_score)
    probability *= number_of_reviews_with_score / total_number_of_reviews
    return probability
    # Prediction model:
    # ((for i = 0 to n) * (single_word_occurences[i] / word_count_of_score)) * (number_of_reviews_with_score / total_number_of_reviews)
    # single_word_occurences = number of occurences for that word in reviews with that score
    
    

def CreateDictionaryOfWords(review_list):
    dictionary_of_scoredict = {
        "1": {},
        "2": {},
        "3": {},
        "4": {},
        "5": {}
    }
    
    word_count_of_scoredict = {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
    }

    number_of_reviewsdict = {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
    }
    
    for review in review_list: 
        words = review.text.split()
        for word in words:
            if word in dictionary_of_scoredict[str(int(review.score))]:
                dictionary_of_scoredict[str(int(review.score))][word] += 1
            else:
                dictionary_of_scoredict[str(int(review.score))][word] = 1
            
            word_count_of_scoredict[str(int(review.score))] += 1
            number_of_reviewsdict[str(int(review.score))] += 1
    return (word_count_of_scoredict, dictionary_of_scoredict, number_of_reviewsdict)


    
def FindCertainScore(review_list, i):
    count = 0
    for review in review_list:
        if(review.score == i):
            count+= 1
    return count

def ReviewsWithScore(review_list, score):
    positive_review_list = []
    for review in review_list:
        if(review.score == score):
            positive_review_list.append(review)
    return positive_review_list

# [1, 5, 10, 100, 105, 109, 200, 205, 230] = eigVector
# n = 3
# 10 og 100, 109 og 200, 205 og 230
# Cluster 10 > og < 100
def CutAtGaps(eigVector):
    orderedEigVector = eigVector.tolist()
    orderedEigVector.sort()
    #print(orderedEigVector)
    length = eigVector.size
    maxdifference = [Gap(-1, -1, -1), Gap(-1, -1, -1), Gap(-1, -1, -1)]
    for x in range(0, (length - 1)):
        head = orderedEigVector[x]
        tail = orderedEigVector[x+1]
        distance = orderedEigVector[x-1] - orderedEigVector[x]
        # sorter maxdifference så den med lavest distance ligger forest
        for y in range(0,2):
            if(maxdifference[y].distance < distance):
                maxdifference[y].distance = distance
                maxdifference[y].head = head
                maxdifference[y].tail = tail
                break


    print(maxdifference[0].distance)
    print(maxdifference[0].head)
    print(maxdifference[0].tail)
    print(maxdifference[1].distance)
    print(maxdifference[1].head)
    print(maxdifference[1].tail)    
    print(maxdifference[2].distance)
    print(maxdifference[2].head)
    print(maxdifference[2].tail)


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
    eigenvector = eigenvector.real
    print(type(eigenvector[1]))
    return eigenvector[1]

if __name__ == "__main__":
    main2()
