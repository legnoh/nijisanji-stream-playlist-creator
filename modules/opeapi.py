import requests
import numpy

def get_members_only_video_ids(video_ids):

    target_lists = []
    member_only_video_ids = []

    for i in range(0, len(video_ids), 10):
        target_lists.append(video_ids[i: i+10])    

    for i,target_list in enumerate(target_lists):
        print("({c}/{a}) Fetching members only video information...".format(c=i*10,a=len(target_lists)*10))
        try:
            response = requests.get(
                url="https://yt.lemnoslife.com/videos",
                params={
                    "part": "isMemberOnly",
                    "id": ','.join(target_list),
                },
            )
            raw_json = response.json()

            for item in raw_json['items']:
                if item['isMemberOnly'] == True:
                    member_only_video_ids.append(item['id'])  

        except requests.exceptions.RequestException as e:
            print('ERROR: {e}'.format(e=e))
            return []

    return member_only_video_ids
