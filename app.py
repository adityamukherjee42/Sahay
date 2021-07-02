from flask import Flask, render_template, url_for, request, session, redirect
import pandas as pd
import json
import plotly
import plotly.express as px
import pymongo
import bcrypt

global date
global padd
global pdis



client=pymongo.MongoClient('mongodb+srv://admin:abcde12345@trial.fk9mp.mongodb.net/test')



mydb=client['trial']
dailyinfo = mydb.dailyinfo
ptable  = mydb.ptable

maintable = mydb.maintable

formtable = mydb.form

users = mydb.logtrial

dlist=list()
plist=list()
alist=list()
glist = list()
for i in maintable.find():
    dlist.append(i['date'])
    plist.append(int(i['padd']))
    glist.append('Inpatients')
    dlist.append(i['date'])
    plist.append(int(i['pdis']))
    glist.append('Outpatients')
    staffsize = i['staff']

wtime=0
k=0
pdict = dict()
cost=0
mcount=0
icount=0
ucount=0
for j in formtable.find():
    pdict[j['pid']] = {j['dept']:j['wtime']}
    wtime+=int(j['wtime'])
    cost+=int(j['cost'])
    if(j['btype']=='Mediclaim'):
        mcount+=1
    if (j['btype'] == 'Insured'):
        icount += 1
    if (j['btype'] == 'Uninsured'):
        ucount += 1

    k+=1

avgwtime=wtime/k
avgcost=cost/k

agg_result = formtable.aggregate([
   {
      "$group": {
         "_id": '$dept',
         "Avgwtime": {
            "$avg": "$wtime"
         }
      }
   }
])
d = dict()
cc = 2
keys = []
vals = []
for i in agg_result:
   for j in i:
      if (cc % 2 == 0):
         keys.append(i[j])
      else:
         vals.append(i[j])
      cc += 1

app = Flask(__name__)
@app.route('/home')
def notdash():



   df = pd.DataFrame({
      "Day": dlist,
      "Patients": plist,
      "Group": glist
   })
   df_1 = pd.DataFrame({
      "Depatment": keys,
      "Avg Waiting time": vals,
   })
   fig = px.bar(df, x="Day", y="Patients", color="Group",barmode="group",height=280,title='Patient Admission History')
   fig.update_layout({
      'plot_bgcolor': 'rgba(0, 0, 0, 0)',
      'paper_bgcolor': 'rgba(0, 0, 0, 0)',
   })
   fig.update_yaxes(tick0=200)
   fig1 = px.bar(df_1, x="Avg Waiting time", y="Depatment", orientation='h',title='Avg Waiting Time By Division',height=480,width=450)
   fig1.update_layout({
      'plot_bgcolor': 'rgba(0, 0, 0, 0)',
      'paper_bgcolor': 'rgba(0, 0, 0, 0)',
   })


   graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
   graphJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
   return render_template('notdash.html', graphJSON=graphJSON,column_names=df.columns.values, row_data=list(df.values.tolist()),
                           link_column="", zip=zip,graphJSON1=graphJSON1,avgwtime=avgwtime,avgcost=avgcost,k=k,staffsize=staffsize)

