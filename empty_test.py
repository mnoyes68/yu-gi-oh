import numpy as np

mylist = []
x = np.zeros((2,20))
print "Array"
print x
print "Reshaped Array"
print x.reshape((1, -1))
for i in range(10):
	mylist.append(x.reshape((1, -1)))
print mylist