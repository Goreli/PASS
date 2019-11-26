'''
Created on 19 May 2018

Refer these links re moving expired docs to a different collection.
    https://stackoverflow.com/questions/27039083/mongodb-move-documents-from-one-collection-to-another-collection?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    https://stackoverflow.com/questions/8933307/clone-a-collection-in-mongodb?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
    https://docs.mongodb.com/manual/reference/command/cloneCollection/
    
Check if the upsert_documents and remove_documents methods should raise an exception
 - refer comments in the body of the methods.
 
The move_data method can probably be optimised compared to the original 
javascript based implementation shown in the first reference above.
Try using sets to identify the minimum set required for insertion
and exact set required for deletion. This is to avoid upsertion of existing
documents.  


@author: David
'''
import logging
import datetime
from pymongo import MongoClient, ReplaceOne, DeleteOne
from copy import deepcopy
from pprint import pprint


class MongodbAdapter:

    def __init__(self, connstr, dbstr, collstr, logger=None):
        self._client = MongoClient(connstr)
        self._db = self._client[dbstr]
        self._collection = self._db[collstr]
        self._logger = logger

    def filter_urls(self, urls):
        filtered_urls = deepcopy(urls)
        cursor = self._collection.find(
            {'url': {'$in': urls}}, {'_id': 0, 'url': 1})
        for doc in cursor:
            url = doc['url']
            filtered_urls.remove(url)
        msg = f'Keeping documents with the following url(s): {filtered_urls}'
        self._log_low_lvl_msg(msg)
        return filtered_urls

    def insert_one(self, pydoc):
        result = self._collection.insert_one(pydoc)
        auction_id = pydoc['document']['auction']['auction_id']
        msg = f'Document with auction_id={auction_id} stored under _id={result.inserted_id}'
        self._log_low_lvl_msg(msg)

    def _log_low_lvl_msg(self, msg, usetimestamp=False):
        outmsg = msg
        if (usetimestamp):
            local_dt_str = datetime.datetime.now().__str__().split('.')[0]
            outmsg = f'{local_dt_str} - {msg}'
        if (self._logger):
            if (self._logger.getEffectiveLevel() < logging.INFO):
                self._logger.info(outmsg)
        else:
            print(outmsg)

    def upsert_documents(self, documents):
        ''' The minimum requirement for the content of the documents is 
            each document must contain the _id field.
            As the documents are inserted into the database they should
            contain the entire content expected of them.
            '''
        self._log_low_lvl_msg(
            f'Started upsert_documents.', usetimestamp=True)
        requests = []
        inserted_ids = []
        for doc in documents:
            id = doc['_id']
            requests.append(ReplaceOne({'_id': id}, doc, upsert=True))
            inserted_ids.append(id)
        result = self._collection.bulk_write(requests, ordered=False)

        self._log_low_lvl_msg(f'result.deleted_count={result.deleted_count}')
        self._log_low_lvl_msg(f'result.inserted_count={result.inserted_count}')
        self._log_low_lvl_msg(f'result.matched_count={result.matched_count}')
        self._log_low_lvl_msg(f'result.modified_count={result.modified_count}')
        self._log_low_lvl_msg(f'result.upserted_count={result.upserted_count}')
#         self._log_low_lvl_msg(f'result.upserted_ids={result.upserted_ids}')
        self._log_low_lvl_msg(
            f'ended upsert_documents.', usetimestamp=True)

        assert (len(requests) == result.matched_count + result.upserted_count)
        # Should probably raise an exception here if the counts above don't match up.
        # Need to understand if bulk_write raises such exceptions by itself,
        # so there wouldn't be a need to do it in this piece of code.

        return inserted_ids

    def remove_documents(self, documents):
        ''' The minimum requirement for the content of the documents is 
            each document must contain the _id field.
            '''
        self._log_low_lvl_msg(
            f'started remove_documents.', usetimestamp=True)
        requests = []
        for doc in documents:
            id = doc['_id']
            requests.append(DeleteOne({'_id': id}))
        result = self._collection.bulk_write(requests, ordered=False)

        self._log_low_lvl_msg(f'result.deleted_count={result.deleted_count}')
        self._log_low_lvl_msg(f'result.inserted_count={result.inserted_count}')
        self._log_low_lvl_msg(f'result.matched_count={result.matched_count}')
        self._log_low_lvl_msg(f'result.modified_count={result.modified_count}')
        self._log_low_lvl_msg(f'result.upserted_count={result.upserted_count}')
