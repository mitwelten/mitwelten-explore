from dashboard.models import Annotation, AppUser
import requests
import os
import datetime
from configuration import DATA_API_URL


def get_annotations(auth_cookie=None):
    url = f"{DATA_API_URL}explore/annotations"
    res = requests.get(url, headers={"Authorization": f"Bearer {auth_cookie}"})
    if res.status_code != 200:
        return []
    annots = res.json()
    annotations = []
    for annot in annots:
        # timestamp = datetime.datetime.strptime(annot.get("time"), "%Y-%m-%d %H:%M")
        timestamp = datetime.datetime.fromisoformat(annot.get("created_at"))

        annotations.append(
            Annotation(
                title=annot.get("title"),
                md_content=annot.get("content"),
                timestamp=timestamp,  # .isoformat(),#.astimezone(datetime.timezone.utc).strftime("%d.%m.%Y %H:%M"),
                user=AppUser(
                    dict(
                        preferred_username=annot.get("username"),
                        name=annot.get("full_name"),
                        sub=annot.get("user_sub"),
                    )
                ),
                url=annot.get("url"),
                id=annot.get("id"),
            )
        )
    annotations.sort()
    return annotations


def get_annotation(annot_id, auth_cookie=None):
    url = f"{DATA_API_URL}explore/annotations/{annot_id}"
    res = requests.get(url, headers={"Authorization": f"Bearer {auth_cookie}"})
    if res.status_code == 200:
        annot = res.json()

        return Annotation(
            title=annot.get("title"),
            md_content=annot.get("content"),
            timestamp=datetime.datetime.fromisoformat(annot.get("created_at")),
            user=AppUser(
                dict(
                    preferred_username=annot.get("username"),
                    name=annot.get("full_name"),
                    sub=annot.get("user_sub"),
                )
            ),
            url=annot.get("url"),
            id=annot.get("id"),
        )


def get_annotation_by_user(user_sub, auth_cookie):
    filtered = [a for a in get_annotations(auth_cookie) if a.user.sub == user_sub]
    return filtered


def post_annotation(annotation: Annotation, auth_cookie):
    url = f"{DATA_API_URL}explore/annotations"
    res = requests.post(
        url=url,
        json=annotation.to_dict(),
        headers={"Authorization": f"Bearer {auth_cookie}"},
    )
    return True


def update_annotation(annot_id: int, annot_content: str, auth_cookie):
    url = f"{DATA_API_URL}explore/annotations/{annot_id}"
    res = requests.put(
        url=url,
        json=dict(content=annot_content),
        headers={"Authorization": f"Bearer {auth_cookie}"},
    )
    if res.status_code == 200:
        return True
    else:
        return False


def delete_annotation(annot_id: int, auth_cookie):
    url = f"{DATA_API_URL}explore/annotations/{annot_id}"
    res = requests.delete(url=url, headers={"Authorization": f"Bearer {auth_cookie}"})
    return True


def update_collection(datasets, auth_cookie):
    url = f"{DATA_API_URL}explore/collection"
    res = requests.post(
        url=url, headers={"Authorization": f"Bearer {auth_cookie}"}, json=datasets
    )


def get_collection(auth_cookie):
    url = f"{DATA_API_URL}explore/collection"
    res = requests.get(url=url, headers={"Authorization": f"Bearer {auth_cookie}"})
    return res.json()
