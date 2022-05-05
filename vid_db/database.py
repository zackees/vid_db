# pylint: disable=all
import os
from datetime import datetime
from typing import List, Optional

from vid_db.db_full_text_search import DbFullTextSearch
from vid_db.db_sqlite_video import DbSqliteVideo  # type: ignore
from vid_db.video_info import VideoInfo

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
DB_PATH_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DB_PATH_DIR, exist_ok=True)


class Database:
    def __init__(self, db_path: str = DB_PATH_DIR) -> None:
        self.db_path = db_path
        db_path_sqlite = os.path.join(db_path, "videos.sqlite")
        db_path_fts = os.path.join(db_path, "full_text_seach")
        self.db_sqlite = DbSqliteVideo(db_path_sqlite)
        self.db_full_text_search = DbFullTextSearch(db_path_fts)

    def update_many(self, vids: List[VideoInfo]) -> None:  # type: ignore
        self.db_sqlite.insert_or_update(vids)
        self.db_full_text_search.add_videos(vids)

    def update(self, vid: VideoInfo) -> None:
        self.update_many([vid])

    def get_video_list(
        self,
        date_start: datetime,
        date_end: datetime,
        channel_name: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[VideoInfo]:
        vid_list: List[VideoInfo] = self.db_sqlite.find_videos(
            date_start, date_end, channel_name=channel_name, limit_count=limit
        )
        return vid_list

    def query_video_list(
        self,
        query_string: str,
        limit: Optional[int] = None,
    ) -> List[dict]:
        options = {}
        if limit is not None:
            options["limit"] = limit
        vids0: List[dict] = self.db_full_text_search.channel_search(
            query_string, **options
        )
        vids1: List[dict] = self.db_full_text_search.title_search(
            query_string, **options
        )
        vid_list = vids0 + vids1
        found_urls = set()
        filtered_vids = []
        for vid in vid_list:
            if vid["url"] in found_urls:
                continue
            found_urls.add(vid["url"])
            filtered_vids.append(vid)
        if limit is not None:
            filtered_vids = filtered_vids[:limit]
        return filtered_vids
