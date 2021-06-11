import random
from re import L, sub
from flask import Flask, render_template, request,session,redirect,url_for, flash
import MySQLdb
from database import Database as Mydatabase
from MySQLdb.cursors import DictCursor
from random import Random, randrange
import random as rand
import time
import datetime
from flask_mail import Mail, Message
import smtplib, ssl
import time
from DataBaseUtility import GetQuestions
from wtforms_components import TimeField
from functools import wraps
from datetime import timedelta, datetime

app = Flask(__name__,static_folder='static',
            template_folder='templates')

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'vempadasivakumarreddy@gmail.com',
    MAIL_PASSWORD = 'Siva@2501'
)
mail= Mail(app)

@app.before_request
def make_session_permanent():
	session.permanent = True
	app.permanent_session_lifetime = timedelta(minutes=15)


def is_logged(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, Please login','danger')
			return redirect(url_for('login'))
	return wrap

                                                                                     
# def is_logged():
#     if session.get('logged_in'):                                                                     
#         return redirect(url_for('main'))                                                                
#     else:                                                                                                     
#         return redirect(url_for('login'))

@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

def sendotponmail(Email, xx,Name):
    var1 = ('Hi %s, <br>Your One time password is : <b>%s</b><br><br>Thanking you,<br>Evoluzn Inc<p align = "justify"><br><br><b>This is a system generated email. You are requested not to reply on this.</b><br><br><b>Disclaimer :</b> This e-mail message is for the sole use of the intended recipient(s) and may contain certain confidential and privileged information. Any unauthorized review, use, disclosure or distribution is prohibited. If you are not the intended recipient, please contact the sender by e-mail and destroy all copies of the original message.</p>'%(Name, xx))
    fromaddr = app.config.get('MAIL_USERNAME')
    toaddrs = Email
    print(fromaddr)
    print(toaddrs)
    print(xx)
    var22 = Message("One time password for Registering in intelliZENS", sender=fromaddr, recipients=[toaddrs])
    var22.html = var1
    mail.send(var22)
    print(Email)
    return True

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        xx = str(rand.randrange(100000, 999999))
        Name = request.form.get('name')
        Email = request.form.get('email')
        Mobile = request.form.get('mobile')
        Qualification = request.form.get('qualification')
        Course = request.form.get('course')
        Year_of_Passout = request.form.get('passout')
        Password = request.form.get('password')
        
        session['email'] = request.form.get('email')
        if 'email' in session:
            e = session['email']
        conn = Mydatabase.connect_dbs()
        cursor = conn.cursor()

        if Email and Mobile:
            cursor.execute("select * from quiz where Mobile = %s or Email = %s",[Mobile,Email])
        elif Email:
            cursor.execute("select * from quiz where Email = %s",[Email])
        else:
            cursor.execute('select * from quiz where Mobile = %s', [Mobile])
        msg = cursor.fetchone()
        if not msg:
            sql = "INSERT INTO quiz (UserRegDate, Name,Email, Mobile, Qualification, Course, Year_of_Passout, Password,OTP) VALUES (%s, %s, %s, %s, %s, %s,%s,%s,%s)"
            cursor.execute(sql, (time.strftime('%Y-%m-%d %H:%M:%S'), Name, Email, Mobile, Qualification, Course, Year_of_Passout, Password, xx,))
            if cursor.rowcount > 0:
                retval = sendotponmail(Email, xx, Name)
                if retval == True:
                    conn.commit()
                    cursor.close()
                    conn.close()
                    return render_template('verify.html', email = e)
                else:
                    conn.rollback()
                    cursor.close()
                    conn.close()
                    return "<h1>User registraion Failed </h1>"
            else:
                conn.rollback()
                cursor.close()
                conn.close()
                return "<h1>User registration Failed </h1>"
        else:
            conn.rollback()
            cursor.close()
            conn.close()
            if msg['Email'] == Email:
                return "<h1>Email Already registered! </h1>"
        cursor.close()
    return render_template ('register.html')

@app.route('/otp_confirmation/', methods=['GET', 'POST'])
def otp_confirmation():
    if request.method == 'POST':
        Email = request.form.get('email')
        OTP = request.form.get('OTP')
        conn = Mydatabase.connect_dbs()
        cursor = conn.cursor()
        if Email:
            Email = Email
        cursor.execute('select * from quiz where Email = %s',[Email])
        msg = cursor.fetchone()
        if msg:
            if msg['OTP'] == OTP:
                
                cursor.execute('update quiz set OTPVerifed = 1 where Email =%s', [Email])
                conn.commit()
                cursor.close()
                conn.close()
                return render_template('confirm.html')
            else:
                conn.rollback()
                conn.commit()
                conn.close()
                return "<h1>Incorrect OTP</h>"
    else:
        return "<h1>Email not found!</h1>"

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method ==  'POST':
        Email = request.form.get('email')
        Password = request.form.get('password')
        session['email'] = request.form.get('email')
        session['logged_in'] = True
        if 'email' in session:
            e = session['email']
        conn = Mydatabase.connect_dbs()
        cursor = conn.cursor()

        if Email:
            Email = Email
        cursor.execute('select * from quiz where(Email = %s)', [Email])
        msg = cursor.fetchone()
        if msg:
            if msg['Password'] == Password:
                conn.commit()
                cursor.close()
                conn.close()
                # return redirect(url_for('setup'))
                # return render_template('quiz.html', questions_list = questions_list, email =e)
                return render_template('main.html', email = e)
            else:
                conn.commit()
                cursor.close()
                conn.close()
                return "<h1>Incorrect Password!</h1>"
        else:
            conn.commit()
            cursor.close()
            conn.close()
            return "<h1>Email/Mobile not registered!</h1>"
        cursor.close()
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
	session.clear()
	flash('Successfully logged out', 'success')
	return redirect(url_for('index'))


@app.route('/main', methods=['GET','POST'])
@is_logged
def main():
    print('ok main')
    session['email'] = request.form.get('email')
    if 'email' in session:
        e = session['email']
    if request.method == 'POST':
        exercise = int(request.form.get["exercise"])
        sets = int(request.form.get["sets"])
        session.get["exercise"] = exercise
        session["sets"] = sets
        session["set_counter"] = 0
        
    print('ok')
        
    return render_template('main.html', email =e)


# @app.route('/main', methods=['GET','POST'])
# @is_logged
# def main():
#     print('ok main')
#     session['email'] = request.form.get('email')
#     if 'email' in session:
#         e = session['email']
#     if request.method == 'POST':
#         exercise = int(request.form.get["exercise"])
#         sets = int(request.form.get["sets"])
#         session.get["exercise"] = exercise
#         session["sets"] = sets
#         session["set_counter"] = 0
        
#     print('ok')
        
#     return render_template('main.html', email =e)


@app.route('/send_email_otp', methods=['GET', 'POST'])
def send_email_otp() :
    if request.method == 'POST':
        xx = str(rand.randrange(100000, 999999))
        Name = request.form.get('name')
        Email = request.form.get('email')
        if 'email' in session:
            e = session['email']
        conn = Mydatabase.connect_dbs()
        cursor = conn.cursor()
        
        cursor.execute("select * from new_table where Email = %s", [Email])
        msg = cursor.fetchone()
        if msg:
            cursor.execute("update new_table set OTP = %s, OTPVerified = 0 where Email = %s", (xx, Email))
            retval = sendotponmail(Email,xx, msg['Name'])
            if retval == True:
                conn.commit()
                cursor.close()
                conn.close()
                return render_template('verify.html', email = e)
            else:
                conn.rollback()
                cursor.close()
                conn.close()
                return "<h1>Request to resend OTP</h1>"
        else:
            conn.rollback()
            cursor.close()
            conn.close()
            return "<h1>Email Id not registered!</h1>"
    else:
        return render_template('Resend_email_otp.html' )


class Question:
    q_id = -1
    question = ""
    option1= ""
    option2=""
    option3=""
    option4=""
    correctOption = -1

    
    def __init__(self, q_id, question, option1, option2, option3, option4, correctOption):
        self.q_id = q_id
        self.question = question
        self.option1 = option1
        self.option2 = option2
        self.option3 = option3 
        self.option4 = option4
        self.correctOption = correctOption
        

    def get_correct_option(self):
        if self.correctOption == 1:
            return self.option1
        elif self.correctOption == 2:
            return self.option2
        elif self.correctOption == 3:
            return self.option3
        elif self.correctOption == 4:
            return self.option4
        else:
            return 0
        

# q1 = Question(1, "What id Capital of Andhra Pradesh?", "Vizag", "Amaravathi", "Karnool", "Tirupathi",1)
# q2 = Question(2, "Largest River in India?", "Godavari", "Yamuna", "cavari", "Ganaga", 4)
# q3 = Question(3, "In Which season rains will be more?", "Summer", 'Winter', "Rainy", "Spring",3)


questions_list = []


def RandomQuestions(questionSubj):

    conn = Mydatabase.connect_dbs()
    cursor = conn.cursor()

    randomQestions =  GetQuestions(cursor, 15,questionSubj)

    print('>>>>>>>>>>>',len(randomQestions))
    questions_list.clear()

    for row in randomQestions :

        correctAns = row['CorrectAnswer']
        options = row['options'].split(',')
        options.append(correctAns)
        randomizedOptions = []

        for opt in range(0,len(options)):
            rIndx = random.randint(0,len(options) -1)
            randomizedOptions.append(options.pop(rIndx))

        
        correctAnsIndx = randomizedOptions.index(correctAns)+1

        tempQuestion = Question(row['idquestions'],row['question'],randomizedOptions[0],randomizedOptions[1],randomizedOptions[2],randomizedOptions[3],correctAnsIndx)
        questions_list.append(tempQuestion)
    
    return questions_list





@app.route("/quiz/<qusestionSubj>")
@is_logged
def quiz(qusestionSubj):
    print('>>>>>>>>>>>>',qusestionSubj)
    global start_time
    if 'email' in session:
            e = session['email']
    start_time = time.strftime('%Y-%m-%d %H:%M:%S')
    
    if request.method == "POST":
        exercise = int(request.form.get["exercise"])
        sets = int(request.form.get["sets"])
        session.get["exercise"] = exercise
        session["sets"] = sets
        session["set_counter"] = 0
        
        
        session['email'] = request.form.get('email')
        
        return redirect(url_for("submitquiz"))
    
    #RandomQuestions('General')

    return render_template('quiz.html', questions_list = RandomQuestions(qusestionSubj), email = e)




# @app.route("/submitquiz", methods=['GET', 'POST'])
# def submitquiz():
#     correct_count = 0
#     selected_option=[]
#     correct_option=[]
#     Question=[]
#     if 'email' in session:
#         e=session['email']
#     if request.method == 'POST':
#         Email = e
#         SrNo = request.form.get('SrNo')
#         Question1 = request.form.get('q1')
#         Question2 = request.form.get('q2')
#         Question3 = request.form.get('q3')
#         option = request.form.get('option')
#         conn = Mydatabase.connect_dbs()
#         cursor = conn.cursor()
#         if Email:
#             cursor.execute('select * from quiz where Email = %s', [Email])
#         print(Email)
#         msg = cursor.fetchone()
#         if msg:
#             cursor.execute('select * from score where SrNo = %s and idquiz = %s',( msg['idquiz'],[SrNo]))
#             found = cursor.fetchone()
#             if not found:
#                 for question in questions_list:
#                     qid = str(question.q_id)
#                     q=str(question.question)
#                     Question.append(q)
#                     selected_options = request.form[qid]
#                     not_selected_options = str(question.not_selected_option)
#                     selected_option.append(selected_options)
#                     correct_options = question.get_correct_option()
#                     correct_option.append(correct_options)
#                     print(not_selected_options)
                    
#                     if qid in request.form and request.form[qid] == correct_options:
#                         correct_count = correct_count + 1
#                     elif selected_options == None:
#                         correct_count = correct_count + 0
#                 else:
#                     correct_count = correct_count + 0
                    

#                 if str(question.question) == 'None':
#                     correct_count = correct_count +0

                    
#                 total_count = str(correct_count )
                        
#                 Question1 = Question[0]
#                 Question2 = Question[1]
#                 Question3 = Question[2]
            
#                 correct_option1 =correct_option[0]
#                 correct_option2 = correct_option[1]
#                 correct_option3 = correct_option[2]
#                 selected_option1 = selected_option[0]
#                 selected_option2 = selected_option[1]
#                 selected_option3 = selected_option[2]
                
                
#                 sql = "INSERT INTO score (total_count, idquiz,Question1,correct_option1,selected_option1,Question2, correct_option2, selected_option2, Question3,correct_option3 , selected_option3) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
#                 cursor.execute(sql, (total_count,msg['idquiz'],Question1,correct_option1, selected_option1,  Question2,correct_option2, selected_option2,  Question3,correct_option3 , selected_option3))
#                 conn.commit()
#                 cursor.close()
#                 conn.close()


#     return render_template('score.html', c=total_count, email =e)


@app.route("/quiz/submitquiz", methods=['GET', 'POST'])
@is_logged
def submitquiz():
    
    print('>>>>>>>>>>>>',start_time)
    correct_count = 0
    selected_option = []
    correct_option = []
    Question = []
    total_count = 0
    session["set_counter"] = 0
    session["sets"] = 1
    
    if 'email' in session:
        e = session['email']
    print(e)
    
    if session["set_counter"] == session["sets"]:
        session["set_counter"] += 0
    
    
    if request.method == 'POST':
        Email = e

        SrNo = request.form.get('SrNo')

        # Question1 = request.form.get('q1') if 'q1' in request.form else None
        # Question2 = request.form.get('q2') if 'q2' in request.form else None
        # Question3 = request.form.get('q3') if 'q3' in request.form else None
       
        

        conn = Mydatabase.connect_dbs()
        cursor = conn.cursor()

        if Email:
            cursor.execute('select * from quiz where Email = %s', [Email])
        print(Email)
        msg = cursor.fetchone()
        if msg:
            cursor.execute('select * from score where SrNo = %s and idquiz = %s', (msg['idquiz'], [SrNo]))
            found = cursor.fetchone()

            if not found:
                for question in questions_list:
                    qid = str(question.q_id)
                    q = str(question.question)
                    Question.append(q)

                    selected_options = request.form[qid] if qid in request.form else None
                    
                    selected_option.append(selected_options)
                    correct_options = question.get_correct_option()
                    correct_option.append(correct_options)
                    

                    if selected_options == correct_options:
                        correct_count = correct_count + 1
                   
                total_count = str(correct_count)

                Question1 = Question[0]
                Question2 = Question[1]
                Question3 = Question[2]
                Question4 = Question[3]
                Question5 = Question[4]
                Question6 = Question[5]
                Question7 = Question[6]
                Question8 = Question[7]
                Question9 = Question[8]
                Question10 = Question[9]
                Question11= Question[10]
                Question12 = Question[11]
                Question13 = Question[12]
                Question14 = Question[13]
                Question15 = Question[14]
                

                correct_option1 = correct_option[0]
                correct_option2 = correct_option[1]
                correct_option3 = correct_option[2]
                correct_option4= correct_option[3]
                correct_option5 = correct_option[4]
                correct_option6 = correct_option[5]
                correct_option7 = correct_option[6]
                correct_option8 = correct_option[7]
                correct_option9 = correct_option[8]
                correct_option10 = correct_option[9]
                correct_option11 = correct_option[10]
                correct_option12 = correct_option[11]
                correct_option13 = correct_option[12]
                correct_option14 = correct_option[13]
                correct_option15 = correct_option[14]
                



                selected_option1 = selected_option[0]
                selected_option2 = selected_option[1]
                selected_option3 = selected_option[2]
                selected_option4 = selected_option[3]
                selected_option5 = selected_option[4]
                selected_option6 = selected_option[5]
                selected_option7 = selected_option[6]
                selected_option8 = selected_option[7]
                selected_option9 = selected_option[8]
                selected_option10 = selected_option[9]
                selected_option11 = selected_option[10]
                selected_option12 = selected_option[11]
                selected_option13 = selected_option[12]
                selected_option14 = selected_option[13]
                selected_option15 = selected_option[14]
                

                sql1 = "INSERT INTO score_count (start_time,end_time,total_count, idquiz,Question,correct_option,selected_option) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql1, (start_time,time.strftime('%Y-%m-%d %H:%M:%S'),
                    total_count, msg['idquiz'], Question1, correct_option1, selected_option1))
                sql2 = "INSERT INTO score_count (start_time,end_time,total_count, idquiz,Question,correct_option,selected_option) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql2, (start_time,time.strftime('%Y-%m-%d %H:%M:%S'),
                    total_count, msg['idquiz'], Question2, correct_option2, selected_option2))
                sql3 = "INSERT INTO score_count (start_time,end_time,total_count, idquiz,Question,correct_option,selected_option) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql3, (start_time,time.strftime('%Y-%m-%d %H:%M:%S'),
                    total_count, msg['idquiz'], Question3, correct_option3, selected_option3))
                sql4 = "INSERT INTO score_count (start_time,end_time,total_count, idquiz,Question,correct_option,selected_option) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql4, (start_time,time.strftime('%Y-%m-%d %H:%M:%S'),
                    total_count, msg['idquiz'], Question4, correct_option4, selected_option4))
                sql5 = "INSERT INTO score_count (start_time,end_time,total_count, idquiz,Question,correct_option,selected_option) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql5, (start_time,time.strftime('%Y-%m-%d %H:%M:%S'),
                    total_count, msg['idquiz'], Question5, correct_option5, selected_option5))
                sql6 = "INSERT INTO score_count (start_time,end_time,total_count, idquiz,Question,correct_option,selected_option) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql6, (start_time,time.strftime('%Y-%m-%d %H:%M:%S'),
                    total_count, msg['idquiz'], Question6, correct_option6, selected_option6))
                sql7 = "INSERT INTO score_count (start_time,end_time,total_count, idquiz,Question,correct_option,selected_option) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql7, (start_time,time.strftime('%Y-%m-%d %H:%M:%S'),
                    total_count, msg['idquiz'], Question7, correct_option7, selected_option7))
                sql8 = "INSERT INTO score_count (start_time,end_time,total_count, idquiz,Question,correct_option,selected_option) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql8, (start_time,time.strftime('%Y-%m-%d %H:%M:%S'),
                    total_count, msg['idquiz'], Question8, correct_option8, selected_option8))
                sql9 = "INSERT INTO score_count (start_time,end_time,total_count, idquiz,Question,correct_option,selected_option) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql9, (start_time,time.strftime('%Y-%m-%d %H:%M:%S'),
                    total_count, msg['idquiz'], Question9, correct_option9, selected_option9))
                sql10 = "INSERT INTO score_count (start_time,end_time,total_count, idquiz,Question,correct_option,selected_option) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql10, (start_time,time.strftime('%Y-%m-%d %H:%M:%S'),
                    total_count, msg['idquiz'], Question10, correct_option10, selected_option10))
                sql11 = "INSERT INTO score_count (start_time,end_time,total_count, idquiz,Question,correct_option,selected_option) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql11, (start_time,time.strftime('%Y-%m-%d %H:%M:%S'),
                    total_count, msg['idquiz'], Question11, correct_option11, selected_option11))
                sql12 = "INSERT INTO score_count (start_time,end_time,total_count, idquiz,Question,correct_option,selected_option) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql12, (start_time,time.strftime('%Y-%m-%d %H:%M:%S'),
                    total_count, msg['idquiz'], Question12, correct_option12, selected_option12))
                sql13 = "INSERT INTO score_count (start_time,end_time,total_count, idquiz,Question,correct_option,selected_option) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql13, (start_time,time.strftime('%Y-%m-%d %H:%M:%S'),
                    total_count, msg['idquiz'], Question13, correct_option13, selected_option13))
                sql14 = "INSERT INTO score_count (start_time,end_time,total_count, idquiz,Question,correct_option,selected_option) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql14, (start_time,time.strftime('%Y-%m-%d %H:%M:%S'),
                    total_count, msg['idquiz'], Question14, correct_option14, selected_option14))
                sql15 = "INSERT INTO score_count (start_time,end_time,total_count, idquiz,Question,correct_option,selected_option) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql15, (start_time,time.strftime('%Y-%m-%d %H:%M:%S'),
                    total_count, msg['idquiz'], Question15, correct_option15, selected_option15))
                conn.commit()
                cursor.close()
                conn.close()
        
    return render_template('score.html', c=total_count, email=e,  sets=session["set_counter"])