#         self._log_low_lvl_msg(f'result.upserted_ids={result.upserted_ids}')
        self._log_low_lvl_msg(
            f'ended remove_documents.', usetimestamp=True)

        assert (len(requests) == result.deleted_count)
        # Should probably raise an exception here if the counts above don't match up.
        # Need to understand if bulk_write raises such exceptions by itself,
        # so there wouldn't be a need to do it in this piece of code.

    def move_documents(self, target_adapter, filter, batch_size):
        self._log_low_lvl_msg(
            f'started move_documents using filter {filter}.', usetimestamp=True)

        count = self._collection.find(filter).count()
        if(self._logger):
            self._logger.info(
                f'Identified {count} documents to be moved.')
        while count:
            if(self._logger):
                self._logger.info(
                    f'Moving a batch of {min(count, batch_size)} documents out of {count}')
            source_docs = self._collection.find(filter).limit(batch_size)
            ids_of_copied_docs = target_adapter.upsert_documents(source_docs)

            target_docs = target_adapter._collection.find(
                {'_id': {'$in': ids_of_copied_docs}})
            self.remove_documents(target_docs)

            count = self._collection.find(filter).count()

        self._log_low_lvl_msg(
            f'ended move_documents.', usetimestamp=True)


'''            
function insertBatch(collection, documents) {
  var bulkInsert = collection.initializeUnorderedBulkOp();
  var insertedIds = [];
  var id;
  documents.forEach(function(doc) {
    id = doc._id;
    // Insert without raising an error for duplicates
    bulkInsert.find({_id: id}).upsert().replaceOne(doc);
    insertedIds.push(id);
  });
  bulkInsert.execute();
  return insertedIds;
}

function deleteBatch(collection, documents) {
  var bulkRemove = collection.initializeUnorderedBulkOp();
  documents.forEach(function(doc) {
    bulkRemove.find({_id: doc._id}).removeOne();
  });
  bulkRemove.execute();
}

function moveDocuments(sourceCollection, targetCollection, filter, batchSize) {
  print("Moving " + sourceCollection.find(filter).count() + " documents from " + sourceCollection + " to " + targetCollection);
  var count;
  while ((count = sourceCollection.find(filter).count()) > 0) {
    print(count + " documents remaining");
    sourceDocs = sourceCollection.find(filter).limit(batchSize);
    idsOfCopiedDocs = insertBatch(targetCollection, sourceDocs);

    targetDocs = targetCollection.find({_id: {$in: idsOfCopiedDocs}});
    deleteBatch(sourceCollection, targetDocs);
  }
  print("Done!")
}
'''

if __name__ == '__main__':

    src = MongodbAdapter(
        'mongodb://localhost:27017', 'JewelryAuctionsCurrent', 'PA_sets', None)

#     src.upsert_documents(
#         [{'_id': 1, 'a': 1}, {'_id': 2, 'b': 2}, {'_id': 3, 'b': 3}])
#     src.remove_documents(
#         [{'_id': 1, 'a': 1}, {'_id': 2, 'b': 2}, {'_id': 3, 'b': 3}])

    src.upsert_documents(
        [{'_id': 11, 'a': 11}, {'_id': 12, 'b': 12}, {'_id': 13, 'b': 13}, {'_id': 14, 'b': 14}, {'_id': 15, 'b': 15}, {'_id': 16, 'b': 16}])
    trgt = MongodbAdapter(
        'mongodb://localhost:27017', 'JewelryAuctionsCompleted', 'PA_sets', None)
    filter = {'b': {'$in': [11, 13, 14, 15]}}
    batch_size = 2
    src.move_documents(trgt, filter, batch_size)
