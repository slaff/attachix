# -*- coding: utf-8 -*-

class DummyCalendarProvider():
    def isCalendar(self, path, user=None):
        return True

    def store(self, path, event, user=None):
        pass

    def search(self, path, filter, user=None):
        return {path:1}


