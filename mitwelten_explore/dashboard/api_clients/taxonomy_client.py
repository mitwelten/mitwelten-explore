from dashboard.utils.communication import CachedRequest
from dashboard.models import RankEnum, Taxon, GBIFTaxon
from configuration import DATA_API_URL

cr = CachedRequest("taxonomy_cache",60*60)

def get_taxon_by_level(level: RankEnum):
    url = f"{DATA_API_URL}taxonomy/level/{level}"
    res = cr.get(url)
    if res.status_code == 200:
        taxons = res.json()
        return [Taxon(**t) for t in taxons]
    return []


def get_parent_taxonomy(taxon_key: int):
    url = f"{DATA_API_URL}taxonomy/id/{taxon_key}"
    res = cr.get(url)
    if res.status_code == 200:
        taxons = res.json()
        return [Taxon(**t) for t in taxons]
    return []

def get_taxon(taxon_key: int):
    taxon_tree = get_parent_taxonomy(taxon_key=taxon_key)
    return min(taxon_tree)

def get_taxon_dataset(taxon_key):
    url = f"{DATA_API_URL}taxonomy/id/{taxon_key}"
    res = cr.get(url)
    if res.status_code == 200:
        taxon_resp = res.json()
        taxons = [Taxon(**t) for t in taxon_resp]
        return min(taxons).to_dataset()
    return None

def get_gbif_taxon_dataset(taxon_key):
    url = f"{DATA_API_URL}taxonomy/id/{taxon_key}"
    res = cr.get(url)
    if res.status_code == 200:
        taxon_resp = res.json()
        taxons = [Taxon(**t) for t in taxon_resp]
        return GBIFTaxon(**min(taxons).to_dataset()).to_dataset()
    return None