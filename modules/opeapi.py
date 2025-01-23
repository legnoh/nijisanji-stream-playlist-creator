import requests,logging

def get_members_only_video_ids(video_ids):

    target_lists = []
    member_only_video_ids = []

    for i in range(0, len(video_ids), 10):
        target_lists.append(video_ids[i: i+10])    

    for i,target_list in enumerate(target_lists):
        logging.info(f"({i*10}/{len(target_lists)*10}) Fetching members only video information...")
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
            logging.info(f'ERROR: {e}')
            return []

    return member_only_video_ids
