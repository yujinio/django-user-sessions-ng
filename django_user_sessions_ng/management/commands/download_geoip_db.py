import os
import tarfile
import urllib.request
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.utils.http import urlencode

DEFAULT_MAXMIND_GEOIP_DOWNLOAD_BASE_URL = "https://download.maxmind.com/app/geoip_download"


class Command(BaseCommand):
    help = "Download or update existing GeoIP2 database files."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("-k", "--maxmind-license-key", required=True)
        parser.add_argument(
            "-u",
            "--maxmind-geoip-download-base-url",
            default=DEFAULT_MAXMIND_GEOIP_DOWNLOAD_BASE_URL,
            help=f"Base URL for downloading GeoIP2 database files. The default is {DEFAULT_MAXMIND_GEOIP_DOWNLOAD_BASE_URL}.",
        )

    def handle(self, maxmind_license_key: str, maxmind_geoip_download_base_url: str, *args, **options) -> None:
        if not (db_path := getattr(settings, "GEOIP_PATH", None)):
            return self.stderr.write("GEOIP_PATH is not set in settings.py. Aborting.")

        db_path = Path(db_path)

        if not db_path.exists():
            db_path.mkdir(parents=True)

        for basename, url in (
            (
                "GeoLite2-City.tar.gz",
                self.get_download_url(
                    maxmind_geoip_download_base_url,
                    maxmind_license_key,
                    "GeoLite2-City",
                ),
            ),
            (
                "GeoLite2-Country.tar.gz",
                self.get_download_url(
                    maxmind_geoip_download_base_url,
                    maxmind_license_key,
                    "GeoLite2-Country",
                ),
            ),
        ):
            fp = db_path / basename
            self.stdout.write(f"Downloading {basename} to {fp}...")
            urllib.request.urlretrieve(url, str(fp))
            self.stdout.write(f"Downloaded {fp}. Extracting...")
            self.extract_tar(db_path, fp)
            self.stdout.write(f"Extracted {fp}. Clealing...")
            fp.unlink()
            self.stdout.write(f"Cleaned.")

    @staticmethod
    def get_download_url(maxmind_geoip_download_base_url: str, maxmind_license_key: str, edition: str) -> str:
        return f"{maxmind_geoip_download_base_url}?{urlencode({'edition_id': edition, 'license_key': maxmind_license_key, 'suffix': 'tar.gz'})}"

    def extract_tar(self, db_path: Path, tar_path: Path) -> None:
        with tarfile.open(tar_path) as tarball:
            for tarinfo in tarball:
                if tarinfo.name.endswith(".mmdb"):
                    tarinfo.name = os.path.basename(tarinfo.name)
                    tarball.extract(tarinfo, path=str(db_path))
