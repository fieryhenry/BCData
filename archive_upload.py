from typing import Callable
import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from clint.textui.progress import Bar as ProgressBar
import tbcml
import os
import dotenv


def log(message: str) -> None:
    print(message)
    path = os.path.join(os.path.dirname(__file__), "archive_upload.log")
    with open(path, "a") as f:
        f.write(message + "\n")


def create_callback(encoder: MultipartEncoder) -> Callable[[MultipartEncoder], None]:
    encoder_len = encoder.len
    bar = ProgressBar(expected_size=encoder_len, filled_char="=", width=20)

    def callback(monitor: MultipartEncoderMonitor) -> None:
        bar.show(monitor.bytes_read)

    return callback


def does_file_exist(identifier: str, filename: str) -> bool:
    url = f"https://archive.org/download/{identifier}/{filename}"
    response = requests.head(url, allow_redirects=True)
    return response.status_code == 200

def get_all_files(identifier: str) -> list[str]:
    url = f"https://archive.org/metadata/{identifier}"
    response = requests.get(url)

    if response.status_code != 200:
        return

    metadata = response.json()
    files = metadata.get('files', [])
    file_list: list[str] = []
    for file in files:
        file_list.append(file.get("name", ""))

    return file_list


dotenv.load_dotenv()

# Set your Archive.org API key and the identifier of the item you want to upload to
api_key = os.getenv("ARCHIVE_API_KEY")

# URL for the Archive.org API endpoint
# Path to the folder containing the files you want to upload

# Create a session and set the API key in the headers
session = requests.Session()
session.headers.update({"authorization": f"LOW {api_key}"})

all_ccs = [
    tbcml.CountryCode.EN,
    tbcml.CountryCode.JP,
    tbcml.CountryCode.KR,
    tbcml.CountryCode.TW,
]


def upload_apks(cc: tbcml.CountryCode):
    all_gvs = tbcml.Apk.get_all_versions(cc)
    item_identifier = f"jp.co.ponos.battlecats{cc.get_patching_code()}"

    all_files = get_all_files(item_identifier)
    for i, gv in enumerate(all_gvs[::-1]):
        log(f"{i+1}/{len(all_gvs)}")
        apk = tbcml.Apk(gv, cc)
        log(f"{cc.value, gv.to_string()}")
        apk_path = apk.pkg_path
        api_url = f"https://s3.us.archive.org/{item_identifier}"

        file = f"{gv}.apk"
        if file in all_files:
            log(f"Skipping {file} {cc} as it already exists")
            continue

        log(f"Downloading {file} {cc}")
        apk.download()

        if not (res := tbcml.Apk.is_apksigner_installed()):
            log("apksigner not found")
            log(str(res))
            continue

        if apk.is_modded or not tbcml.Apk.is_original(apk_path):
            log(f"Skipping {file} {cc} as it is not original")
            continue

        upload_file(cc, apk_path, api_url, file, all_files)

    return all_gvs


def upload_server_files(latest_gv: tbcml.GameVersion, cc: tbcml.CountryCode):
    apk = tbcml.Apk(latest_gv, cc)
    res = apk.download()
    if not res:
        log(str(res.error))
        return
    res = apk.extract(use_apktool=False)
    if not res:
        log(str(res.error))
        return

    langs = [None]
    if cc == tbcml.CountryCode.EN:
        langs += tbcml.Language.get_all()

    for lang in langs:
        log(lang.value if lang else cc.value)
        res = apk.download_server_files(lang=lang, display=True)

        if not res:
            log(str(res.error))
            return

    upload_directory(
        cc,
        apk.get_server_path(),
        f"jp.co.ponos.battlecats{cc.get_patching_code()}",
    )


def upload_directory(cc: tbcml.CountryCode, path: tbcml.Path, identifier: str):
    log(f"Uploading {path} {cc}")

    all_files = get_all_files(identifier)


    # Upload all the files in the directory
    for file in path.get_files():
        upload_file(cc, file, identifier, file.get_file_name(), all_files)


def upload_file(cc: tbcml.CountryCode, path: tbcml.Path, identifier: str, file: str, all_files: list[str]):
    log(f"Uploading {file} {cc}")


    if file in all_files or does_file_exist(identifier, file):
        log(f"Already exists!")
        return

    api_url = f"https://s3.us.archive.org/{identifier}"

    # Open the file
    with open(path.to_str(), "rb") as f:
        # Upload the file
        # response = session.put(f"{api_url}/{file}", data=f, stream=True)
        # Create a multipart encoder
        encoder = MultipartEncoder(
            fields={
                "file": (file, f, "application/octet-stream"),
                "metadata": '{"collection": "opensource"}',
            }
        )
        callback = create_callback(encoder)
        # Create a monitor to track the progress of the upload
        monitor = MultipartEncoderMonitor(encoder, callback)
        # Upload the file
        try:
            response = session.put(
                f"{api_url}/{file}",
                data=monitor,
                headers={"Content-Type": monitor.content_type},
            )
        except Exception as e:
            print(e)
            return
        # Print the response

        log(str(response.status_code))
        log(response.text)
        log("")


for cc in all_ccs:
    all_gvs = upload_apks(cc)
    latest_gv = all_gvs[-1]
    print(latest_gv)
    upload_server_files(latest_gv, cc)
