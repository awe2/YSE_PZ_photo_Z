from django_cron import CronJobBase, Schedule
from YSE_App.models.transient_models import *
from YSE_App.common.utilities import GetSexigesimalString
from YSE_App.common.alert import IsK2Pixel, SendTransientAlert
from YSE_App.common.thacher_transient_search import thacher_transient_search
from YSE_App.common.tess_obs import tess_obs
from YSE_App.common.utilities import date_to_mjd
import datetime

import numpy as np
import pandas
import os
import pickle

from sklearn.ensemble import RandomForestRegressor
from SciServer import Authentication, CasJobs 

class YSE(CronJobBase):

	RUN_EVERY_MINS = 480

	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'YSE_App.data_ingest.Photo_Z.YSE'

	def do(self,user='awe2',password='StandardPassword',path_to_model='YSE_App\\data_ingest\\RF_model.sav'):
		"""
		Predicts photometric redshifts from RA and DEC points in SDSS

		An outline of the algorithem is:

		first pull from SDSS u,g,r,i,z magnitudes from SDSS; 
			should be able to handle a list/array of RA and DEC

		place u,g,r,i,z into a vector, append the derived information into the data array

		predict the information from the model

		return the predictions in the same order to the user
		
		Note: N <= 1000 because of CAS; could do this in batches over 1000

		inputs:
			Ra: list or array of len N, right ascensions of target galaxies in decimal degrees
			Dec: list or array of len N, declination of target galaxies in decimal degrees
			Search: float, arcmin tolerance to search for the object in SDSS Catalogue
			model: str, filepath to saved model for prediction
		
		Returns:
			predictions: array of len N, photometric redshift of input galaxy

		"""
		#save time b/c the other cron jobs print a time for completion
		
		#final will have something like:
		#transient_list = Transients.objects.filter(photometric_redshift=None & tags.galactic_host=True)  
		
		#but for now lets do:
		nowdate = datetime.datetime.utcnow() - datetime.timedelta(100)
		transient_list = Transient.objects.filter(created_date__gt=nowdate)
		#transient_list = Transients.objects.filter()
		#print('Number of test transients:', len(transient_list))
		RA=[]
		DEC=[]
		#print('debug first for loop')
		for transients in transient_list:
		
			RA.append(transients.RADecimalString()) #get list of RA and DEC that need
			DEC.append(transients.DecDecimalString())
		#print('exited for loop')
		#print('how many RA and DEC?: ',len(RA),len(DEC))
		
		
		#okay now were ready to continue as planned	
		N=len(RA)
		
		#Check to make sure N < 1000; else we need to batch this job to CAS
		#something
		#for first pass lets just take first 1000 
		if N > 1000:
			RA = RA[0:999]
			DEC = DEC[0:999]
		N = len(RA)
		
		Ra = np.array(RA)
		Dec = np.array(DEC)
		#print('test conditional, now how many are in N?',len(RA),N)
		#print(RA[0],DEC[0])
		#First take RA and DEC and get u,g,r,i,z
		hold=[]
		#j=0 #to debug
		for val in range(N): #if this works, maybe find a way to vectorize?
			#if j == 0:
				#print('entered second for loop')
				#print(str(val))
				#print(str(Ra[val]))
				#print(str(Dec[val]))
				#print('({},{},{}),|'.format(str(val),str(Ra[val]),str(Dec[val])))
			string = '({},{},{}),|'.format(str(val),str(Ra[val]),str(Dec[val]))
			#if j == 0:
			#	print(string)
			hold.append(string)
			#if j ==0:
			#	print(hold)
				j=1
		#print('exited second for loop')
		#print('length of held strings: ', len(hold))
		sql = "CREATE TABLE #UPLOAD(|id INT PRIMARY KEY,|up_ra FLOAT,|up_dec FLOAT|)|INSERT INTO #UPLOAD|   VALUES|"
		for data in hold:
			sql = sql + data
		#there is a comma that needs to be deleted from the last entry for syntax to work
		sql = sql[0:(len(sql)-2)] + '|'
		#append the rest to it
		sql = sql + "SELECT|p.u,p.g,p.r,p.i,p.z|FROM #UPLOAD as U|OUTER APPLY dbo.fGetNearestObjEq((U.up_ra),(U.up_dec),1) as N|LEFT JOIN Galaxy AS p ON N.objid=p.objid"
		#change all | to new line
		sql = sql.replace('|','\n')
		#print('successfully built sql query')
		Authentication.login(user,password)
		#print('successfully used authentication')
		job = CasJobs.executeQuery(sql,'DR15','pandas')
		#print('activated CAS') 
		#job is a pandas dataframe with ra,dec and u,g,r,i,z; First thing we can do is append new rows that are the colors
		job['u-g']= job['u'].values - job['g'].values
		job['g-r']= job['g'].values - job['r'].values
		job['r-i']= job['r'].values - job['i'].values
		job['i-z']= job['i'].values - job['z'].values
		job['u_over_z']= job['u'].values / job['z'].values
		#now feed to a RF model for prediction
		X = job.values
		#print('shape of test array: ', np.shape(X))
		model = pickle.load(open(path_to_model, 'rb'))
		#print('loaded model')
		#Need to deal with NANs now since many objects are outside the SDSS footprint, later models will learn to deal with this
		#ideas: need to retain a mask of where the nans are in the row
		mask = np.invert((job.isna().any(1).values)) #true was inside SDSS footprint
		#also will want this mask in indices so we can insert the predicted data correctly
		indices=[]
		for i,val in enumerate(mask):
			if val == True:
				indices.append(i)
		predictions = model.predict((X[mask,:]))
		#make nan array with size of what user asked for
		return_me = np.ones(N)*np.nan
		#now replace nan with the predictions in order
		return_me[indices] = predictions
		#print(return_me)
		print('time taken:', datetime.datetime.utcnow() - nowdate)
		#and then probably something like Transients.photometrc_redshift = predictions
		return(return_me)
