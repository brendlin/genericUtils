###################################################
#
#  Decode the var DetCells in the D3PD containing
#  the detector information
#
#
#
#
###################################################

class PyDecodeDetCells():
    def __init__(self):
        """initialize needed variables

        \param self
        """
        self.key_length = { 'det': 4
                      ,'em' : 5
                      ,'hec': 2
                      ,'fcal': 2
                      ,'tile': 8
                     }
        self.det_key  = ''
        self.em_key   = ''
        self.hec_key  = ''
        self.fcal_key = ''
        self.tile_key = ''

        self.decoded_string = ''


    def reset(self):
        """Reset all values before decoding to make sure there is no overlap

        \param self
        """
        self.det_key  = ''
        self.em_key   = ''
        self.hec_key  = ''
        self.fcal_key = ''
        self.tile_key = ''

        self.decoded_string = ''


    def splitKey(self, key_string):
        """Split the key up by detector.

        Split the key up into different strings corresponding to each detector section.
        The places to split the key at are defined by self.key_length[det].
        \param self
        \param key_string Binary number stored as a string to split up.
        """
        self.reset() 
        key_list = []  #mainly for testing purposes
        self.det_key, key_string = key_string[-(self.key_length['det']) :], key_string[: -(self.key_length['det'])]
        self.em_key, key_string = key_string[-(self.key_length['em']) :], key_string[: -(self.key_length['em'])]
        self.hec_key, key_string = key_string[-(self.key_length['hec']) :], key_string[: -(self.key_length['hec'])]
        self.fcal_key, key_string = key_string[-(self.key_length['fcal']) :], key_string[: -(self.key_length['fcal'])]
        self.tile_key, key_string = key_string[-(self.key_length['tile']) :], key_string[: -(self.key_length['tile'])]
        key_list = [self.det_key, self.em_key, self.hec_key, self.fcal_key, self.tile_key]   # test the keys. Only implemented in test so far
        return key_list

    def detDecode(self, key):
        """Decode the det_key string.

        adds to the output string the name of the detector

        \param self
        \param key the detector key to decode
        \return output The string of decoded keys
        """
        output = ''
        if key[0] == '1':
            output += 'tile,'
        if key[1] == '1':
            output += 'fcal,'
        if key[2] == '1':
            output += 'hec,'
        if key[3] == '1':
            output += 'em,'
        return output

    def emDecode(self, key):
        """Decode the em_key string.

        adds to the output string the name of the part of the detector
        and adds which layer of the em cal was hit.

        \param self
        \param key the detector key to decode
        \return output The string of decoded keys
        """
        output = ''
        if key[0] == '1':
            output += 'ecOuter,'
        if key[1] == '1':
            output += 'ecInner,'
        if key[2] == '1':
            output += 'barrel,'
        if 'em,' in self.decoded_string:
            output += 'layer_'+str(int( key[3:], 2))+',' # Convert last two bits from binary number to int then back to string
        return output

    def hecDecode(self, key):
        """Decode the hec_key string.

        adds to the output string the sample in the had end cap

        \param self
        \param key the detector key to decode
        \return output The string of decoded keys
        """
        output = ''
        if 'hec,' in self.decoded_string:
            output += 'sample_'+str(int( key[0:],2))+','
        return output

    def fcalDecode(self, key):
        """Decode the fcal_key string.

        adds to the output string the module number in the fcal

        \param self
        \param key the detector key to decode
        \return output The string of decoded keys
        """
        output = ''
        if 'fcal,' in self.decoded_string:
            output += 'module_'+str(int( key[0:],2))+','
        return output

    def tileDecode(self, key):
        """Decode the tile_key string.

        adds to the output string the name of the part of the detector
        and adds the layer in the detector.

        \param self
        \param key the tile key to decode
        \return output The string of decoded keys
        """
        output = ''
        # key[0] apparently is not used
        if not key == '':
            if key[1] == '1':
                output += 'gapScin,'
            if key[2] == '1':
                output += 'gap,'
            if key[3] == '1':
                output += 'extBarrel,'
            if key[4] == '1':
                output += 'barrel,'
        if 'tile,' in self.decoded_string:
            output += 'sample_'+str(int( key[5:], 2))+','
        return output

    def getDetKey(self):
        return self.det_key

    def getEmKey(self):
        return self.em_key
        
    def getHecKey(self):
        return self.hec_key

    def getFcalKey(self):
        return self.fcal_key

    def getTileKey(self):
        return self.tile_key



    def decode(self, key):
        """Decode the binary key.

        More details.

        \param key The value of the DetCells variable.
        """
        key_string = bin(key)  #convert the key to a binary number and store as a string
        key_string = key_string[2:]

        diff = abs( len(key_string) - 21)
        key_string = '0'*diff + key_string

        self.splitKey( key_string ) #split up the string

        self.decoded_string = ''
        self.decoded_string +=  self.detDecode(self.det_key) # make the output string !!!!WARNING: detDecode() must be first
        if not self.em_key == '':
            self.decoded_string += self.emDecode(self.em_key)
        if not self.hec_key == '':
            self.decoded_string += self.hecDecode(self.hec_key)
        if not self.fcal_key == '':
            self.decoded_string += self.fcalDecode(self.fcal_key)
        if not self.tile_key == '':
            self.decoded_string += self.tileDecode(self.tile_key)
                               

        return self.decoded_string









