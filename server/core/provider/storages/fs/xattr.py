"""
TLV - Type, Length, Value

Type(1 byte): 0-file, 1-meta key, 2-meta data
Length(4 bytes): int
Value: string|binary

0 10 ab
1 len(thumbnail-image)  thumbnail-image
2 len(image-binary) binary

"""

class FileSystem:
    """
    Adding extended attributes with random size above the file system level
    """

    def store(self, file):
        """
        Stores a file and adds the settings needed to allow it to hold extra meta data
        """
        pass

    def get(self, file):
        """
        Gets reference to the file content
        """
        pass

    def setAttribute(self, file, name, value, size=None):
        """
        Sets an attribute to a file
        """
        pass

    def getAttribute(self, file, name):
        """
        Gets an attribute from a file
        """
        return None
