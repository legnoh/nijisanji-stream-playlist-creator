from datetime import datetime
from janome.tokenizer import Tokenizer, Token
from lingua import Language, LanguageDetectorBuilder
from zoneinfo import ZoneInfo
import collections,itertools,re,requests,os,logging
import modules.youtube_direct as ytd
from modules.niji_dataclass import RootJSON, Stream, OnAirType
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from pyvirtualdisplay.display import Display
from bs4 import BeautifulSoup

def get_streams(subscription_channels:list[str], lang=None, archive_hours=12, wait_minutes=15) -> list[Stream] | None:

    now = datetime.now(ZoneInfo("Asia/Tokyo"))

    all_movies: list[Stream] = []
    nominated_movies: list[Stream] = []
    pre_nominated_movies: list[Stream] = []

    favorite_keywords = ['雑談', 'ざつだん',
                         '朝', '昼', '夕', '晩', '夜',
                         '凸', '酒', '料理', '掃除', '作業', '勉強',
                         'らじ', 'ラジ', 'RADIO',
                         '競馬', '賞', '記念', '杯', 'ダービー', 'オークス']
    filter_keyword = '歌|メン限|メンバー限定|MEMBER'
    common_words = []
    words = []

    languages = [Language.JAPANESE, Language.ENGLISH, Language.KOREAN, Language.INDONESIAN]
    detector = LanguageDetectorBuilder.from_languages(*languages).build()
    t = Tokenizer("./niji_dict.csv", udic_enc="utf8")

    if os.environ.get('GITHUB_ACTIONS', False):
        logging.info("# start display...")
        display = Display(visible=False, size=(1024, 768))
        display.start()

    driver = webdriver.Chrome(service=Service(), options=webdriver.ChromeOptions())
    driver.implicitly_wait(0.5)
    driver.get("https://www.youtube.com/")

    try:
        logging.info(f"fetch movie data...")
        response_initial = requests.get("https://www.nijisanji.jp/streams")
        soup = BeautifulSoup(response_initial.text, "html.parser")
        script = soup.find("script", id="__NEXT_DATA__")
        if script and script.string:
            root_json_data = RootJSON.model_validate_json(script.string)
            all_movies = root_json_data.props.page_props.streams
        else:
            logging.warning("Failed to find __NEXT_DATA__ script")
            return None

        logging.info("# 情報収集")
        for i,m in enumerate(all_movies):

            if m.channel is None:
                logging.warning(f"channel is None: {m.title}")
                continue

            # 欲しい情報をdictに追加しておく

            ## 動画ID
            video_url = m.url or ''
            m.youtube_video_id = video_url.replace('https://www.youtube.com/watch?v=', '')

            ## 購読チャンネル
            m.subscribed = m.channel.name in subscription_channels
            
            ## 配信言語(推定)
            m_lang = detector.detect_language_of(m.title or '')
            if m_lang != None:
                m.lang = m_lang.name
            else:
                m.lang = None
            
            ## キーワード一致フラグ
            for keyword in favorite_keywords:
                if keyword in (m.title or ''):
                    m.keyword_match = True
                    break
            if m.keyword_match is None:
                m.keyword_match = False

            # 中の単語を形態素解析で収集
            for token in t.tokenize(m.title or ''):
                if type(token) is Token:
                    s_token = token.part_of_speech.split(',')
                    if (s_token[0] == '名詞' and s_token[1] == '一般') \
                        or (s_token[0] == '動詞' and s_token[1] == '自立' and len(token.surface) >= 2) \
                        or (s_token[0] == '形容詞' and s_token[1] == '自立'):
                        words.append(token.surface)
        
        # 頻出単語上位10個から10回以上出たものを除外ワードとして特定
        logging.info("# トレンドワード特定")
        c = collections.Counter(words)
        common_words_select = c.most_common(10)
        for w in common_words_select:
            if w[1] > 10:
                logging.info(f"除外ワード: {w}")
                common_words.append(w[0])
        
        # 除外ロジック
        logging.info("# 除外")
        for m in all_movies:

            # 頻出単語を含むものをリストから除外する
            # (あまりにブームになっているものはつまらないので)
            exc_flag = False
            for cw in common_words:
                if cw in (m.title or ''):
                    exc_flag = True
                    logging.info(f"除外(頻出({cw})): {m.title}")
                    break
            if exc_flag == True:
                continue

            # 除外キーワードの配信を除外する
            # (ログインが必要な配信、ライブ性のない配信はリストに入れても意味がない)
            if len(re.findall(filter_keyword, m.title or '')) != 0:
                logging.info(f"除外(不適格): {m.title}")
                continue
        
            # 配信終了から指定時間以上経ったものも除外する
            if m.end_at is not None and (now - m.end_at).total_seconds() > (archive_hours * 60 * 60):
                logging.info(f"除外({archive_hours}時間経過): {m.title}")
                continue

            # 配信前で、配信開始前15分以上のものも除外する
            if (m.start_at is not None
                and m.end_at is None
                and m.status == OnAirType.not_on_air
                and (m.start_at - now).total_seconds() > wait_minutes * 60):
                logging.info(f"除外(開始{wait_minutes}分以上前): {m.title}")
                continue

            # 配信言語指定がある場合、指定した言語以外の配信を除外する
            if lang is not None and lang != m.lang:
                logging.info(f"除外(対象外言語({m.lang})): {m.title}")
                continue

            # ここまで残ったものをプレ候補として選定する
            pre_nominated_movies.append(m)
        
        # 最後にメン限かどうか判定する
        logging.info("# メン限判定")
        for m in pre_nominated_movies:
            if ytd.is_members_only(driver, m.youtube_video_id or ''):
                logging.info(f"除外(メン限): {m.title}")
            else:
                nominated_movies.append(m)

        # 残った動画をジャンル別に整理していく
        logging.info("# 最終ピックアップ")
        movies_genred = [[],[],[],[],[],[],[]]
        for m in nominated_movies:

            # 1: 配信中, 登録チャンネル, キーワード一致
            if m.status == OnAirType.on_air and m.subscribed and m.keyword_match:
                movies_genred[0].append(m)
                continue

            # 2: 登録チャンネル、キーワード一致
            if m.subscribed and m.keyword_match:
                movies_genred[1].append(m)
                continue

            # 4: キーワード一致
            if m.keyword_match:
                movies_genred[3].append(m)
                continue

            # 3: 配信中, 登録チャンネル
            if m.status == OnAirType.on_air and m.subscribed:
                movies_genred[2].append(m)
                continue

            # 5: 登録チャンネル
            if m.subscribed:
                movies_genred[4].append(m)
                continue

            # 6: 配信中
            if m.status == OnAirType.on_air:
                movies_genred[5].append(m)
                continue

            # 7: その他
            movies_genred[6].append(m)

        # リストを順番に結合する
        movies = list(itertools.chain(
            movies_genred[0],
            movies_genred[1],
            movies_genred[2],
            movies_genred[3],
            movies_genred[4],
            movies_genred[5],
            movies_genred[6],
        ))
        return movies

    except requests.exceptions.RequestException:
        logging.warning('HTTP Request failed')
        return None
