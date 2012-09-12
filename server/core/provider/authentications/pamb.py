# [ Authentication Backends ] #
from backend import AbstractBackend, OTHER

import pam
class PamBackend(AbstractBackend):
    passwordStorage = OTHER
    
    def check(self, username, password, realm):
        """
        Checks if there is a user with the specified username and password for the specified realm
        @param string username
        @param string password in clear text
        @return boolean
        """
        return pam.authenticate(username, password)