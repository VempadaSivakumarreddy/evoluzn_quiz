import random
from re import sub
from MySQLdb import cursors
from  database import Database as MyDb


conn = MyDb.connect_dbs()
cursor = conn.cursor()



def insertQuestions():

    cursor.execute("SELECT * FROM `quiz`.`questions`")
    myresult = cursor.fetchall()

    lastPrimaryKey = len(myresult)

    with open("D:\Quiz\Questions.csv" ,mode="r",encoding="utf-8") as questionContainer:
        questionsRowWise = questionContainer.read().split("\n")[1:]
        questionContainer.close()

    for indx ,row in enumerate(questionsRowWise):
       # print(indx,row)
        primaryKey = lastPrimaryKey+indx+1
        asList = row.split(",")
        question = asList[0].strip()
        options = asList[1].replace('|',',').strip()
        correctAns = asList[2].strip()
        Subject = asList[3].strip()

        query = "INSERT INTO `quiz`.`questions` (`idquestions`, `questionid`, `question`, `options`, `CorrectAnswer`, `Subject`) VALUES ('{id}', '{idq}', '{qsn}', '{opn}', '{cAns}', '{sub}')".format(id=primaryKey,idq=str(primaryKey),qsn =question,opn = options,cAns = correctAns,sub = Subject)
        #print(query)
        cursor.execute(query)
        conn.commit()
        # mycursor.execute("SELECT * FROM customers")
        # cursor.excecute("INSERT INTO `quiz`.`questions` (`idquestions`, `questionid`, `question`, `options`, `CorrectAnswer`, `Subject`) VALUES ('3', '3', '2+3', '4,3,9', '5', 'Math')")

# insertQuestions()




def GetQuestions(cursor , NoOfReqQuestions , Subject):
    # subjects Example Math, General, Programming

    query = "SELECT * FROM `quiz`.`questions` WHERE Subject ='{subject}'".format(subject =Subject)

    cursor.execute(query)
    reqSubQusetions = cursor.fetchall()
    
    questionsAslist = list(reqSubQusetions)
    randomQuestions = []

    maxQusns = NoOfReqQuestions if len(questionsAslist) >= NoOfReqQuestions else len(questionsAslist)
    #print('length ',len(reqSubQusetions),maxQusns)
    for i in range(0,maxQusns):
        randomIndx = random.randint(0,len(questionsAslist)-1)
        #print(randomIndx)
        randomQuestions.append(questionsAslist.pop(randomIndx))

    return randomQuestions



