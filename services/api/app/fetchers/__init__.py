"""All job sources. To add a source: write a Fetcher subclass and add it here."""

from app.fetchers.arbeitnow import ArbeitnowFetcher
from app.fetchers.base import Fetcher, RawJob
from app.fetchers.remoteok import RemoteOKFetcher
from app.fetchers.remotive import RemotiveFetcher

ALL_FETCHERS: list[Fetcher] = [
    ArbeitnowFetcher(),
    RemoteOKFetcher(),
    RemotiveFetcher(),
]

__all__ = ["ALL_FETCHERS", "Fetcher", "RawJob"]
