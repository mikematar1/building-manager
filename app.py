from flask import Flask,redirect,render_template,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///building.db"
db = SQLAlchemy(app)
loggedin=False
password="matar"
class Apartment(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    appname = db.Column(db.String(120))
    name = db.Column(db.String(120))
    number = db.Column(db.String(120))
    daterented = db.Column(db.String(120))
    duedate = db.Column(db.String(120))
    nextpaymentdate = db.Column(db.String(120))
    rent = db.Column(db.Integer)
    deposit = db.Column(db.Integer)
    lastkwh = db.Column(db.Integer)
    nkeys = db.Column(db.Integer)
    hascar = db.Column(db.String(10))
    hasremote=db.Column(db.String(10))
    status = db.Column(db.String(120)) #occupied / renovation / available
    
    rents=db.relationship('Rent',backref='apartment',lazy=True)
    ebills = db.relationship('Electricity',backref='apartment',lazy=True)
    def __init__(self,appname,name,number,daterented,duedate,rent,deposit,lastkwh,nkeys,hascar,hasremote,status):
        self.appname=appname
        self.name=name
        self.number=number
        self.daterented=daterented
        self.duedate=duedate
        self.rent=rent
        self.deposit=deposit
        self.lastkwh=lastkwh
        self.nkeys=nkeys
        self.hascar=hascar
        self.hasremote=hasremote
        self.status=status
        
        self.nextpaymentdate = (datetime.strptime(daterented,"%m/%d/%y") + timedelta(30)).strftime("%D")
    def changename(self,newname):
        self.name=newname
    def changenumber(self,newnumber):
        self.number=newnumber
    def changedaterented(self,newdaterented):
        self.daterented=newdaterented
        daterentedmonth = datetime.strptime(self.daterented,"%m/%d/%y")
        thismonth = datetime.today()
        num_months = (thismonth.year - daterentedmonth.year) * 12 + (thismonth.month - daterentedmonth.month)
        self.nextpaymentdate = (datetime.strptime(self.daterented,"%m/%d/%y") + timedelta(30*(num_months+1))).strftime("%D")
    def changeduedate(self,newduedate):
        self.duedate=newduedate
    def changerent(self,newrent):
        self.rent=newrent
    def changedeposit(self,newdeposit):
        self.deposit=newdeposit
    def changelastkwh(self,newlastkwh):
        self.lastkwh=newlastkwh
    def changenkeys(self,newnkeys):
        self.nkeys=newnkeys
    def changehascar(self,newhascar):
        self.hascar=newhascar
    def changehasremote(self,newhasremote):
        self.hasremote=newhasremote
    def changestatus(self,newstatus):
        if newstatus=='renovation' or newstatus =='available':
            self.name=""
            self.number=""
            self.deposit=0
            self.nkeys=0
            self.daterented="0"
            self.duedate="0"
            self.nextpaymentdate="0"
        self.status=newstatus
        
class KWHPRICE(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    date=db.Column(db.String(120))
    price = db.Column(db.Integer)
    def __init__(self,date,price):
        self.date=date
        self.price=price


class Rent(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    date = db.Column(db.String(120))
    price = db.Column(db.Integer)
    apartment_id = db.Column(db.Integer,db.ForeignKey('apartment.id'))
    def __init__(self,date,price,apartmentid):
        self.date=date
        self.price=price
        self.apartment_id=apartmentid
class Electricity(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    date=db.Column(db.String(120))
    kwh = db.Column(db.Integer)
    price = db.Column(db.Integer)
    kwhprice = db.Column(db.Integer)
    apartment_id=db.Column(db.Integer,db.ForeignKey('apartment.id'))
    def __init__(self,date,kwh,price,kwhprice,apartmentid):
        self.date=date
        self.kwh=kwh
        self.price=price
        self.kwhprice=kwhprice
        self.apartment_id=apartmentid

def createapps():
    k = KWHPRICE(date="11/1/22",price=10000)
    db.session.add(k)
    apps=[]
    for x in range(1,6):
        for y in range(1,4):
            apps.append(f"{str(x)}/{str(y)}")
    for y in range(1,5):
        apps.append(f"6/{str(y)}")
    for x in apps:
        a = Apartment(appname=x,name="Dd",number="Aa",daterented="1/1/22",duedate="2/2/2",rent=124,deposit=214,lastkwh=241,nkeys=2,hascar="tes",hasremote="tes",status="occupied")
        db.session.add(a)
    db.session.commit()

@app.route("/")
def main():
    if loggedin:
        apartments=Apartment.query.all()
        dates = [(datetime.today()+ timedelta(x)).strftime("%D") for x in range(11)]
        print(dates)
        soonleaving = []
        soonrent=[]
        overduerent=[]
        for x in apartments:
            
            if x.duedate in dates:
                
                soonleaving.append(x)
            
            if x.nextpaymentdate in dates:
                if x not in soonleaving:
                    soonrent.append(x)
            else:
                try:
                    d=datetime.strptime(x.nextpaymentdate,"%m/%d/%y")
                    if d<datetime.today() and x not in soonleaving:
                        overduerent.append(x)
                except:
                    pass
        
            
        return render_template("main.html",apartments=apartments,soonleaving=soonleaving,soonrent=soonrent,overduerent=overduerent)
    else:
        return render_template("password.html")
@app.route("/verifypassword",methods=['POST','GET'])
def verify():
    inputpassword = request.form['password']
    if inputpassword==password:
        global loggedin
        loggedin=True
    return redirect("/") 
@app.route("/apartment/<int:id>")
def apartment(id):
    app = Apartment.query.get(id)
    return render_template("apartment.html",app=app)
@app.route("/makechanges",methods=['POST','GET'])
def makechanges():
    appid = request.form['appid']
    app = Apartment.query.get(appid)
    name = request.form['name']
    number=request.form['number']
    rent = request.form['rent']
    deposit=request.form['deposit']
    lastkwh = request.form['lastkwh']
    nkeys=request.form['nkeys']
    hascar = request.form['hascar']
    hasremote = request.form['hasremote']
    daterented = request.form['ddate']
    duedate=request.form['date']
    
    status = 'occupied'
    if name:
        app.changename(name)
    if number:
        app.changenumber(number)
    if rent:
        app.changerent(rent)
    if deposit:
        app.changedeposit(deposit)
    if lastkwh:
        app.changelastkwh(lastkwh)
    if nkeys:
        app.changenkeys(nkeys)
    if hascar:
        app.changehascar(hascar)
    if hasremote:
        app.changehasremote(hasremote)
    if status:
        app.changestatus(status)
    if daterented:
        daterented=(datetime.strptime(daterented[2:],"%y-%m-%d")).strftime("%D")
        app.changedaterented(daterented)
    else:
        app.changedaterented(datetime.today().strftime("%D"))
    if duedate:
        duedate=(datetime.strptime(duedate[2:],"%y-%m-%d")).strftime("%D")
        app.changeduedate(duedate)
    else:
        app.changeduedate((datetime.strptime(app.daterented,"%m/%d/%y")+timedelta(days=30)).strftime("%D"))
    
    db.session.commit()

    return redirect(f"/apartment/{appid}")
@app.route("/changerenter/<int:id>")
def changerenter(id):
    app = Apartment.query.get(id)
    return render_template("changerenter.html",app=app)

@app.route("/extend/<int:id>")
def extend(id):
    app = Apartment.query.get(id)
    app.changeduedate((datetime.strptime(app.duedate,"%m/%d/%y") + timedelta(30)).strftime("%D"))
    db.session.commit()
    return redirect(f"/apartment/{id}")
@app.route("/melectricity")
def melectricity():
    apps = Apartment.query.all()
    kwhprice = KWHPRICE.query.all()[-1].price
    for app in apps[:]:
        if len(app.ebills)>0:
            lastbill = app.ebills[-1]
            lastbillmonth = (datetime.strptime(lastbill.date,"%m/%d/%y")).strftime("%m")
            thismonth = datetime.today().strftime("%m")
            if lastbillmonth==thismonth:
                apps.remove(app)
    return render_template("electricity.html",apps=apps,kwhprice=kwhprice)
@app.route("/bill/<int:id>/<int:kwh>/<int:kwhprice>")
def bill(id,kwh,kwhprice):
    app=Apartment.query.get(id)
    

    prevbill = app.lastkwh
    e=Electricity(date=datetime.today().strftime("%D"),kwh=kwh,kwhprice=kwhprice,price=(kwh-prevbill)*kwhprice,apartmentid=id)
    db.session.add(e)
    app.changelastkwh(kwh)
    db.session.commit()
    return redirect("/melectricity")
@app.route("/changekwhprice",methods=['POST','GET'])
def changekwhprice():
    newkwhprice=request.form['kwhprice']
    k = KWHPRICE(datetime.today().strftime("%D"),newkwhprice)
    db.session.add(k)
    db.session.commit()
    return redirect("/melectricity")
@app.route("/freeapp/<int:id>")
def freeapp(id):
    app = Apartment.query.get(id)
    app.changestatus('available')
    db.session.commit()
    return redirect(f"/apartment/{str(id)}")
@app.route("/makerentpayment/<int:id>")
def makerentpayment(id):
    app = Apartment.query.get(id)
    app.nextpaymentdate = (datetime.strptime(app.nextpaymentdate,"%m/%d/%y") + timedelta(days=30)).strftime("%D")
    db.session.commit()
    return redirect(f"/apartment/{str(id)}")
@app.route("/changerent/<int:id>",methods=['POST','GET'])
def changerent(id):
    app = Apartment.query.get(id)
    newrent = request.form['newrent']
    app.changerent(int(newrent))
    db.session.commit()
    return redirect(f"/apartment/{str(id)}")
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)