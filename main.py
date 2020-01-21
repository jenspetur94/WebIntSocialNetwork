from numpy import linalg as LA
import numpy as np
from user import User
from gap import Gap
from review import Review
from decimal import *

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
    print("Adjacency done!")
    laplacianMatrix = Laplacian(adjacencyMatrix)
    print("Laplacian done!")
    eigVector = CalculateEigenVector(laplacianMatrix)
    print("Eigvector done!")
    number_of_clusters = 5
    community_gaps = CutAtGaps(eigVector, number_of_clusters - 1)
    print("Number of gaps: " + str(len(community_gaps)))
    print("Cut at gaps done!")
    getcontext().prec = 28 # opsætter decimal
    eigVector = eigVector.tolist()
    list_of_communities = SplitCommunities(eigVector, user_list, community_gaps) 
    print("Number of communities: " + str(len(list_of_communities)))
    for community in list_of_communities:
        print("Size of community: " + str(len(community)))
    
    main2(list_of_communities)

# head lille værdi
# tail stor værdi
# Overvej bare at splitte i midten af tail og head

def SplitCommunities(eigvector, user_list, community_gaps):
    communities_with_users = []

    community_splits = []
    for i in range(0, len(community_gaps)):
        community_splits.append((community_gaps[i].head + community_gaps[i].tail) / 2)
    print(community_splits)
    community_splits.sort()
    print(community_splits)
    #for i in range(0, len(community_splits)):
    #    print("Split range: " + str(community_splits[i]))

    for i in range(0, len(community_splits)):
        community_with_users = []
#       print("Head " + str(community_gaps[i].head) + " < " + " eigval "+ " < " + " Tail " + str(community_gaps[i-1].tail))
        for user in user_list:
            if eigvector[user.id] <= community_splits[i]:
                community_with_users.append(user)
                user_list.remove(user)
        communities_with_users.append(community_with_users)
    
    communities_with_users.append(user_list)
    return communities_with_users


    

def main2(list_of_communities):
    f = open("SentimentTrainingData.txt", "r")

    a = f.readlines()

    review_list = []
    length = len(a)
    nextId = 1

    for x in range(0, 226530, 9):
        productId = a[x][19:].strip()
        userId = a[x+1][15:]
        profileName = a[x+2][20:]
        helpfulness = a[x+3][19:]
        score = float(a[x+4][14:])
        time = a[x+5][13:]
        summary = a[x+6][16:]
        text = a[x+7][13:]
        review_list.append(Review(nextId, productId, userId, profileName, helpfulness, score, time, summary, text))
        nextId += 1
    
    total_number_of_reviews = len(review_list)
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
    predictions = []


    test_review = "I purchased this formula but was worried after reading the comments here that my 5 month old baby would suffer from constipation.  He did.  However, I really wanted to use organic formula so I added a few teaspoons of prunes to his cereal and within 12 hours - problem solved.  No constipation since and he has been on this formula for about 2 weeks. I give him some prune/cereal every 4 days.  If your baby is not yet on solids you might consider giving him a little apple or pear juice mixed with water.  This should do the trick also.  Don't let the constipation issue scare you off."
    scores = []
    for i in ["1", "2", "3", "4", "5"]:
        scores.append(PredictScore2(test_review.split(), dictionary_of_scoredict[i], word_count_of_scoredict[i], number_of_reviewsdict[i], total_number_of_reviews))
    print(scores)


    #for community in list_of_communities:
    #    predictions.append(PredictMany(community, dictionary_of_scoredict, word_count_of_scoredict, number_of_reviewsdict, total_number_of_reviews))

    #PrintPredictions(list_of_communities, predictions, dictionary_of_scoredict, word_count_of_scoredict, number_of_reviewsdict, total_number_of_reviews)

#Something is very wrong with the predictions

def PredictScore2(review_to_predict, dictionary_of_score, word_count_of_score, number_of_reviews_with_score, total_number_of_reviews):
    probability = 1
    for n in range(1, len(review_to_predict) + 1):
        try:
            dictionary_of_score[word]
        except:
            continue
        word = review_to_predict[n - 1]
        probability *= n * (dictionary_of_score[word] / word_count_of_score)
    probability *= number_of_reviews_with_score / total_number_of_reviews
    return probability

def PrintPredictions(communities, predictions, dictionary_of_score, word_count_of_score, number_of_reviews_with_score, total_number_of_reviews):
    for community in communities:
        community_average = PredictMany(community, dictionary_of_score, word_count_of_score, number_of_reviews_with_score, total_number_of_reviews)
        for user in community:
            if 3 < community_average:
                if len(user.review.split()) > 2:
                    a = 0
                    print(str(user.username) + " " +  str(PredictHighest(user.review.split(), dictionary_of_score[user.id], word_count_of_score[user.id], number_of_reviews_with_score[user.id], total_number_of_reviews)) + " * ")    
                else:
                    print(str(user.username) + " * " + " yes ")
            else:
                if len(user.review.split()) > 2:
                    a = 0
                    print(str(user.username) + " " +  str(PredictHighest(user.review.split(), dictionary_of_score, word_count_of_score, number_of_reviews_with_score, total_number_of_reviews)) + " * ")    
                else: 
                    print(str(user.username) + " * " + " no ")

        #print(str(user.username) + )
    #FindError(dictionary_of_scoredict, word_count_of_scoredict, number_of_reviewsdict, total_number_of_reviews)
