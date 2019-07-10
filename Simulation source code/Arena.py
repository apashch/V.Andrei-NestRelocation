import numpy as np
#import nibabel as nib # NIFTI images processing
import scipy.misc # image export
import imageio
import scipy.stats as stats
from math import log, sin, cos


class Arena:

	def __init__(self, type):
		self.type = type
		self.arFile, self.origin = getTypeFile(type)
		self.nestDim = self.loadField(self.arFile)[2:]
		

	def reset(self, field = "c0d0"):
		self.arFile, self.origin = getTypeFile(field)
		self.nestDim = self.loadField(self.arFile)[2:]
	
	def getNestDim(self):
		#print(self.nestDim)
		return self.nestDim


	def loadField(self, filename):
		self.field = np.load(filename)
		self.dim = self.field.shape
		self.dimX = self.dim[0] # x-dimension of the whole area
		self.dimY = self.dim[1] # y-dimension of the whole area
		self.minY = np.argwhere(sum(self.field) > 0)[0][0]  # min y-coordinate of the avaliable nest
		self.maxY = np.argwhere(sum(self.field) > 0)[-1][0] # max y-coordinate of the avaliable nest
		self.minX = np.argwhere(sum(self.field.transpose()) > 0)[0][0]   # min x-coordinate of the avaliable nest
		self.maxX = np.argwhere(sum(self.field.transpose()) > 0)[-1][0]  # max x-coordinate of the avaliable nest
		#print('x:', self.minX, self.maxX, 'y:', self.minY, self.maxY)

		return self.dim, self.field, self.maxX-self.minX, self.maxY-self.minY

	def getFieldVal(self, x_or_tuple, y = None, default = 0):
		try:
			if y == None:
				#print(round(x_or_tuple[0]), round(x_or_tuple[1]))
				return self.field[int(round(x_or_tuple[0])), int(round(x_or_tuple[1]))]
			else:
				#print(round(x_or_tuple), round(y))
				return self.field[int(round(x_or_tuple)), int(round(y))]
		except IndexError:
			#print("WARNING! FIELD VALUE OUTSIDE OF DEFINED ARENA REQUESTED; DEFAULT VALUE OF {} RETURNED INSTEAD".format(default))
			return default

	def setFieldVal(self, val, x_or_tuple, y = None):
		try:
			if y == None:
				self.field[int(round(x_or_tuple[0])), int(round(x_or_tuple[1]))] = val
			else:
				self.field[int(round(x_or_tuple)), int(round(y))] = val
		except IndexError:
			pass

	def Xmin(self):
		return self.minX

	def Xmid(self):
		return (self.maxX + self.minX) // 2



	def getStartPos(self, pars, dist = 'e'):
		try:
			dist = pars["INIT_DISTR"]
		except KeyError:
			pass
		shift = pars["SHIFT"]

		mu, sigma = log(100), 0.9 # parameters for lognormal distr
		positions = np.empty((2, pars['NUM']), dtype = int) # array with NUM columns; j-th in the end represents starting (x, y) of j-th ant
		#positions[1] = [np.random.choice((np.nonzero(self.field[positions[0][i]])[0])) for i in range(pars['NUM'])]

		if dist == 'e':
			lower = 0 # left bound of exponential x-distribution
			upper = self.maxX - self.origin[0] - 5 # length of non-truncated region ofexponential x-distr
			scale = pars["ESCALE"]
			X = stats.truncexpon(b = (upper-lower)/scale, loc=lower, scale=scale)
			positions[0] = X.rvs(pars['NUM']) + self.origin[0]
			def pdf(t):
				return 0;

		elif dist == 'ls':
			i = 0
			while i < pars['NUM']:
				s = self.origin[0] - shift + np.random.lognormal(mu, sigma)
				while s > self.maxX - 5 or s < self.minX + 5:
					s = self.origin[0] - shift + np.random.lognormal(mu, sigma)
				positions[0][i] = int(s)
				i += 1
			def pdf(t): 
				# np.random.lognormal pdf taken from documenatation
				arr = [0 if (x < self.origin[0] - shift) or (x > self.maxX - 5) else np.exp(-(np.log(x) - mu)**2 / (2 * sigma**2)) / (x * sigma * np.sqrt(2 * np.pi))  for x in t]
				return arr

		elif dist == 'rs': 
			i = 0
			while i < pars['NUM']:
				s = self.maxX - np.random.lognormal(mu, sigma)
				while s > self.maxX - 5 or s < self.minX + 5:
					s = self.maxX - np.random.lognormal(mu, sigma)
				positions[0][i] = int(s)
				i += 1
			def pdf(t):
				x = self.maxX - t
				return np.exp(-(np.log(x) - mu)**2 / (2 * sigma**2)) / (x * sigma * np.sqrt(2 * np.pi)) 

		elif dist == 'u':
			positions[0] = self.origin[0] - shift + np.random.randint(self.maxX - self.origin[0] + shift - 5, size = pars['NUM'])
			def pdf(t):
				arr = [0 if (x < self.origin[0] - shift) or (x > self.maxX - 5) else 1/(self.maxX - self.origin[0] + shift - 5) for x in t]
				return arr


		#for i in range(pars['NUM']):
			#print(dist, positions[0][i])
			#print('\n')

		positions[1] = [np.random.choice((np.nonzero(self.field[positions[0][i]])[0])) for i in range(pars['NUM'])]
		return positions.transpose(), pdf #return as list of coordinate pairs and return a the pdf function

	def getInter(self, x, y, interrad):
		neighbours = np.unique(self.field[x - interrad : x + interrad + 1, y - interrad : y + interrad + 1])
		setIntNeigh = {int(i) for i in neighbours}
		return setIntNeigh

	def fillbodyspace(self, antID, headX, headY, direction, length, width):
		if length == 0 and width == 0:
			return -1
		yy, xx = np.mgrid[-width//2 : width//2+1, -length : 1]
		rot =  np.array(((np.cos(direction), -np.sin(direction)),  (np.sin(direction),  np.cos(direction))))
		xxr, yyr = np.zeros_like(xx), np.zeros_like(yy)
		for i, j, ir, jr in np.nditer([xx, yy, xxr, yyr], op_flags=[['readonly'], ['readonly'], ['readwrite'], ['readwrite']]):
			ir[...],  jr[...] = np.matmul(np.array([i, j]), rot)[0]+headX, np.matmul(np.array([i, j]), rot)[1]+headY
			if self.getFieldVal(int(ir), int(jr))  != 0:
				self.setFieldVal(antID, int(ir), int(jr))
		return (xxr, yyr)

		# body = np.zeros((length+1, width+1, 2), dtype = int)
		# for delY in range(-width//2, width//2+1):
		# 	for delX in range(-length, 1):
		# 		body[delX-1][delY+width//2] = [int(round(headX + delX*cos(direction))), int(round(headY + delY*sin(direction)))]
		# for u in np.unique(body):
		# 	self.setFieldVal(antID, u)
		# print(np.unique(body, axis = 0))
		# print("#########################################")
		# return body


def getTypeFile(type):
	fieldfolder = 'fields_processed/'
	translator = {
				#old_set, ORIGIN = (1100, 550)
				'4o_2_4o_old' : ("4ch_2_4ch_Field.npy", (1100, 550)),
				'3o_2_3o_old' : ("3ch_2_3ch_Field.npy", (1100, 550)),
				'4c_2_4c_old' : ("4chcl_2_4chcl_Field.npy", (1100, 550)),
				'3o_2_4o_old' : ("3ch_2_4ch_Field.npy", (1100, 550)),
				'1sq_2_1sq'	  : ('1sq_2_1sq_Field.npy', (1100, 550)),

				#new set, ORIGIN = (1260, 570)
				'4o_2_4o' 	  : ('4ch_2_4ch_fixed_Field.npy', (1260, 570)),
				'3o_2_3o' 	  : ('3ch_2_3ch_fixed_Field.npy', (1260, 570)),
				'3o_2_4o' 	  : ("3ch_2_4ch_fixed_Field.npy", (1260, 570)),
				'4o_2_3o'	  : ("4ch_2_3ch_fixed_Field.npy", (1260, 570)),
				'4o_2_3cl'	  : ("4ch_2_3ch_cl_Field.npy", (1260, 570)),
				'3o_2_4cl'	  : ("3ch_2_4ch_cl_Field.npy", (1260, 570)),

				#virtual set, ORIGIN = (1470, 540), area = 690,000
				'c0d0'		  : ("c0d0_Field.npy",(1470, 540)),
				'c1d0'		  : ("c1d0_Field.npy",(1470, 540)),
				'c0d1'		  : ("c0d1_Field.npy",(1470, 540)),
				'c1d1'		  : ("c1d1_Field.npy",(1470, 540)),
				'2tun'		  : ("2tun_Field.npy",(1475, 540)),
				'c0d1-m'	  : ("c0d1-m_Field.npy",(1470, 540)),
				 }
	try:
		return fieldfolder+translator[type][0], translator[type][1]
	except  KeyError:
		return "FIELD NOT FOUND"

# generate field from a .nii.gz segmentation or a .gif black and white image
def generate(filename, targetfolder = None):
	if not targetfolder:
		targetfolder = 'fields_processed'
	ext = filename.split('.')[-1]

	if ext  == 'gif':
		array2d = np.asarray(imageio.imread(filename)).transpose()
		#avoid grey zones
		array2d[array2d > 0] = 255

	print("Nest map sucesfully generated")
	print("Area of the nest: ", np.sum(array2d)/255)

	# LEGACY FROM .nii.gz arenas processing
	# elif ext == 'gz':

	# 	img = nib.load(filename)
	# 	data = img.get_data()

	# 	# get a 2d slice of the pseudo 3d NIFTI image
	# 	array2d = np.squeeze(data)

	# 	# make all selected pixels white
	# 	array2d[array2d == 1] = 255;
	# END OF LEGACY PIECE
	

	#uncomment below for open field result
	#array2d[array2d == 0] = 255; 

	#save result as a NumPy array file and as a .gif image
	filename = filename.split('/')[-1]
	newfilename = targetfolder + '/' + filename[:max(filename.find('_raw'), filename.find('.'))]
	np.save(newfilename+'_Field.npy', array2d)
	scipy.misc.imsave(newfilename+'_Field.gif', array2d.transpose())

if __name__ == "__main__":
	##### Usage example (file  generation)
	#generate('fields_raw/c0d0.gif')
	#generate('fields_raw/c0d1.gif')
	#generate('fields_raw/c1d0.gif')
	#generate('fields_raw/c1d1.gif')
	generate('fields_raw/4ch_2_4ch_fixed.gif')
	generate('fields_raw/3ch_2_4ch_fixed.gif')
	generate('fields_raw/2tun.gif')
	generate('fields_raw/c0d1-m.gif')


