import cffi
import marshal
from numbers import Number


class BaseCodec(object):

    def __init__( self ):
        self.ffi = cffi.FFI()
        self.lib = self.ffi.dlopen(None)
        # types
        self.TYPE_STR = 99
        self.TYPE_UTF8 = 100 
        self.TYPE_NUM = 101

        # sizes in bytes
        self.DATALENSZ = 2 
        self.TYPESZ = 1
        self.USRSZ = 1
        self.USRTYPESZ = self.USRSZ + self.TYPESZ
        self.METASZ = self.USRTYPESZ + self.DATALENSZ

    # byte encoding 
    #               uint8      char*
    # [ 1 user ] [ 1 type ] [  data ]
    # data len is retrieved from db !
    # len is not part of encoding because it fucks order
   
    def enc_str(self, s, itp ):
        sc="xx"+s
        cdata = self.ffi.new("char []",sc)
        ctype = self.ffi.new('uint8_t *',itp)
        #clen  = self.ffi.new('uint16_t *',len(s) )
        typebuff =  self.ffi.buffer(ctype,self.USRTYPESZ)        
        #lenbuff  =  self.ffi.buffer(clen,self.DATALENSZ )

        databuff = self.ffi.buffer(cdata)
        databuff[1] = typebuff [0]
        #databuff[2] = lenbuff  [0]
        #databuff[3] = lenbuff  [1]
        print "enc cdata len",len(cdata)
        return cdata


    # warn: decode relies on external data size
    # this is done with database context
    # 
    def decode(self, cdata, cdata_len):
        #sz = self.TYPESZ + cdata_sz
        #print "decode cdata len",len(cdata)
        buff = self.ffi.buffer ( cdata,cdata_len )
        ctype = self.ffi.new('uint8_t*',0 )
        #clen  = self.ffi.new('uint16_t*',2 )
        #lenbuff = self.ffi.buffer ( clen, self.DATALENSZ )
        typebuff = self.ffi.buffer ( ctype, self.USRTYPESZ )

        typebuff[0] = buff [1]
        #lenbuff[0] = buff [2]
        #lenbuff[1] = buff [3]         

        #buff = self.ffi.buffer ( cdata, clen[0]+self.METASZ ) 
       # ( typeID,  data )
        if ctype[0] == self.TYPE_NUM:
            return ctype[0], marshal.loads( buff[self.USRTYPESZ:-1] )
        if ctype[0] == self.TYPE_STR:
            return ctype[0],buff[self.USRTYPESZ:-1]
        if ctype[0] == self.TYPE_UTF8:
            return ctype[0],buff[self.USRTYPESZ:-1].decode('utf-8')



    def encode(self, data):
       if isinstance(data, Number): 
           return self.enc_str(marshal.dumps(data), self.TYPE_NUM) 
       if isinstance(data, str ):
            return self.enc_str(data, self.TYPE_STR)
       if isinstance(data, unicode ):
            return self.enc_str(data.encode('utf-8'),self.TYPE_UTF8)



   
