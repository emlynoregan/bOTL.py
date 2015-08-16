from jsonpath_rw import parse

def transform(aMASSource, abOTLTransform):
    ''' 
    bOTL transform external method
    '''
    lscope = {
        "$": aMASSource,
        "@": aMASSource
    }
    
    lresults = _transform(lscope, abOTLTransform)[0]
    return lresults[0] if lresults else None
    
def _transform(aScope, abOTLTransform):
    ''' 
    transform using populated scope
    '''
    print("in: %s, %s" % (abOTLTransform, aScope))
    
    lsectionF = GetSectionFunction(abOTLTransform)
    
    lresults, lkeepnulls = lsectionF(aScope)

    print("out: %s, %s" % (lresults, lkeepnulls))
    
    return lresults, lkeepnulls
        
def GetSectionFunction(abOTLTransform):
    '''
    return the correct section function to use on the top level of this transform 
    
    Section functions take a scope and return a pair of (results list, keep-nulls).
    
    Note the real functions also take a bOTL transform, which is partially applied
    using a lambda.
    '''
    lfunction = None
    if isinstance(abOTLTransform, dict):
        # got a dict
        if "_type" in abOTLTransform:
            ltype = abOTLTransform.get("_type")
            if ltype == "#":
                lfunction = lambda(aScope): EvaluateFullSection(aScope, abOTLTransform) 
            elif ltype == "object":
                lfunction = lambda(aScope): EvaluateObjectSection(aScope, abOTLTransform)
            elif ltype == "literal":
                lfunction = lambda(aScope): EvaluateLiteralSection(aScope, abOTLTransform)
        else:
            lfunction = lambda(aScope): EvaluateObject(aScope, abOTLTransform)
    elif isinstance(abOTLTransform, list):
        lfunction = lambda(aScope): EvaluateList(aScope, abOTLTransform)
    elif isinstance(abOTLTransform, basestring):
        if abOTLTransform[:1] == "#":
            lfunction = lambda (aScope): EvaluateFullSection(aScope, {"_type": "#", "path": abOTLTransform[1:]})
        else:
            lfunction = lambda (aScope): ([abOTLTransform], True)
    else:
        lfunction = lambda (aScope): ([abOTLTransform], True)
        
    return lfunction

# Evaluate functions must return a list of results and a boolean to indicate if nulls were included

def EvaluateFullSection(aScope, abOTLSection):
    lpath = abOTLSection.get("path")
    lpath = lpath if lpath else "@"
    print(lpath)
    lscopeid = abOTLSection.get("scope")
    lhastransform = "transform" in abOTLSection
    ltransform = abOTLSection.get("transform", None)
    lhasnulltransform = "nulltransform" in abOTLSection
    lnulltransform = abOTLSection.get("nulltransform", None)
    lkeepnulls = abOTLSection.get("nulls", True)
    
    #1: Evaluate the path
    if lpath[:1] == "$":
        # this is a bit of a hack. I'd like to be able to tell jsonpath to use the attribute "$" as the root,
        # but the library doesn't support that.
        lscope = aScope.get("$")
    else:
        lscope = aScope
    try:
        lselections = [lmatch.value for lmatch in parse(lpath).find(lscope)]
    except Exception, ex:
        raise Exception("Failed to parse '%s': %s" % (lpath, repr(ex)))

    lresults = []
        
    if lselections:
        # here we've got some results
        if lhastransform:
            # need to transform all items in selection
            for lselection in lselections:
                # set up scope for transform, store 
                # settings for restoration afterwards
                lprev_at = aScope.get("@")
                aScope["@"] = lselection
                if lscopeid:
                    lprev_scopeid = aScope.get(lscopeid)
                    aScope[lscopeid] = lselection
                
                lresults.extend(_transform(aScope, ltransform)[0])
                
                # now restore the scope
                aScope["@"] = lprev_at
                if lscopeid:
                    aScope[lscopeid] = lprev_scopeid
        else:
            lresults = lselections
    else:
        # here we've got no results
        if lhasnulltransform:
            lresults = _transform(aScope, lnulltransform)[0]
        else:
            lresults = []
            
    
    if not lkeepnulls:
        lresults = [lresult for lresult in lresults if not lresult is None]
        
    return lresults, lkeepnulls

def EvaluateObjectSection(aScope, abOTLObjectSection):
    lvalue = abOTLObjectSection.get("value")
    if not isinstance(lvalue, dict):
        raise Exception("Dict expected as value in Object Section") 
    retval = {}
    for lkey in lvalue.keys():
        lresults, lkeepnulls = _transform(aScope, lvalue[lkey]) if lkey != "_type" else ([lvalue[lkey]], True)
        lresult = lresults[0] if lresults else None
        if lresult or lkeepnulls:
            retval[lkey] = lresult
        
    return [retval], True

def EvaluateLiteralSection(aScope, abOTLObjectSection):
    return [abOTLObjectSection.get("value")], True

def EvaluateObject(aScope, abOTLObject):
    ltransformedObject = ((lkey, _transform(aScope, abOTLObject[lkey])) for lkey in abOTLObject.keys())
    
    #ltransformedObject is a list of pairs of (key, (results, keep-nulls))

    # what's this do? It's saying:
    # for each (key, (results, keep-nulls)) in ltransformedObject,
    # include (key, results[0] if results else None)
    # but only if there are some results, or keep-nulls

    lfilteredObject = {
        litem[0]: (litem[1][0][0] if litem[1][0] else None) 
        for litem in ltransformedObject 
        if litem[1][0] or litem[1][1]
    }
    
    print ("fobj: %s" % lfilteredObject)
    # And lfilteredObject is a dictionary comprehension, so
    # the (key, results[0]) pairs become entried in the dict.
    
    return [lfilteredObject], True

def EvaluateList(aScope, abOTLList):
    retval = [_transform(aScope, litem)[0] for litem in abOTLList]
    retval = [litem for llist in retval for litem in llist]
    return [retval], True


