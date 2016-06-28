'''
Given a cohort, feature list, and platform, this program draws a clustered heatmap  
INPUT 1: cohort ID
INPUT 2: feature list , currently in a file with one feature per row
INPUT 3: platform
Example:  python heatmapForWebApp1.py 2 testFeatureList.txt mRNA_UNC_HiSeq_RSEM
NOTE: The idea is for a user to be able to select a cohort and a set of features from the WebApp, and then to be able to view a clustered heatmap for the corresponding data.

'''
import sys
import string
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import GoogleCredentials
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np 

def getData(bigqueryService,cohortID, featureFilename, platform):
    
    #read in feature list, e.g from a file that contains 1 feature name per row
    featureFileHandle = open(featureFilename,"r")	
    featureList = featureFileHandle.read().strip().split('\n')
    
    projectID = 'isb-cgc'	
    ds = 'tcga_201510_alpha'
   
    table = '['+projectID+':'+ds+'.'+platform+']'
    print table

    if platform.startswith('mRNA'):
        featureColumn = 'HGNC_gene_symbol'
        valueColumn = 'normalized_count'
    elif platform=='miRNA_expression' :
        featureColumn='mirna_id'
        valueColumn='normalized_count'
    elif platform=='DNA_Methylation_betas':
        featureColumn='Probe_Id'
        valueColumn='Beta_Value'


    try:
	queryRequest = bigqueryService.jobs()
        sqlQuery= ' '.join(['SELECT SampleBarcode,',featureColumn,',',valueColumn,'FROM', table, 'WHERE SampleBarcode IN',
                        '(SELECT sample_barcode FROM [isb-cgc:dev_deployment_cohorts.dev_test_cohorts_2] WHERE cohort_id=',cohortID,')',
                        'AND',featureColumn,'IN (',','.join(["'"+i+"'" for i in featureList]),')'])
        print sqlQuery
   	body={"query":sqlQuery} 
        queryResponse = queryRequest.query(projectId=projectID,body=body).execute()	

	return queryResponse

    except HttpError as err:
	print('Error: {}'.format(err.content))
        raise err 	  

if __name__ == '__main__':

    # Grab the application's default credentials from the environment.
    credentials = GoogleCredentials.get_application_default()
    # Construct the service object for interacting with the BigQuery API.
    bigqueryService = build('bigquery', 'v2', credentials=credentials)

    cohortID = sys.argv[1]
    featureFilename = sys.argv[2]
    platform = sys.argv[3]
    
    bqResponse = getData(bigqueryService,cohortID, featureFilename, platform)
    
    dataToPlot = [[row['f'][0]['v'],row['f'][1]['v'],row['f'][2]['v']] for row in bqResponse['rows']]
    dataToPlot = pd.DataFrame.from_dict(dataToPlot)
    dataToPlot.columns = ['SampleBarcode','Feature','Values']	
    dataToPlot[['Values']] = dataToPlot[['Values']].apply(pd.to_numeric)
    dataToPlot = dataToPlot.pivot_table(index='Feature',columns='SampleBarcode',values='Values',aggfunc=np.mean)	
    	 
    #data range? normalization?
    ax = sns.clustermap(dataToPlot,xticklabels=False,yticklabels=False,robust=True)
    ax.savefig('test.png')
    #print ax
    print ax.dendrogram_row.reordered_ind
    print ax.dendrogram_col.reordered_ind 
    #sns.plt.show() 	
