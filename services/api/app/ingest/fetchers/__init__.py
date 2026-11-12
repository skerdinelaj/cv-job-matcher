"""All job sources. To add a source: write a Fetcher subclass and add it here."""

from app.ingest.fetchers.arbeitnow import ArbeitnowFetcher
from app.ingest.fetchers.base import Fetcher, RawJob
from app.ingest.fetchers.remoteok import RemoteOKFetcher
from app.ingest.fetchers.remotive import RemotiveFetcher

ALL_FETCHERS: list[Fetcher] = [
    ArbeitnowFetcher(),
    RemoteOKFetcher(),
    RemotiveFetcher(),
]

__all__ = ["ALL_FETCHERS", "Fetcher", "RawJob"]
