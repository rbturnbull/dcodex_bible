import re
from pathlib import Path
from bs4 import BeautifulSoup
import requests
import json

from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
from dcodex_bible.models import BibleManuscript
from imagedeck.models import Deck, DeckImageIIIF


def download_file(url, local_dir, force_download=False):
    """ 
    Download a file with a URL to a local directory.

    Normally skips a file if there is already a file with that filename in the local directory (unless force_download is True).
    Adapted from https://stackoverflow.com/a/16696317 
    """
    filename = url.split('/')[-1]
    
    local_dir = Path(local_dir)

    # Make directory if necessary
    local_dir.mkdir(parents=True, exist_ok=True)

    local_path = Path(local_dir)/filename

    # Check to see if this file already exists
    if force_download == False and local_path.exists():
        return local_path

    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
    return local_path


def get_csntm_ms(siglum: str, url_path: str, data_dir:Path):
    ms = BibleManuscript.objects.filter(siglum=f"GA{siglum}").first()
    if not ms or ms.imagedeck:
        return

    url = f"https://manuscripts.csntm.org{url_path}"
    print(f"Importing {siglum} from {url}")

    ms_data_dir = data_dir/siglum
    file = download_file(url, ms_data_dir)

    with open(file, 'r') as f:
        contents = f.read()

    soup = BeautifulSoup(contents, 'lxml')
    images = soup.find_all('img')
    if not images:
        return

    ms.imagedeck, _ = Deck.objects.update_or_create(name=f'CSNTM {siglum}')

    iiif_server_pattern = re.compile(r".*images\.csntm\.org/IIIFServer\.ashx.*")
    for image in images:
        src = ""
        if image.get("src")  and iiif_server_pattern.match(str(image['src'])):
            src = str(image['src'])
        elif image.get("data-original") and iiif_server_pattern.match(str(image['data-original'])):
            src = str(image['data-original'])
        else:
            print(f"cannot find src in image {image}")
            continue

        base = Path(src).parent.parent.parent.parent
        base_url = "https:"+str(base)
        info_url = "https:"+str(base/"info.json")
        info_path = download_file(info_url, ms_data_dir/base.name)

        with open(info_path) as f:
            info = json.load(f)
        height = info['height']
        width = info['width']
        
        print(base_url, width, height)
        image, _ = DeckImageIIIF.objects.update_or_create(base_url=base_url, defaults=dict(width=width, height=height))
        ms.imagedeck.add_image(image)

    ms.save()

class Command(BaseCommand):
    help = "Imports references to CSNTM's IIIF images."

    def add_arguments(self, parser):
        parser.add_argument(
            "cache", type=str, help="The directory to store the temporary cache files from the CSNTM."
        )

    def handle(self, *args, **options):
        data_dir = Path(options['cache'])
        file = download_file("https://manuscripts.csntm.org", data_dir)
        with open(file, 'r') as f:
            contents = f.read()
        soup = BeautifulSoup(contents, 'lxml')
        pattern = re.compile(r"/Manuscript/Group/GA_(.*)$")
        links = soup.find_all('a', href=pattern)
        for link in links:
            
            href = link['href']
            m = pattern.match(href)
            assert m is not None
            siglum = m.group(1)
            if m := re.match(r"(P?\d+).*", siglum):
                siglum = m.group(1)
            if m := re.match(r"[Ll]ect_(\d+).*", siglum):
                siglum = "l"+m.group(1)

            if not re.match(r"[Pl]?\d+$", siglum):
                raise ValueError(f"cannot understand siglum {siglum}")

            try:
                get_csntm_ms(siglum, href, data_dir)
            except Exception as err:
                print(err)
                continue



