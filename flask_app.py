from flask import Flask,render_template,request,jsonify,redirect,url_for
import mysql.connector
from flask_ngrok import run_with_ngrok
#from flask_mail import Mail, Message

class User:
    def __init__(self,name,reg_no,branch,mail_id,db):
        self.name=name
        self.reg_no=reg_no
        self.branch=branch
        self.mail=mail_id
        self.db=db
    def disp(self):
        print(self.name,self.reg_no,self.branch,self.mail)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  database="spotlight"
)

myc = mydb.cursor()

def login(user,pwd,db):
    regq = f"select reg_no from {db}"
    reg_list = []
    reg = user
    password = pwd
    check = f"select * from {db} where reg_no='{reg}'"
    myc.execute(regq)
    for i in myc:
        for j in i:
            reg_list.append(j)

    if reg in reg_list:
        myc.execute(check)
        for i in myc:
            pass_check = i[4]
        if password == pass_check:
            global u
            u = User(i[0],i[1],i[2],i[3],db)
            return 1
        else:
            return "password incorrect"
    else:
        return "User not found"
    

def register(name,reg_no,branch,mail,pwd,db):
    regq = f"select reg_no from {db}"
    reg_list = []
    add = f"insert {db} (name,reg_no,branch,mail_id,password) values(%s,%s,%s,%s,%s)"
    val = (name,reg_no,branch,mail,pwd)
    myc.execute(regq)
    for i in myc:
        for j in i:
            reg_list.append(j)

    if reg_no in reg_list:
        return (f"{reg_no} user already exist")
    else:
        myc.execute(add,val)
        mydb.commit()
        return 1
    
def complaint(name,mail,reg_no,sub,disc):
    myc.execute("select count(*) from complaint")
    for i in myc:
        id=(i[0])+1
    cmp = "insert complaint(id,name,mail,reg_no,sub,disc,status) values(%s,%s,%s,%s,%s,%s,%s)"
    values = (id,name,mail,reg_no,sub,disc,0)
    myc.execute(cmp,values)
    mydb.commit()
    return id,'Complaint Successfully Uploaded'

def update(status,id):
    myc.execute(f"update complaint set status='{status}' where id={id}")
    mydb.commit()

app = Flask(__name__,template_folder='templates')
#run_with_ngrok(app)

@app.route('/')
@app.route('/home',methods=['POST','GET'])
def home():
    if logins==1:
        if request.method=='POST':
            name = request.form['Name']
            mail = request.form['email']
            reg_no = request.form['Reg_no']
            sub = request.form['sub']
            img = request.files['img']
            disc = request.form['disc']
            id,status=complaint(name,mail,reg_no,sub,disc)
            if id!=0:
                img.save(f"static/images/{id}.jpg")
            return render_template('demo.html',status=status,name=u.name,reg_no=u.reg_no,branch=u.branch,mail=u.mail)
        return render_template('demo.html',name=u.name,reg_no=u.reg_no,branch=u.branch,mail=u.mail) 
    else:
        return render_template('login2.html')


@app.route('/login',methods=['POST','GET'])
def Login():
    if request.method == 'POST':
        uname = request.form['uname'].upper()
        pwd = request.form['pwd']
        db = request.form['select']
        status = login(uname,pwd,db)
        if status == 1:
            global logins
            logins = 1
            return redirect(url_for('home'))
        else:
            return render_template('login2.html',status=status)
    return render_template('login2.html')

@app.route('/student-signup',methods=['POST','GET'])
def s_signup():
    if request.method=='POST':
        uname = request.form['uname'].upper()
        name = request.form['name']
        branch = request.form['branch'].upper()
        mail = request.form['Mail'].lower()
        pwd = request.form['pwd']
        cpwd = request.form['cpwd']
        db = 'student'
        if pwd!=cpwd:
            return render_template("signuppage.html",status='password not matched')
        status = register(name,uname,branch,mail,pwd,db)
        if status == 1:
            return render_template('login2.html')
        else:
            return render_template('signuppage.html',status=status)
    return render_template('signuppage.html')

@app.route('/management-signup',methods=['POST','GET'])
def m_signup():
    if request.method=='POST':
        uname = request.form['uname'].upper()
        name = request.form['name']
        branch = request.form['branch'].upper()
        mail = request.form['Mail'].lower()
        pwd = request.form['pwd']
        cpwd = request.form['cpwd']
        db = 'management'
        if pwd!=cpwd:
            return render_template("signuppage2.html",status='password not matched')
        status = register(name,uname,branch,mail,pwd,db)
        if status == 1:
            return render_template('login2.html')
        else:
            return render_template('signuppage2.html',status=status)
    return render_template('signuppage2.html')

@app.route('/logout')
def logout():
    global logins
    logins=0
    return redirect(url_for('Login'))

@app.route('/status')
def status():
    data=[]
    buttons=0
    if u.db=='management':
        buttons=1
    myc.execute("select * from complaint where status='0'")
    for i in myc:
        data.append(list(i))
    return render_template('index.html',data=data,buttons=buttons)

@app.route('/accepted')
def accept():
    data=[]
    buttons=0
    if u.db=='management':
        buttons=1
    myc.execute("select * from complaint where status='accepted'")
    for i in myc:
        data.append(list(i))
    return render_template('index.html',data=data,buttons=buttons)

@app.route('/rejected')
def reject():
    data=[]
    buttons=0
    if u.db=='management':
        buttons=1
    myc.execute("select * from complaint where status='rejected'")
    for i in myc:
        data.append(list(i))
    return render_template('index.html',data=data,buttons=buttons)

@app.route('/completed')
def complete():
    data=[]
    buttons=0
    if u.db=='management':
        buttons=1
    myc.execute("select * from complaint where status='completed'")
    for i in myc:
        data.append(list(i))
    return render_template('index.html',data=data,buttons=buttons)

from flask import jsonify

@app.route('/buttons', methods=['POST'])
def buttons():
    try:
        data = request.get_json(force=True)
        status = data.get('status')
        id = data.get('id')
        print("Received value:", status, id)
        update(status, id)

        # Create a JSON response indicating the redirect URL
        response = {"redirect": None}

        # Set the redirect URL based on the status value
        if status == 'accepted':
            response["redirect"] = url_for('accept')
        elif status == 'rejected':
            response["redirect"] = url_for('reject')
        elif status == 'completed':
            response["redirect"] = url_for('complete')
        else:
            response["redirect"] = url_for('status')

        return jsonify(response)

    except Exception as e:
        print("Exception occurred:", e)
        return jsonify({"redirect": url_for('status')})  # Fallback redirect URL in case of an exception

 
@app.route('/search',methods=['POST'])
def search():
    if request.method=='POST':
        data =[]
        id = request.form['complaint_id']
        myc.execute(f"select * from complaint where id={id}")
        for i in myc:
            data.append(list(i))
        buttons=0
        if u.db=='management':
            buttons=1
        return render_template('index.html',data=data,buttons=buttons)



if '__main__'==__name__:
    logins=0
    app.run(port=2,debug=True)