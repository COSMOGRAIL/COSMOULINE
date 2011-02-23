
def simplemediancoeff(refidentstars, identstars):
	#
	# calculates a simple (but try to get that better ... it's pretty good !) multiplicative coeff for each image
	# "calc one coef for each star and take the median of them"
	# coef = reference / image
	
	
	coeffs = []
	for refstar in refidentstars:
		for star in identstars:
			if refstar.name != star.name:
				continue
			coeffs.append(refstar.flux/star.flux)
			break
			
	if len(coeffs) > 0:
		coeffarr = array(coeffs)
		stddev = coeffarr.std()
		return len(coeffs), float(median(coeffs)), float(stddev), float(max(coeffs) - min(coeffs))
	else:	
		return 0, 1.0, 99.0, 99.0
	
	
	
	
	
	
	
