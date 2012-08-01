# Copyright 2012 10gen, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This file will be used with PyPi in order to package and distribute the final
# product.

"""Receives documents from the oplog worker threads and indexes them
    into the backend.

    This file is a starting point for a doc manager. The intent is
    that this file can be used as an example to add on different backends.
    To extend this to other systems, simply implement the exact same class and
    replace the method definitions with API calls for the desired backend.
    Each method is detailed to describe the desired behavior.
"""

import exceptions


class DocManager():
    """The DocManager class creates a connection to the backend engine and
    adds/removes documents, and in the case of rollback, searches for them.

    The reason for storing id/doc pairs as opposed to doc's is so that
    multiple updates to the same doc reflect the most up to date version as
    opposed to
    multiple, slightly different versions of a doc.
    """

    def __init__(self, url, auto_commit=True):
        """Verify URL and establish a connection.

        This method may vary from implementation to implementation, but it must
        verify the url to the backend and return None if that fails. It must
        also create the connection to the backend, and start a periodic
        committer if necessary. The uniqueKey is '_id', but this may be
        overridden
        by user defined configuration.
        """
        raise exceptions.NotImplementedError

    def upsert(self, doc):
        """Update or insert a document into engine

        This method should call whatever add/insert/update method exists for
        the backend engine and add the document in there. The input will
        always be one mongo document, represented as a Python dictionary.
        """
        raise exceptions.NotImplementedError

    def remove(self, doc):
        """Removes documents from engine

        The input is a python dictionary that represents a mongo document.
        """
        raise exceptions.NotImplementedError

    def search(self, start_ts, end_ts):
        """Called to query engine for documents in a time range.

        This method is only used by rollbacks to query all the documents in
        engine within a certain timestamp window. The input will be two longs
        (converted from Bson timestamp) which specify the time range. The
        return value should be an iterable set of documents.
        """
        raise exceptions.NotImplementedError

    def commit(self):
        """This function is used to force a refresh/commit.

        It is used only in the beginning of rollbacks and in test cases, and is
        not meant to be called in other circumstances. The body should commit
        all documents to the backend engine (like auto_commit), but not have
        any timers or run itself again (unlike auto_commit). In the event of
        too many engine searchers, the commit is wrapped in a retry_until_ok
        to keep trying until the commit goes through.
        """
        raise exceptions.NotImplementedError

    def run_auto_commit(self):
        """Periodically commits to the engine server, if needed.

        This function commits all changes to the engine, and then
        starts a
        timer that calls this function again in one second. The reason for this
        function is to prevent overloading engine from other searchers. This
        function may be modified based on the backend engine and how commits
        are handled, as timers may not be necessary in all instances.
        """
        raise exceptions.NotImplementedError

    def get_last_doc(self):
        """Returns the last document stored in the engine.

        This method is used for rollbacks to establish the rollback window,
        which is the gap between the last document on a mongo shard and the
        last document in engine. If there are no documents, this functions
        returns None. Otherwise, it returns the first document.
        """
        raise exceptions.NotImplementedError
