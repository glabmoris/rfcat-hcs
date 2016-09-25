#!/usr/bin/env python
import binascii
from rflib import *
from termcolor import colored


bits_per_symbol = 3
nb_bits = 69
preamble_pulses = 12
header_bits = 3

def reframe_packet(p):
	#FIXME: This uses an ugly string hack to avoid dealing with bit alignement issues when dealing with long binary sequences. diff or stfu
	raw_frame = ''.join('{0:08b}'.format(ord(x), 'b') for x in p)

	#TODO: different HCS devices have different premables/headers
	preamble = ('01' * preamble_pulses ) + ('0' * header_bits)

	preamble_index = raw_frame.index(preamble)

	frame = raw_frame[preamble_index+ len(preamble):preamble_index+ len(preamble) + nb_bits*bits_per_symbol]

	return frame

def good_packet(p):
	if len(p) == nb_bits * bits_per_symbol:
		#TODO: could add a few sanity checks here such as the string being only being made of 100 and 110 triplets
		return True
	else:
		print "Bad packet: " + len(p) + " bits"
		return False

def pwm_decode(p):
	final_string = ""

	i = 0
	sz = len(p)
	while i < sz:
		final_string += "1" if (p[i+1]=="0") else "0"
		i+=3

	return final_string[::-1]

def print_packet(p):
	print colored(p[:5],'blue') + ' ' + colored(p[5:9],'cyan') + ' ' + colored(p[9:37],'yellow') + ' ' + colored(p[37:69],'red')


print "Configuration du dongle..."
d = RfCat();
d.setFreq(315e6)
d.setMdmModulation(MOD_ASK_OOK)
d.setMdmDRate(5000)
d.makePktFLEN(255) #get some extra bytes to be sure
d.setMaxPower()
d.lowball()
d.setPktPQT(0)
d.setMdmSyncWord(0b1010101010101000)

while True:
	try:
		y, t = d.RFrecv(1)
	
		try:
			packet_bits = reframe_packet(y)
			if good_packet(packet_bits):
				data = pwm_decode(packet_bits)
				print_packet(data)
		except:
			continue
	except KeyboardInterrupt:
		break
	except ChipconUsbTimeoutException:
		pass
