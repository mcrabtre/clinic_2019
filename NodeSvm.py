import numpy as np
import pandas as pd
import random
import time
import matplotlib.pyplot as pt
timelog = True
isImported = True #set to false to run immediately

### SVM Gradient Descent. Takes training vector x and lables y to perform T iterations. 
	###lambda and eta ajust the rate of convergence.
	### Outputs SVM vector w. And vector of loss functions fn for convergence analysis
		### would like fn to be an opaque variable to call only if desired
def svm(x,y,w,eta,lam,tau):
	D, n = np.shape(x)
	#W = np.zeros(tau,n)
	fn = np.zeros(tau)
	for k in range( 0, int(tau)):
		dfn = np.zeros(n)
		for j in range(0 , D):
			wT = w.transpose()
			if (1-y[j]*np.dot(wT, x[j]))<0:
				max = 0
			else:
				max = 1-y[j]*np.dot(wT, x[j])
			fn[k] += ((lam/2)*np.dot(w, wT)**2 + (max**2)/2)/D
			for i in range(0,n):
				dfn[i] += (lam*w[i]-(y[j]*x[j,i])*max)/D
		w = w - eta*dfn
	return w, fn

###read the converts a read .csv matrix into useable arrays. capable of variable lengths
	### reads numPoint values out of dataset data, Converts values to be useable in SVM,
	### and outputs them in the vectors x and y.
		### Can skip the first offset values or select only the values found in case but
		### default is read all values starting at 0
def pandaRead(numPoints, data, offset=0, case=None):
	pointstart=offset
	pointend = pointstart + numPoints

	x = np.array(data[pointstart:pointend,1:])/255
	y = np.array(data[pointstart:pointend,0])
	
	### Select particular values in case
	if case!=None:
		ttab = np.zeros(numPoints, dtype=bool)
		points = np.size(case)
		for i in range(0,points):
			ttab = ttab + (y==case[i])
		x = x[ttab,]
		y = y[ttab]
	### adjust y values to 1 if even and -1 if odd.
	D,_ = np.shape(x)
	for i in range(0, D):
		
		if y[i]%2 == 0:
			y[i] = 1
		else:
			y[i] = -1
			
	return x,y

### Dot products the w vector with the test data. Noralizes the value to 1,-1 and 
### compares with the actual lable
		### capable of showing misclassified images if fig is True. 
		###May error if too many images attempted
def testW(w,x,y, fig=False):
	#h should be approx y
	D,_ = np.shape(x)
	h = np.dot(x,w)
	h[h>0] = 1
	h[h<1] = -1
	
	errcount = 0
	for i in range(0, D):
		if y[i] != h[i]:
			errcount += 1
		### This shows the number that is misclassified if fig is true
		if (y[i] != h[i]) & fig:
			pt.figure(i)
			z = np.array(x[i])
			z.shape = [28,28]
			pt.imshow(255 - z, cmap='gray')
			
	accuracy = (1-errcount/D)*100
 
	return accuracy

### w is the weight, N is the node number. tau is the number of local uptdates 
	### before the global update. D is the number of data points. 

def NodeSVM(w, N, tau=10, D=100, eta=.01, lam=1):
	if timelog:
		starttime=time.time()	
		lasttime = starttime
	runtest = False
	datasize =D
	trainsize = 0
	if runtest:
		trainsize = 1000
	
	###Used for reading and testing .csv files.
		
	filepath = r"all/train.csv"
	data = pd.read_csv(filepath, skiprows=(N*(D+trainsize)), nrows=(datasize+trainsize)).values
	sum = 0 
	
	#If testing particular values set case here.
	
	x, y = pandaRead(datasize, data ,0)
	if runtest:
		xt, yt = pandaRead(trainsize, data, datasize)
	print("Data samples: %i, Iterations: %i" %(datasize,tau))
	if timelog:
		unpacktime = time.time() - lasttime
		lasttime = time.time()
		print("--- Unpacking %s seconds ---"%unpacktime)
	
	
	w, fn = svm(x,y,w,eta,lam,tau)
	#print(w)

	### Run the test of the vector 
	if runtest:
		a = testW(w, xt,yt)
		print("accuracy is: ", a)

	if timelog:
		endtime= time.time() -lasttime
		lasttime = time.time()
		print("--- Computation %s seconds ---" %(endtime))
	
		totaltime = time.time() - starttime
		print("--- Total %s seconds ---" %(totaltime))
	
	return w, fn
if not isImported:    
	w = np.zeros(784)
	N = 0
	w,fn = NodeSVM(w,N)
###Display a color map of W
#print("w0 = ",w[0])
#pt.figure(1)
#w.shape = [28,28]
#pt.imshow(w, cmap='seismic')
#pt.show()
