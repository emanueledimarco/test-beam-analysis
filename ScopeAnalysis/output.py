from array import array
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

_rootBranchType2PythonArray = { 'b':'B', 'B':'b', 'i':'I', 'I':'i', 'F':'f', 'D':'d', 'l':'L', 'L':'l', 'O':'B' }

class OutputBranch:
    def __init__(self, tree, name, rootBranchType, n=1, lenVar=None, title=None):
        n = int(n)
        self.buff   = array(_rootBranchType2PythonArray[rootBranchType], n*[0. if rootBranchType in 'FD' else 0])
        self.lenVar = lenVar
        self.n = n
        if lenVar != None:
            self.branch = tree.Branch(name, self.buff, "%s[%s]/%s" % (name,lenVar,rootBranchType))
        elif n == 1:
            self.branch = tree.Branch(name, self.buff, name+"/"+rootBranchType)
        else:
            self.branch = tree.Branch(name, self.buff, "%s[%d]/%s" % (name,n,rootBranchType))
        if title: self.branch.SetTitle(title)
    def fill(self, val):
        if self.lenVar:
            if len(self.buff) < len(val): # realloc
                self.buff = array(self.buff.typecode, max(len(val),2*len(self.buff))*[0. if self.buff.typecode in 'fd' else 0])
                self.branch.SetAddress(self.buff)
            for i,v in enumerate(val): self.buff[i] = v
        elif self.n == 1: 
            self.buff[0] = val
        else:
            if len(val) != self.n: raise RuntimeError("Mismatch in filling branch %s of fixed length %d with %d values (%s)" % (self.Branch.GetName(),self.n,len(val),val))
            for i,v in enumerate(val): self.buff[i] = v

class OutputTree:
    def __init__(self, tfile, ttree):
        self._file = tfile
        self._tree = ttree
        self._branches = {} 
    def branch(self, name, rootBranchType, n=1, lenVar=None, title=None):
        if (lenVar != None) and (lenVar not in self._branches) and (not self._tree.GetBranch(lenVar)):
            self._branches[lenVar] = OutputBranch(self._tree, lenVar, "i")
        self._branches[name] = OutputBranch(self._tree, name, rootBranchType, n=n, lenVar=lenVar, title=title)
        return self._branches[name]
    def fillBranch(self, name, val):
        br = self._branches[name]
        if br.lenVar and (br.lenVar in self._branches):
            self._branches[br.lenVar].buff[0] = len(val)
        br.fill(val)
    def tree(self):
        return self._tree
    def fill(self):
        self._tree.Fill()
    def write(self):
        self._file.cd()
        self._tree.Write()