def PredictHighest(review, dictionary_of_scoredict, word_count_of_scoredict, number_of_reviewsdict, total_number_of_reviews):
    scores = []
    for i in ["1", "2", "3", "4", "5"]:
        predicted_score = PredictScore(review, dictionary_of_scoredict[i], word_count_of_scoredict[i], number_of_reviewsdict[i], total_number_of_reviews)
        scores.append(predicted_score)
    return scores.index(max(scores)) + 1

def FindError(dictionary_of_scoredict, word_count_of_scoredict, number_of_reviewsdict, total_number_of_reviews):
    f = open("SentimentTestingData.txt", "r")

    a = f.readlines()

    review_list = []
    length = len(a)
    nextId = 1

    for x in range(0, 226530, 9):
        print(x)
        productId = a[x][19:].strip()
        userId = a[x+1][15:]
        profileName = a[x+2][20:]
        helpfulness = a[x+3][19:]
        score = float(a[x+4][14:])
        time = a[x+5][13:]
        summary = a[x+6][16:]
        text = a[x+7][13:]
        review_list.append(Review(nextId, productId, userId, profileName, helpfulness, score, time, summary, text))
        nextId += 1
    
    total_number_of_reviews = len(review_list)
    review_list_1 = ReviewsWithScore(review_list, 1)
    review_list_2 = ReviewsWithScore(review_list, 2)
    review_list_3 = ReviewsWithScore(review_list, 3)
    review_list_4 = ReviewsWithScore(review_list, 4)
    review_list_5 = ReviewsWithScore(review_list, 5)

    negative_review_list = review_list_1 + review_list_2
    positive_review_list = review_list_4 + review_list_5

    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0

    #for review in review_list:
    


def PredictMany(community, dictionary_of_scoredict, word_count_of_scoredict, number_of_reviewsdict, total_number_of_reviews):
    temp = 0
    no_review = 0
    for user in community:
        scores = []
        
        if (len(user.review.split()) < 2):
            no_review += 1
            continue

        for i in ["1", "2", "3", "4", "5"]:
            predicted_score = PredictScore(user.review.split(), dictionary_of_scoredict[i], word_count_of_scoredict[i], number_of_reviewsdict[i], total_number_of_reviews)
            scores.append(predicted_score)
        temp += scores.index(max(scores)) + 1

    if no_review != len(community):
        average_rating = temp / (len(community) - no_review)
    else:
        average_rating = temp / len(community)
    
    print(average_rating)

    return average_rating


    #test_review = "My cats have been happily eating Felidae Platinum for more than two years. I just got a new bag and the shape of the food is different. They tried the new food when I first put it in their bowls and now the bowls sit full and the kitties will not touch the food. I've noticed similar reviews related to formula changes in the past. Unfortunately, I now need to find a new food that my cats will eat."
    #scores = []
    #for i in ["1", "2", "3", "4", "5"]:
    #    scores.append(PredictScore(test_review.split(), dictionary_of_scoredict[i], word_count_of_scoredict[i], number_of_reviewsdict[i], total_reviews))
    #print(scores)

    #tempScore = 0
    #tempProbability = 0
    #for i in range(0, 5):
    #    if scores[i] > tempProbability:
    #        tempProbability= scores[i]
    #        tempScore = i + 1
    #
    #print('score is: ' + str(tempScore) + ' with probability: ' + str(tempProbability))
    # 
    # single_word / word_count(score)
    # Estimate p(word | score)

def PredictScore(review_to_predict, dictionary_of_score, word_count_of_score, number_of_reviews_with_score, total_number_of_reviews):
    probability = 1


    for n in range(1, len(review_to_predict) + 1):
        word = review_to_predict[n - 1]
        try:
            if dictionary_of_score[word] == 0:
                dictionary_of_score[word] = 1
                print("Dictionary of score er 0")
            if word_count_of_score == 0:
                word_count_of_score = 1
                print("Word count er 0")
            if n == 0:
                print("N er 0")
            probability *= n * (dictionary_of_score[word] / word_count_of_score)
        except: 
            continue
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
def CutAtGaps(eigVector, number_of_clusters):
    getcontext().prec = 28 # opsætter decimal
    orderedEigVector = eigVector.tolist()
    orderedEigVector.sort()
    #print(orderedEigVector)
    length = eigVector.size
    maxdifference = []
    for i in range(0, number_of_clusters):
        maxdifference.append(Gap(-1, -1, -1))
    
    # For K clusters, så lav en løkke således at Gap bliver tilføjet K gange.
    for x in range(0, (length - 1)):
        head = orderedEigVector[x]
        tail = orderedEigVector[x+1]
        distance = Decimal(tail) - Decimal(head)
        # sorter maxdifference så den med lavest distance ligger forest
        maxdifference.sort(key=lambda gap: gap.distance)
        for y in range(0,2):
            if(maxdifference[y].distance < distance):
                maxdifference[y].distance = distance
                maxdifference[y].head = head
                maxdifference[y].tail = tail
                break
    return maxdifference

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
    

    return diagonalMatrix

def Laplacian(adjacencyMatrix):
    diagonalMatrix = Diagonal(adjacencyMatrix) 
    
    length = len(adjacencyMatrix)
    laplacianMatrix = [[0 for x in range(length+1)] for y in range(length+1)]

    # Sum all togethers
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
    return eigenvector[1]

if __name__ == "__main__":
    main()
