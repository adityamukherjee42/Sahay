import streamlit as st
import pymongo

client=pymongo.MongoClient('mongodb+srv://admin:abcde12345@trial.fk9mp.mongodb.net/test')

btypelist = ['Mediclaim','Uninsured','Insured']

mydb=client['trial']
formtable = mydb.form

st.header('Patient Feedback Form')

name = st.text_input("Enter patient name")
pid = st.text_input("Patient Id")
age = st.number_input("Enter age:")
dept= st.text_input("Enter Dept.")
admit = st.text_input("Enter admission date")
dis = st.text_input("Enter discharge date")
cost = st.number_input("Enter Cost:")
btype = st.selectbox("Choose Type of bill payment",options=btypelist)
readm = st.selectbox("Readmission?",options=['No','Yes'])
days = st.text_input("Number of Days stayed")
wt = st.slider("Waiting Time",min_value=0,max_value=120,step=5)

if st.button('Submit'):
    addinfo = {
        'name': name,
        'pid': pid,
        'dept': dept,
        'admit': admit,
        'dis': dis,
        'cost': cost,
        'btype': btype,
        'readm' : readm,
        'days' : days,
        'wtime' : wt
    }

    formtable.insert_one(addinfo)

