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
        parser.add_argument(
            "-p",
            "--path",
            default=getattr(settings, "GEOIP_PATH", None),
            help="Path to store GeoIP2 database files. The default is GEOIP_PATH in settings.py.",
        )

    def handle(
        self,
        maxmind_license_key: str,
        maxmind_geoip_download_base_url: str,
        path: str | None,
        *args,
        **options,
    ) -> None:
        if not path:
            return self.stderr.write("GEOIP_PATH is not set in settings.py. Aborting.")

        dbpath = Path(path)

        if not dbpath.exists():
            dbpath.mkdir(parents=True)

        for basename in ("GeoLite2-City", "GeoLite2-Country"):
            self.download_geoip_db(dbpath, maxmind_license_key, maxmind_geoip_download_base_url, basename)

        self.stdout.write("GeoIP2 database files have been downloaded and extracted successfully.")

    def download_geoip_db(
        self, dbpath: Path, maxmind_license_key: str, maxmind_geoip_download_base_url: str, edition: str
    ) -> None:
        basename: str = f"{edition}.tar.gz"
        download_url: str = self.build_download_url(maxmind_geoip_download_base_url, maxmind_license_key, edition)

        fp = dbpath / basename
        self.stdout.write(f"Downloading {basename} to {fp}...")
        urllib.request.urlretrieve(download_url, str(fp))  # nosec
        self.stdout.write(f"Downloaded {fp}. Extracting...")
        self.extract_tar(dbpath, fp)
        self.stdout.write(f"Extracted {fp}. Cleaning...")
        fp.unlink()
        self.stdout.write(f"Cleaned {fp}.")

    def build_download_url(self, maxmind_geoip_download_base_url: str, maxmind_license_key: str, edition: str) -> str:
        return f"{maxmind_geoip_download_base_url}?{urlencode({'edition_id': edition, 'license_key': maxmind_license_key, 'suffix': 'tar.gz'})}"

    def extract_tar(self, dbpath: Path, tar_path: Path) -> None:
        with tarfile.open(tar_path) as tarball:
            for tarinfo in tarball:
                if tarinfo.name.endswith(".mmdb"):
                    tarinfo.name = os.path.basename(tarinfo.name)
                    tarball.extract(tarinfo, path=str(dbpath))
