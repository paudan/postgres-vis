from fpdf import FPDF
from fpdf.py3k import PY3K

class UnicodeFPDF(FPDF):

    def output(self, name='',dest=''):
        "Output PDF to some destination"
        #Finish document if necessary
        if(self.state<3):
            self.close()
        dest=dest.upper()
        if(dest==''):
            if(name==''):
                name='doc.pdf'
                dest='I'
            else:
                dest='F'
        if dest=='I':
            print(self.buffer)
        elif dest=='D':
            print(self.buffer)
        elif dest=='F':
            #Save to local file
            f=open(name,'wb')
            if(not f):
                self.error('Unable to create output file: '+name)
            if PY3K:
                # manage binary data as latin1 until PEP461 or similar is implemented
                f.write(self.buffer.encode("iso8859-13"))
            else:
                f.write(self.buffer)
            f.close()
        elif dest=='S':
            #Return as a string
            return self.buffer
        else:
            self.error('Incorrect output destination: '+dest)
        return ''