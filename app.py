#from sklearn.preprocessing import StandardScaler
#import matplotlib
#import matplotlib.pyplot as plt
#import seaborn as sns
#from sklearn.preprocessing import StandardScaler
#from sklearn.datasets.samples_generator import make_blobs
from sklearn.metrics import silhouette_score 
#from sklearn import metrics
#import numpy as np 
import csv
from sklearn.cluster import DBSCAN
from statistics import mean
import pandas as pd
pd.options.mode.chained_assignment = None
from flask import Flask
from flask import render_template, url_for, request

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/predict/')
def predict():
    return render_template("predict.html")

@app.route('/output',  methods=['POST'])
def output():

    hoarding_df = pd.read_csv('/Users/Akshat/Hoarding_Rate_Evaluator/env/Dataset/Hoarding Rate Evaluator1.csv')
    X_numerics = hoarding_df[['Size of Billboard','Literacy Rate', 'Male','Female','Young', 'Middle Age', 'Old Age', 'Poor', 'Middle Class', 'Rich']]

    #asking for input from the customer
    product = request.form.get('product_type')
    budget = int(request.form.get('budget')) 
    lit_rate = request.form.get('lit_rate')
    age = int(request.form.get('age'))
    eco_rate = int(request.form.get('eco_rate'))
    gender = int(request.form.get('gender'))
    
    mean_size = round(mean(X_numerics['Size of Billboard']),2)
    min_lit_rate = min(X_numerics['Literacy Rate'])
    mean_lit_rate = round(mean(X_numerics['Literacy Rate']),2)

    x_data = ['X','Y', mean_size, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    if lit_rate == 'y':
        x_data[3] = mean_lit_rate
    elif lit_rate == 'n':
        x_data[3] = min_lit_rate

    if gender == 1:
        x_data[4] = 55
        x_data[5] = 45  
    elif gender == 2:
        x_data[4] = 48
        x_data[5] = 52    
    elif gender == 3:
        x_data[4] = 50 
        x_data[5] = 50    

    if age == 1:
        x_data[6] = 70 
        x_data[7] = 20
        x_data[8] = 10
    elif age == 2:
        x_data[6] = 20 
        x_data[7] = 60
        x_data[8] = 20
    elif age == 3:
        x_data[6] = 10 
        x_data[7] = 20
        x_data[8] = 70
    elif age == 4:
        x_data[6] = 33.33 
        x_data[7] = 33.34
        x_data[8] = 33.33

    if eco_rate == 1:
        x_data[9] = 70 
        x_data[10] = 20
        x_data[11] = 10
    elif eco_rate == 2:
        x_data[9] = 25
        x_data[10] = 50
        x_data[11] = 25
    elif eco_rate == 3:
        x_data[9] = 10 
        x_data[10] = 20
        x_data[11] = 70
    elif eco_rate == 4:
        x_data[9] = 33.33 
        x_data[10] = 33.34
        x_data[11] = 33.33

    filename = 'Dataset/Hoarding Rate Evaluator1.csv'

    f = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        f = next(reader)
        data = [[field] for field in f]
        for row in reader:
            for i,r in enumerate(row):
                data[i].append(r)

    hoarding_df = pd.read_csv('/Users/Akshat/Hoarding_Rate_Evaluator/env/Dataset/Hoarding Rate Evaluator1.csv')
    X_numerics = hoarding_df[['Size of Billboard','Literacy Rate', 'Male','Female','Young', 'Middle Age', 'Old Age', 'Poor', 'Middle Class', 'Rich']]


    #adding x_data into X_numerics and data
    X_numerics.loc[X_numerics.index.max() + 1] = x_data[2:12]
    for i in range(13):
        data[i].append(x_data[i])

    #running the DBSCAN algorithm
    sil_score = [] 
    DBS_clustering = DBSCAN(45, 8).fit(X_numerics)
    sil_score.append(silhouette_score(X_numerics, DBS_clustering.labels_))
    #print("\nSilhouette score: ",sil_score)

    #Creating Labels
    labels = DBS_clustering.labels_

    #fetching location according to the labels
    dct = {}
    for i in range(len(labels)):
        if labels[i] in dct.keys():
            if data[0][i+1] not in dct[labels[i]]:
                dct[labels[i]].append(data[0][i+1])
            else:
                continue
        else:
            dct[labels[i]] = []
            dct[labels[i]].append(data[0][i+1])

    #Selecting the cluster which has x_data
    final_dct = {'Location': [],'Address': [],'Billboard_Size':[],'Lit_rate':[],'male': [],'female':[],'young':[],'middle-aged':[],'old':[],'poor':[],'middle':[],'rich':[],'Vehicle_Count':[],'Cost':[],'Link':[]}
    for k,v in dct.items():
         if 'X' in dct[k]:
             for i in dct[k]:
                 final_dct['Location'].append(i)

    #fetching other info for all hoardings in the targeted cluster
    final_dct['Location'].remove('X')

    for i in range(len(final_dct['Location'])):
        for j in range(1,len(data[0])):
            if final_dct['Location'][i] == data[0][j]:
                final_dct['Address'].append(data[1][j])
                final_dct['Billboard_Size'].append(int(data[2][j]))
                final_dct['Lit_rate'].append(float(data[3][j]))
                final_dct['male'].append(float(data[4][j]))
                final_dct['female'].append(float(data[5][j]))
                final_dct['young'].append(float(data[6][j]))
                final_dct['middle-aged'].append(float(data[7][j]))
                final_dct['old'].append(float(data[8][j]))
                final_dct['poor'].append(float(data[9][j]))
                final_dct['middle'].append(float(data[10][j]))
                final_dct['rich'].append(float(data[11][j]))
                final_dct['Cost'].append(int(data[12][j]))
                final_dct['Vehicle_Count'].append(int(data[13][j]))
                final_dct['Link'].append(data[14][j])            
            
    #ranking the hoardings based on size,vehcile count, cost  
    df = pd.DataFrame(final_dct)
    df = df[df['Cost'] <= budget]
    df['ranking'] = df.Billboard_Size * 0.3 + df.Vehicle_Count * 0.4 + df.Lit_rate * 0.2 + (df.male//df.female) * 0.1 
    df = df.sort_values(by ='ranking', ascending=False)
    df = df.head(8)  

    result_list = df[['Location','Address','Billboard_Size','Cost','Vehicle_Count','Link']].values.tolist()    
 
    return render_template("output.html", result_list=result_list)
    
if __name__ == "__main__":
    app.run()