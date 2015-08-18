import unittest
import bOTL
import json
import io
import os

class Tests(unittest.TestCase):
    def deepEqual(self, aMAS1, aMAS2, maxdepth=100):
        retval = False

        if maxdepth:
            retval = type(aMAS1) == type(aMAS2)
            if retval:
                if isinstance(aMAS1, dict):
                    retval = len(aMAS1.keys()) == len(aMAS2.keys())
                    if retval:
                        for lkey in aMAS1.keys():
                            retval = lkey in aMAS2 and self.deepEqual(aMAS1[lkey], aMAS2[lkey], maxdepth-1)
                            if not retval:
                                break
                elif isinstance(aMAS1, (list, tuple, set)):
                    retval = len(aMAS1) == len(aMAS2)
                    if retval:
                        for lindex, litem in enumerate(aMAS1):
                            retval = self.deepEqual(litem, aMAS2[lindex], maxdepth-1)
                else:
                    retval = aMAS1 == aMAS2
            
        return retval
    
    
    def test1(self):
        pass
        
def AddTests():
    ljsonPath = os.path.join(os.path.dirname(__file__), 'testdata.json')

    ljsonFile = open(ljsonPath)
    ljson = json.load(ljsonFile)
    
    for ltestData in ljson["tests"]:
        ltestName = "test_%s" % ltestData[0]
        lsource = ljson["sources"].get(ltestData[1])
        ltransform = ljson["transforms"].get(ltestData[2])
        lexpected = ljson["sources"].get(ltestData[3])
        
        def GetTestFunction(aSource, aTransform, aExpected):
            def TheTestFunction(self):
                lresult = bOTL.transform(aSource, aTransform)
                
                print ("*************************************")
                print ("result: %s" % lresult)
                print ("expected: %s" % aExpected)
        
                self.assertTrue(self.deepEqual(lresult, aExpected, 100))
            return TheTestFunction
            
        ltestFunction = GetTestFunction(lsource, ltransform, lexpected)
        ltestFunction.__name__ = str(ltestName)
        setattr(Tests, ltestName, ltestFunction )

AddTests()        