# define the countdown func.
# @app.route('/t', methods=['GET', 'POST'])
# def countdown(t):
    
#     while t:
#         mins, secs = divmod(t, 60)
#         timer = '{:02d}:{:02d}'.format(mins, secs)
#         print(timer, end="\r")
#         time.sleep(1)
#         t -= 1
      
#     T = countdown(int(t))
#     return render_template('Countdown.html', T=T)




@app.route("/timer", methods=["GET", "POST"])
def setup():
    if request.method == "POST":
        exercise = int(request.form["exercise"])
        # rest = int(request.form["rest"])
        sets = int(request.form["sets"])

        session["exercise"] = exercise
        # session["rest"] = rest
        session["sets"] = sets
        session["set_counter"] = 0

        return redirect(url_for("exercise"))
    return render_template("home.html")


# @app.route("/rest")
# def rest():
#     return render_template("rest.html", rest=session["rest"])


@app.route("/exercise")
def exercise():
    if session["set_counter"] == session["sets"]:
        return redirect(url_for("completed"))
    session["set_counter"] += 1
    return render_template("exercise.html", exercise=session["exercise"])



@app.route("/complete")
def completed():
    return render_template("complete.html", sets=session["set_counter"])

if __name__ == "__main__":
    app.run(host="0.0.0.0")


