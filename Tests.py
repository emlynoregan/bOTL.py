import unittest
import bOTL

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
    
    def test_nones(self):
        bOTL.transform(None, None)
        
    def test_root(self):
        result = bOTL.transform({"name": "Freddo"}, "#$.name")
        
        self.assertEqual(result, "Freddo")
        
    def test_local(self):
        result = bOTL.transform({"name": "Freddo"}, "#@.name")
        
        self.assertEqual(result, "Freddo")
        
    def test_List(self):
        ltransform = ['#$.name']
        lsource = {"name": "Freddo"}
        lexpected = ["Freddo"]
        
        lresult = bOTL.transform(lsource, ltransform)
        
        print ("****")
        print lresult
        
        self.assertTrue(self.deepEqual(lexpected, lresult))

    def test_Object(self):
        ltransform = {'saying': ["#@.quote"], 'fullname': '#@.name'}
        lsource = {"name": "Freddo"}
        lexpected = {'saying': [], 'fullname': "Freddo"}
        
        lresult = bOTL.transform(lsource, ltransform)
        
        print ("****")
        print lresult
        
        self.assertTrue(self.deepEqual(lexpected, lresult))

    def DoSource1Test(self, aTransform, aExpected):
        lresult = bOTL.transform(self._source1, aTransform)
        
        print ("*************************************")
        print ("result: %s" % lresult)
        print ("expected: %s" % aExpected)

        self.assertTrue(self.deepEqual(lresult, aExpected, 100))
                
    def test_Synopsis(self):
        ltransform = {
          "characters": [
            {
              "_type": "#",
              "path": "$.items[*]",
              "transform": {
                "fullname": "#@.name",
                "saying": {
                  "_type": "#",
                  "path": "@.quote",
                  "nulls": False
                }
              }
            }
          ],
          "urls": [
            "#$..website"
          ]
        }
        
        lexpected = {
          "characters": [
            {
              "fullname": "Ambassador Kosh",
              "saying": "Yes"
            },
            {
              "fullname": "Worf"
            },
            {
              "fullname": "Stanley Tweedle"
            }
          ],
          "urls": [
            "http://babylon5.wikia.com/wiki/Kosh",
            "https://en.wikipedia.org/wiki/Worf",
            "http://lexx.wikia.com/wiki/Stanley_Tweedle"
          ]
        }

        self.DoSource1Test(ltransform, lexpected)
        
    def test_Example1(self):
        ltransform = {"urls": ["#$..website"]}
        lexpected = {
          "urls": [
            "http://babylon5.wikia.com/wiki/Kosh",
            "https://en.wikipedia.org/wiki/Worf",
            "http://lexx.wikia.com/wiki/Stanley_Tweedle"
          ]
        }
        
        self.DoSource1Test(ltransform, lexpected)
        
    def test_Basics_1(self):
        ltransform = {"urls": ["#$..website"]}
        lexpected = {
          "urls": [
            "http://babylon5.wikia.com/wiki/Kosh",
            "https://en.wikipedia.org/wiki/Worf",
            "http://lexx.wikia.com/wiki/Stanley_Tweedle"
          ]
        }
        
        self.DoSource1Test(ltransform, lexpected)
        
    def test_Sections_1(self):
        ltransform = {"_type": "#"}
        lexpected = self._source1
                
        self.DoSource1Test(ltransform, lexpected)
                        
    def test_Sections_2(self):
        ltransform = [
         {
          "_type": "#",
          "path": "$.items[*].type"
         }
        ]
        
        lexpected = ["Vorlonn", "Klingon", "Human"]

        self.DoSource1Test(ltransform, lexpected)
                        
    def test_Sections_3(self):
        ltransform = {
          "_type": "#",
          "path": "$..things",
          "nulltransform": "none"
        }
        
        lexpected = "none"

        self.DoSource1Test(ltransform, lexpected)

    def test_Sections_4(self):
        ltransform = [
         {
          "_type": "#",
          "path": "$.items[*].type",
          "transform": {
            "race": {
              "_type": "#"
            }
          }
         }
        ]
        
        lexpected = [
          { "race": "Vorlonn" },
          { "race": "Klingon" },
          { "race": "Human" }
        ]

        self.DoSource1Test(ltransform, lexpected)

    def test_Brief_1(self):
        ltransform = "#"
        lexpected = self._source1
                
        self.DoSource1Test(ltransform, lexpected)
                        
    def test_Brief_2(self):
        ltransform = [ "#$.items[*].type" ]
        
        lexpected = ["Vorlonn", "Klingon", "Human"]

        self.DoSource1Test(ltransform, lexpected)
                        
    def test_Brief_4(self):
        ltransform = [
            {
              "_type": "#",
              "path": "$.items[*].type",
              "transform": {
                "race": "#"
              }
            }
        ]
        
        lexpected = [
          { "race": "Vorlonn" },
          { "race": "Klingon" },
          { "race": "Human" }
        ]

        self.DoSource1Test(ltransform, lexpected)

    def test_Scope(self):
        ltransform = [
         {
          "_type": "#",
          "path": "$.items[*]",
          "scope": "item",
          "transform": 
            {
                "_type": "#",
                "path": "@..images",
                "transform": {
                  "name": "#item.name",
                  "pics": [
                    {
                      "_type": "#",
                      "path": "@" # unnecessary, illustrative
                    }
                  ]
                }
            }
         }
        ]
        
        lexpected = [
          {
            "name": "Worf",
            "pics": [
              [
                "https://en.wikipedia.org/wiki/File:WorfTNG.jpg",
                "http://example.com/worf.jpg"
              ]
            ]
          }
        ]

        self.DoSource1Test(ltransform, lexpected)

    def test_Scope2(self):
        ltransform = [
         {
          "_type": "#",
          "path": "$.items[*]",
          "scope": "item",
          "transform": 
            {
                "_type": "#",
                "path": "@..images",
                "transform": {
                  "name": "#item.name",
                  "pics": [
                    {
                      "_type": "#",
                      "path": "@" # unnecessary, illustrative
                    }
                  ]
                },
                "nulltransform": {
                  "name": "#item.name",
                  "nopics": True
                }
            }
         }
        ]
        
        lexpected = [
          {
            "name": "Ambassador Kosh",
            "nopics": True
          },
          {
            "name": "Worf",
            "pics": [
              "https://en.wikipedia.org/wiki/File:WorfTNG.jpg",
              "http://example.com/worf.jpg"
            ]
          },
          {
            "name": "Stanley Tweedle",
            "nopics": True
          }
        ]

        self.DoSource1Test(ltransform, lexpected)

    def test_Scope3(self):
        ltransform = [
            {
                "_type": "#",
                "path": "$.items[*]",
                "scope": "item",
                "transform": 
                {
                    "name": "#@.name",
                    "pics": {
                        "_type": "#",
                        "path": "@..images",
                        "nulls": False
                    }
                }
            }
        ]
        
        lexpected = [
          {
            "name": "Ambassador Kosh"
          },
          {
            "name": "Worf",
            "pics": [
              "https://en.wikipedia.org/wiki/File:WorfTNG.jpg",
              "http://example.com/worf.jpg"
            ]
          },
          {
            "name": "Stanley Tweedle"
          }
        ]

        self.DoSource1Test(ltransform, lexpected)

    def test_List2(self):
        ltransform = [
            {
              "_type": "#",
              "path": "@..images",
              "transform": {
                "name": "XX",
                "pics": [
                    {
                      "_type": "#",
                      "path": "@[*]", # unnecessary, illustrative
                      "nulls": False
                    }
                ]
              }
            }
        ]
        
        lexpected = [
          {
            "name": "XX",
            "pics": [
              "https://en.wikipedia.org/wiki/File:WorfTNG.jpg",
              "http://example.com/worf.jpg"
            ]
          }
        ]

        self.DoSource1Test(ltransform, lexpected)

    def test_Context1(self):
        ltransform = [ "#$..website", "#$..images[*]" ]
        
        lexpected = [
          "http://babylon5.wikia.com/wiki/Kosh",
          "https://en.wikipedia.org/wiki/Worf",
          "http://lexx.wikia.com/wiki/Stanley_Tweedle",
          "https://en.wikipedia.org/wiki/File:WorfTNG.jpg",
          "http://example.com/worf.jpg"
        ]

        self.DoSource1Test(ltransform, lexpected)

    def test_Context2(self):
        ltransform = "#$..website"
        
        lexpected = "http://babylon5.wikia.com/wiki/Kosh"

        self.DoSource1Test(ltransform, lexpected)

    def test_Context3(self):
        ltransform = {
          "stuff": {
            "_type": "#",
            "path": "$.stuff"
          },
          "thing": {
            "_type": "#",
            "path": "$.thing",
            "nulls": False
          }
        }
        
        lexpected = {
          "stuff": None
        }

        self.DoSource1Test(ltransform, lexpected)

    def test_ObjectSection(self):
        ltransform = {
          "_type": "object",
          "value": {
            "_type": "#",
            "transform": {
              "names": ["#$..name"]
            }
          }
        }
        
        lexpected = {
          "_type": "#",
          "transform": {
            "names": [
              "Ambassador Kosh",
              "Worf",
              "Stanley Tweedle"
            ]
          }
        }
        
        self.DoSource1Test(ltransform, lexpected)

    def test_LiteralSection(self):
        ltransform = {
          "_type": "literal",
          "value": {
            "_type": "#",
            "transform": {
              "names": ["#$..name"]
            }
          }
        }
        
        lexpected = {
          "_type": "#",
          "transform": {
            "names": ["#$..name"]
          }
        }
        
        self.DoSource1Test(ltransform, lexpected)

    def test_KeepNulls(self):
        ltransform = [{
            "_type": "#",
            "path": "$..items[*]",
            "transform": {
                "_type": "#",
                "path": "@..quote",
                "transform": {
                    "quote": "#@"
                },
                "nulltransform": None
            },
            "nulls": True
        }]
        
        lexpected = [{'quote': 'Yes'}, None, None]
        
        self.DoSource1Test(ltransform, lexpected)

    def test_DontKeepNulls(self):
        ltransform = [{
            "_type": "#",
            "path": "$..items[*]",
            "transform": {
                "_type": "#",
                "path": "@..quote",
                "transform": {
                    "quote": "#@"
                },
                "nulltransform": None
            },
            "nulls": False
        }]
        
        lexpected = [{'quote': 'Yes'}]
        
        self.DoSource1Test(ltransform, lexpected)

    _source1 = {
          "cursor": "8b08006b-963a-6909-c132-cc618cd4b352",
          "more": True,
          "items": [
            {
              "name": "Ambassador Kosh",
              "type": "Vorlonn",
              "resources": {
                "website": "http://babylon5.wikia.com/wiki/Kosh",
                "quote": "Yes"
              }
            },
            {
              "name": "Worf",
              "type": "Klingon",
              "resources": {
                "website": "https://en.wikipedia.org/wiki/Worf",
                "images": [
                  "https://en.wikipedia.org/wiki/File:WorfTNG.jpg",
                  "http://example.com/worf.jpg"
                ]
              }
            },
            {
              "name": "Stanley Tweedle",
              "type": "Human",
              "resources": {
                "website": "http://lexx.wikia.com/wiki/Stanley_Tweedle"
              }
            }
          ]
        }