@app.route('/hospitalperformence')
def hospitalperform():
   df = pd.DataFrame({
      "Day": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
      "Percentage": [2, 19,14,11,20,10,4, 11, 5,4]
   })
   fig = px.area(df, x="Day", y="Percentage",height=350,width=420,title="Patients to their percentage of stay")
   fig.update_xaxes(showgrid=False)
   fig.update_yaxes(showgrid=False)
   fig.update_layout({
      'plot_bgcolor': 'rgba(0, 0, 0, 0)',
      'paper_bgcolor': 'rgba(0, 0, 0, 0)',
   })
   fig.add_vline(x=4, line_width=3, line_dash="dash", line_color="green",fillcolor="red")
   graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
   df_1 = pd.DataFrame({
      "AGE": ["0-1", "1-17", "18-44", "45-64", "65-84","84+"],
      "Avg cost": [4500,8200,7200,12100,12300,9600],
   })
   fig1 = px.bar(df_1, y='Avg cost', x='AGE',text='Avg cost',title='Avg Treatment cost(by Age group)',height=550,width=420)
   fig1.update_traces(texttemplate='%{text:.2s}', textposition='outside')
   fig1.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
   fig1.update_layout({
      'plot_bgcolor': 'rgba(0, 0, 0, 0)',
      'paper_bgcolor': 'rgba(0, 0, 0, 0)',
   })
   fig1.update_xaxes(showgrid=True,zeroline=True)
   fig1.update_yaxes(tickprefix="$",showgrid=False,zeroline=False)
   graphJSON1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
   df_2 = pd.DataFrame({
      "Quater": ["Q1", "Q2", "Q3"],
      "Rate": [10, 35, 40]
   })

   fig2 = px.bar(df_2, y='Rate', x='Quater', title='Readmision Rate', height=350,
                 width=420)
   fig2.add_hline(y=28.3, line_width=3, line_dash="dash")
   fig2.update_layout({
      'plot_bgcolor': 'rgba(0, 0, 0, 0)',
      'paper_bgcolor': 'rgba(0, 0, 0, 0)',
   })
   fig2.update_xaxes(showgrid=False)
   fig2.update_xaxes(showgrid=False)
   graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
   print(str(int((ucount/k)*100))+str(int((icount/k)*100))+str(int((mcount/k)*100)))
   df_3 = pd.DataFrame({
      "Payer": ["Uninsured", "Insured", "Mediclaim"],
      "Percentage": [int((ucount/k)*100),int((icount/k)*100),int((mcount/k)*100)]
   })
   fig3 = px.pie(df_3, values='Percentage', names='Payer',title='Stays by Payer',height=550,width=420)
   fig3.update_layout({
      'plot_bgcolor': 'rgba(0, 0, 0, 0)',
      'paper_bgcolor': 'rgba(0, 0, 0, 0)',
   })
   fig3.update_layout(legend=dict(
      yanchor="top",
      y=1.01,
      xanchor="left",
      x=0.70
   ))
   graphJSON3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
   df_4 = pd.DataFrame({
      "Quarter": ["Quater1", "Quater1", "Quater2", "Quater2", "Quater3", "Quater3"],
      "Patients": [0.3, 1, 0.8, 0.5, 0.6, 1.2],
      "Group": ["Ventilator Associated Pneumonia", "Surgery acquired", "Ventilator Associated Pneumonia", "Surgery acquired", "Ventilator Associated Pneumonia", "Surgery acquired" ]
   })
   fig4 = px.bar(df_4, x="Quarter", y="Patients", color="Group",color_discrete_map={
        'Ventilator Associated Pneumonia': 'Blue',
        'Surgery acquired': 'Turquoise'
    },barmode="group",height=560,width=420,title='Hospital-Acquired Infections')
   fig4.update_layout({
      'plot_bgcolor': 'rgba(0, 0, 0, 0)',
      'paper_bgcolor': 'rgba(0, 0, 0, 0)',
   })
   fig4.update_xaxes(ticksuffix="%",showgrid=False)
   fig4.update_xaxes(showgrid=False)
   fig4.update_layout(legend=dict(
      yanchor="bottom",
      y=-0.25,
      xanchor="left",
      x=0.01
   ))
   graphJSON4 = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
   return render_template("performence.html",graphJSON=graphJSON,graphJSON1=graphJSON1,graphJSON2=graphJSON2,
                          graphJSON3=graphJSON3,graphJSON4=graphJSON4)
@app.route('/dentry',methods=['POST','GET'])
def dentry():
    if request.method == 'POST':
        date = request.form['date']
        padd = request.form['padd']
        pdis = request.form['pdis']
        staff = request.form['sstr']
        nurse = request.form['nstr']
        had = request.form['had']

        addinfo = {
            'date': date,
            'padd': padd,
            'pdis': pdis,
            'staff': staff,
            'nurse': nurse,
            'had': had
        }

        maintable.insert_one(addinfo)


        return redirect(url_for('dentry'))
    else:
        return render_template("dentry.html")


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    #users = mongo.db.users
    login_user = users.find_one({'name': request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
            #session['username'] = request.form['username']
            return redirect(url_for('notdash'))


    return 'Invalid username/password combination'


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        #users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name': request.form['username'], 'password': hashpass})
            #session['username'] = request.form['username']
            return redirect(url_for('notdash'))

        return 'That username already exists!'

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
