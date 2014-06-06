class VHost():
    # IP and port on which the VHost is listening
    ip   = '0.0.0.0'
    port = 80

    # Hostnames that will be handled
    host = ['localhost']
    root = None
    env  = {}
    ssl  = {
        # If you want to serve the requests via SSL put here
        # keyfile = 'location/to/key/file',
        # certfile = 'location/to/cert/file'
    }
    config = None,
    timeouts  = {
        'init': 5, # wait 5 seconds to get the initial connection line
                   # this is also the keep-alive time
        'headers': 10 # wait 10 seconds to process all the headers
    }

    def __init__(self, config):
        self.config = config

    def load(self):
        """
        Load the resources and providers needed for this vhost.
        Put the implementation in the child class
        """
        pass

    def build(self):
        """
        Build the resource tree
        Put the implementation in the child class
        """
        pass