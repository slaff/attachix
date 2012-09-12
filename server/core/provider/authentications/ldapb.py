# [ Authentication Backends ] #
from backend import AbstractBackend, OTHER

import ldap
class LdapBackend(AbstractBackend):
    passwordStorage = OTHER

    def __init__(self, server, shortDn):
        self.server = server
        self.shortDn= shortDn

    def check(self, username, password, realm):
        """
        Checks if there is a user with the specified username and password for the specified realm
        @param string username
        @param string password in clear text
        @return boolean
        """
        connection = ldap.initialize(self.server)
        connection.set_option(ldap.OPT_REFERRALS,0)

        result = connection.simple_bind("%s\\%s" % (self.shortDn, username), password)
        try:
            if connection.result(result) is not None:
                return True
        except:
            pass

        return False