import uuid

class AlleleExt(object):

    def get_alleles(self, allele_data, batch_size, testObject):

        list_to_yield = []
        dateProduced = allele_data['metaData']['dateProduced']
        dataProvider = allele_data['metaData']['dataProvider']
        release = ""

        if 'release' in allele_data['metaData']:
            release = allele_data['metaData']['release']

        for alleleRecord in allele_data['data']:

            globalId = alleleRecord['primaryId']
            localId = globalId.split(":")[1]

            if testObject.using_test_data() is True:
                is_it_test_entry = testObject.check_for_test_id_entry(globalId)
                if is_it_test_entry is False:
                    continue

            allele_dataset = {
                "symbol": alleleRecord.get('symbol'),
                "geneId": alleleRecord.get('gene'),
                "primaryId": alleleRecord.get('primaryId'),
                "globalId": globalId,
                "localId": localId,
                "taxonId": alleleRecord.get('taxonId'),
                "synonyms": alleleRecord.get('synonyms'),
                "secondaryIds": alleleRecord.get('secondaryIds'),
                "dataProvider": dataProvider,
                "dateProduced": dateProduced,
                "loadKey": dataProvider+"_"+dateProduced+"_allele",
                "release": release,
                "uuid": str(uuid.uuid4())
            }

            list_to_yield.append(allele_dataset)
            if len(list_to_yield) == batch_size:
                yield list_to_yield

                list_to_yield[:] = []  # Empty the list.

        if len(list_to_yield) > 0:
            yield list_to_yield


