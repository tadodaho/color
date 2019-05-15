import numpy as np
DIR = 'data/'

def openillum(filename):
	lst = []
	with open(DIR + filename, 'r') as f:
		result = f.read().rstrip().rsplit('\n')
		lst = []
		for row in result:
			coeff = 1
			for col in row.split('\t')[1:]:
				coeff *= float(col)
			lst.append(coeff)
	return lst

def openobs(filename):
	X = []
	Y = []
	Z = []
	with open(DIR + filename, 'r') as f:
		result = f.read().rstrip().rsplit('\n')
		for row in result:
			col = row.split('\t')[1:]
			X.append(float(col[0]))
			Y.append(float(col[1]))
			Z.append(float(col[2]))
	return (X, Y, Z)

def calculation(coeff, obsr, illnt):
	X, Y, Z = (0, 0 ,0)
	norm = 10
	for idx in range(len(coeff)):
		X += coeff[idx] * obsr[0][idx] * illnt[idx] / norm
		Y += coeff[idx] * obsr[1][idx] * illnt[idx] / norm
		Z += coeff[idx] * obsr[2][idx] * illnt[idx] / norm

	# chromacity coordinates (x, y)
	x = np.round(X / (X + Y + Z), 2)
	y = np.round(Y / (X + Y +Z), 2)
	tristimul = np.round(Y) #tristimulus

	X /= 100
	Y /= 100
	Z /= 100

	red = (X * 3.2406) + (Y * (-1.5372)) + (Z * (-0.4986))
	green = (X * (-0.9689)) + (Y *  1.8758) + (Z *  0.0415)
	blue = (X *  0.0557) + (Y * (-0.2040)) + (Z *  1.0570)

	red = check_first(red)
	green = check_first(green)
	blue = check_first(blue)

	red *= 255
	green *= 255
	blue *= 255

	red = check_second(red)
	green = check_second(green)
	blue = check_second(blue)
	return (int(red), int(green), int(blue)), (x, y, tristimul), (int(X * 100), int(Y * 100), int(Z * 100))

def check_first(value):
	if (value > 0.0031308):
		return 1.055 * (pow(value,(1/2.4))) - 0.055
	else:
		return 12.92 * value

def check_second(value):
    if value < 0:
        return 0
    elif value > 255:
        return 255
    return value
