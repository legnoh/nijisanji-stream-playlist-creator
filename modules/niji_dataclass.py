from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
import datetime
from enum import Enum

class Liver(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra='allow')
    external_id: Optional[str] = Field(default=None, alias='external-id')
    id: Optional[str] = None

class Channel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra='allow')
    name: Optional[str] = None
    thumbnail_url: Optional[str] = Field(default=None, alias='thumbnail-url')
    main: Optional[bool] = None
    id: Optional[str] = None
    liver: Optional[Liver] = None

class OnAirType(Enum):
    not_on_air = "not_on_air"
    on_air = "on_air"

class Stream(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra='allow')
    title: Optional[str] = None
    url: Optional[str] = None
    fallback_thumbnail_url: Optional[str] = Field(default=None, alias='fallback-thumbnail-url')
    start_at: Optional[datetime.datetime] = Field(default=None, alias='start-at')
    end_at: Optional[datetime.datetime] = Field(default=None, alias='end-at')
    status: Optional[OnAirType] = None
    id: Optional[str] = None
    platform: Optional[str] = None
    channel: Optional[Channel] = None
    event_livers: Optional[list[Liver]] = Field(default=None, alias='event-livers')
    youtube_video_id: Optional[str] = None
    subscribed: Optional[bool] = None
    lang: Optional[str] = None
    keyword_match: Optional[bool] = None

class PageProps(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra='allow')
    streams: list[Stream]

class Props(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra='allow')
    page_props: PageProps = Field(alias='pageProps')

class RootJSON(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra='allow')
    props: Props
