from os import read
from flask import Flask,render_template,request
import flask
from mysql.connector import connect
from mysql.connector.connection import MySQLConnection

def get_db_connection():
    mysqlConnection = connect(host="localhost",port=3306,database='vaccination_drive',user='doc',password='doc',auth_plugin='mysql_native_password')
    return mysqlConnection

app = Flask(__name__)
vaccine_dict = {}

@app.before_first_request
def populate_ds():
    
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute("select * from vaccination")
    rows=cursor.fetchall()

    if rows==None : return

    for row in rows: 
        info={}
        info["reference_number"]=row[0]  
        info["name"]=row[1]
        info["mobile_number"]=row[2]
        info["aadhar_card_number"]=row[3]
        info["vaccine_name"]=row[4]
        vaccine_dict[row[0]]=info        
    conn.close()

@app.route('/index')
def index():
    return render_template('index.html',vaccine_dict=vaccine_dict)

@app.route('/register')
def register():
    return render_template('register.html',vaccine_dict=vaccine_dict)

@app.route("/registerRecipient",methods=["POST"]) 
def registerRecipient() :
    info={"name" : "","mobile_number":"","aadhar_card_number":"","vaccine_name":""}
    for key,value in request.form.items() :
        if  key=="name" : info["name"]=value
        if  key=="mobileNumber" : info["mobile_number"]=value
        if  key=="aadharCardNumber" : info["aadhar_card_number"]=value
        if  key=="vaccineName" : info["vaccine_name"]=value
    errors=[]
    for key,value in info.items() :
        if value=="" : errors.append(f"{key} required")  
    if len(errors)>0 : return render_template("error.html",vaccine_dict=vaccine_dict,errors=errors)
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("insert into vaccination (name,mobile_number,aadhar_card_number,vaccine_name) values(%s,%s,%s,%s)",(info["name"],info["mobile_number"],info["aadhar_card_number"],info["vaccine_name"]))
    info["reference_number"]=cursor.lastrowid
    vaccine_dict[info["reference_number"]]=info
    conn.commit()
    conn.close()
    return render_template("message.html",vaccine_dict=vaccine_dict,message=f"{info['name']} registered with reference number : {info['reference_number']}")

@app.route("/update/<reference_number>")
def update(reference_number):
     return render_template("update.html",vaccine_dict=vaccine_dict,reference_number=reference_number)

@app.route("/updateRecord/<reference_number>",methods=["POST"])
def updateRecord(reference_number) :
    info={}
    reference_number=int(reference_number)
    for key,value in request.form.items() :
        if  key=="name" : info["name"]=value
        if  key=="mobileNumber" : info["mobile_number"]=value
        if  key=="aadharCardNumber" : info["aadhar_card_number"]=value
        if  key=="vaccineName" : info["vaccine_name"]=value
    conn=get_db_connection()
    cursor=conn.cursor()
    sql="update vaccination set "
    flag=False
    dictInfo=vaccine_dict[reference_number]
    for key,value in info.items() :
        if value!="" :
            s=f'{key}="{value}",' 
            dictInfo[key]=value
            sql+=s
            flag=True
    if flag==True :
        if sql.endswith(",") : sql=sql[:len(sql)-1]
        sql+=f' where reference_number={reference_number}'
        cursor.execute(sql)
        vaccine_dict[reference_number]=dictInfo     
        conn.commit()
        conn.close()
    return render_template("message.html",vaccine_dict=vaccine_dict,message=f"Record registered with reference number : {reference_number} updated")

@app.route("/remove/<reference_number>")
def deleteRecord(reference_number) :
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute("delete from vaccination where reference_number=%s",(reference_number,))
    vaccine_dict.pop(int(reference_number)    )
    conn.commit()
    conn.close() 
    return render_template("message.html",vaccine_dict=vaccine_dict,message=f"Record registered with reference number : {reference_number} deleted")

@app.route('/')
def login():
    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)