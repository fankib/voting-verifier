enc_modulus = 89884656743115795386465259539451236680898848947115328636715040578866337902750481566354238661203768010560056939935696678829394884407208311246423715319737062188883946712432742638151109800623047059726541476042502884419075341171231440736956555270413618581675255342293149119973622969239858152417678164812113740223
enc_order = 44942328371557897693232629769725618340449424473557664318357520289433168951375240783177119330601884005280028469967848339414697442203604155623211857659868531094441973356216371319075554900311523529863270738021251442209537670585615720368478277635206809290837627671146574559986811484619929076208839082406056870111
enc_generator = 4
sig_modulus = 89884656743115795386465259539451236680898848947115328636715040578866337902750481566354238661203768010560056939935696678829394884407208311246423715319737062188883946712432742638151109800623047059726541476042502884419075341171231440736956555270413618581675255529365358698328774708775703215219351545329613875969
sig_order = 730750818665451459101842416358141509827966271787
sig_generator = 43753966268956158683794141044609048074944399463497118601009260015278907944793396888872654797436679156171704835263342098747229841982963550871557447683404359446377648645751856913829280577934384831381295103182368037001170314531189658120206052644043469275562473160989451140877931368137440524162645073654512304068

import sys
import json

is_linux = sys.platform == 'linux'
is_android = sys.platform == 'linux4'

if is_linux:
	from urllib import request
if is_android:
	import urllib
  
def modexp(base, exponent, modulus):
	if modulus == 1:
		return 0
	# Assert :: (modulus - 1) * (modulus - 1) does not overflow base
	result = 1
	base = base % modulus
	while exponent > 0:
		if ( exponent % 2 == 1):
			result = (result * base) % modulus
		exponent = exponent >> 1
		base = (base * base) % modulus
	return result
	
def mapGq2Zq(element):
	if element < enc_order:
		return element - 1
	return enc_modulus - element - 1
	
def urlopen(url):
	if is_android:
		return urllib.urlopen(url)
	if is_linux:
		return request.urlopen(url)
	return None


def publicSignatureKey(secretKey):	
	return modexp(sig_generator, secretKey, sig_modulus)

def getBallots(board):
    ballotsJson = urlopen(board + '/ballots')
    ballots = json.load(ballotsJson)
    return ballots['messages'] # verify signature ..
    
def getBallot(board, publicSignatureKey):
	ballots = getBallots(board)
	for ballot in ballots:
		if ballot['publicSignatureKey'] == str(publicSignatureKey):
			return ballot
	return Null
	
def getOptions(board):	
	electionDetailJson = urlopen(board + '/electionDetail')	
	electionDetail = json.load(electionDetailJson)	
	message = electionDetail['message']	
	optionsJson = message['options']	
	options = json.loads(optionsJson)	
	return options
	
def getEncryptionKey(board):
	encryptionKeyJson = urlopen(board + '/encryptionKey')
	encryptionKey = json.load(encryptionKeyJson)
	return int(encryptionKey['message']['value'])
    
def verify(sid, eid, x, r):
	board = sid + '/board/' + eid
	encryptionKey = getEncryptionKey(board)
	publicKey = publicSignatureKey(x)	
	ballot = getBallot(board, publicKey)	
	b = int(ballot['encryption']['b'])
	m2 = modexp(encryptionKey, enc_order-r, enc_modulus)
	m = (b * m2) % enc_modulus
	m = mapGq2Zq(m)
	print('decimal:', m)
	m = '{0:b}'.format(m)
	m = m[::-1] # reverse m
	print('start -->', m)
	options = getOptions(board)	
	selectedOptions = [];
	for key, value in enumerate(m):		
		if value == '1':			
			option = options[key]			
			selectedOptions.append(option)	
	return selectedOptions

def parseAndVerify(msg):
	tokens = msg.split('=')
	s = tokens[1][:-1]
	e = tokens[2][:-1] # cut of x of x=
	x = int(tokens[3][:-1]) # cut of n of n=
	r = int(tokens[4])
	return verify(s,e,x,r)


if __name__ == '__main__':
	if not len(sys.argv) == 2 or len(sys.argv) == 4:
		print('''usage:
	python verifier.py <electionid> <secretkey> <randomization>
		or
	python verifier.py <fullmessage> # fullmessage: e=<electionid>x=<secretkey>r=<randomization>
	''')
	
	if len(sys.argv) == 2:
		parseAndVerify(sys.argv[1])
	if len(sys.argv) == 4:
		e = sys.argv[1]
		x = int(sys.argv[2])
		r = int(sys.argv[3])	
		verify(e, x, r)
	
	


