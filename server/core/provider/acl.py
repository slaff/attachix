# To change this template, choose Tools | Templates
# and open the template in the editor.

class Interface():
    def isAllowed(self, action, object):
        raise Exception('Implement this method in the child class')

class Property(Interface):

    denyRules = {
        # action : { 'namespaces1': 1, ...}
    }
    
    def __init__(self, denyRules):
        self.denyRules = denyRules

    """
    Implements filtering by namespace
    @param string action
        - read
        - write
    @param string object  key
    """
    def isAllowed(self, action, object):
        nameSpace = ''
        if object[0:1] == '{':
            last = object.find('}',1)
            if last > 0:
                nameSpace = object[1:last]

        try:
            return not self.denyRules[action][nameSpace]
        except:
            return True
