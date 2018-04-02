import uuid
from services import UrlService

class AlleleExt(object):

    def get_alleles(self, allele_data, batch_size, testObject, graph):

        list_to_yield = []
        dateProduced = allele_data['metaData']['dateProduced']
        dataProvider = allele_data['metaData']['dataProvider']
        release = ""

        if 'release' in allele_data['metaData']:
            release = allele_data['metaData']['release']

        for alleleRecord in allele_data['data']:
            crossReferences = []
            globalId = alleleRecord['primaryId']
            localId = globalId.split(":")[1]
            modGlobalCrossRefId = ""

            if testObject.using_test_data() is True:
                is_it_test_entry = testObject.check_for_test_id_entry(globalId)
                if is_it_test_entry is False:
                    continue

            if 'crossReferences' in alleleRecord:

                for crossRef in alleleRecord['crossReferences']:
                    crossRefId = crossRef.get('id')
                    local_crossref_id = crossRefId.split(":")[1]
                    prefix = crossRef.get('id').split(":")[0]
                    pages = crossRef.get('pages')
                    global_id = crossRef.get('id')

                    # some pages collection have 0 elements
                    if pages is not None and len(pages) > 0:
                        for page in pages:
                            if page == 'allele':
                                modGlobalCrossRefId = UrlService.get_complete_url(local_crossref_id, crossRefId,
                                                                                   global_id, prefix + page, graph)
                            crossReferences.append({
                                "id": crossRef.get('id'),
                                "globalCrossRefId": crossRef.get('id'),
                                "localId": local_crossref_id,
                                "crossRefCompleteUrl": UrlService.get_complete_url(local_crossref_id, crossRefId,
                                                                                   global_id, prefix + page, graph),
                                "prefix": prefix,
                                "crossRefType": page,
                                "primaryKey": global_id + page,
                                "uuid": str(uuid.uuid4())
                            })

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
                "modGlobalCrossRefId": modGlobalCrossRefId,
                "uuid": str(uuid.uuid4())
            }

            list_to_yield.append(allele_dataset)
            if len(list_to_yield) == batch_size:
                yield list_to_yield

                list_to_yield[:] = []  # Empty the list.

        if len(list_to_yield) > 0:
            yield list_to_yield


    # def get_complete_url (self, local_id, global_id, primary_id):
    #     # Local and global are cross references, primary is the gene id.
    #     # TODO Update to dispatch?
    #     complete_url = None
    #
    #
    #     if global_id.startswith('MGI'):
    #         complete_url = 'http://www.informatics.jax.org/allele/' + global_id
    #     elif global_id.startswith('RGD'):
    #         complete_url = 'https://rgd.mcw.edu/rgdweb/report/gene/main.html?id=RGD:' + local_id
    #     elif global_id.startswith('SGD'):
    #         complete_url = 'http://www.yeastgenome.org/locus/' + local_id
    #     elif global_id.startswith('FB'):
    #         complete_url = 'http://flybase.org/reports/' + local_id + '.html'
    #     elif global_id.startswith('ZFIN'):
    #         complete_url = 'http://zfin.org/' + local_id
    #     elif global_id.startswith('WB:'):
    #         complete_url = 'http://www.wormbase.org/db/get?name=' + local_id + ';class=Variation'
    #
    #     return complete_url