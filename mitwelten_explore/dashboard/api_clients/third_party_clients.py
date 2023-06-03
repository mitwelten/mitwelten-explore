from dashboard.utils.communication import CachedRequest
from markdownify import markdownify


cr = CachedRequest("third_party_cache",2*60*60)

def get_wiki_summary(sciname, lang="de", char_limit=None):
    url = "https://{}.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles={}".format(
        lang, sciname
    )
    if char_limit is not None:
        url += "&exchars={}".format(char_limit)
    result = cr.get(url).json()
    page_id = next(iter(result["query"]["pages"]))
    summary = {
        "extract": result["query"]["pages"][page_id].get("extract"),
        "title": result["query"]["pages"][page_id].get("title"),
    }
    return summary




def generate_wiki_link(sciname, lang="de"):
    return "https://{}.wikipedia.org/wiki/{}".format(lang, sciname.replace(" ", "_"))



def request_image_extmetadata(image_name):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&titles=File:{image_name}&prop=imageinfo&iiprop=user|userid|canonicaltitle|url|extmetadata&format=json"
    req = cr.get(url)
    if req.status_code == 200:
        result = req.json()
        
        page_id = next(iter(result["query"]["pages"]))
        if page_id == "-1":
            return None
        image_info = result["query"]["pages"][page_id].get("imageinfo")
        if isinstance(image_info, list) and len(image_info)>0:
            image_info = image_info[0]
            return image_info.get("extmetadata")
    return None



def generate_image_attribution(image_url):
    if image_url is None:
        return None
    image_name = image_url.split("/")[-1]
    if image_name is None:
        return None
    img_extmetadata =  request_image_extmetadata(image_name)
    if img_extmetadata:
        try:
            artist = img_extmetadata.get("Artist").get("value")
            artist_md = "© "+markdownify(artist)
            license = img_extmetadata.get("License").get("value")
            license_url = img_extmetadata.get("LicenseUrl").get("value")
            if license is not None and license_url is not None:
                artist_md += f", [{license}]({license_url})"
            elif license is not None:
                artist_md += f", {license} "
                
            return artist_md
        except AttributeError:
            return None
    return None


