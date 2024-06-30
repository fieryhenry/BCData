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
for cc in all_ccs:
    all_gvs = tbcml.Apk.get_all_versions(cc)
    for i, gv in enumerate(all_gvs[::-1]):
        log(f"{i+1}/{len(all_gvs)}")
        apk = tbcml.Apk(gv, cc)
        log(f"{cc.value, gv.to_string()}")
        apk_path = apk.pkg_path
        item_identifier = f"jp.co.ponos.battlecats{cc.get_patching_code()}"
        api_url = f"https://s3.us.archive.org/{item_identifier}"

        file = f"{gv}.apk"
        if does_file_exist(item_identifier, file):
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

        log(f"Uploading {file} {cc}")

        # Open the file
        with open(apk_path.to_str(), "rb") as f:
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
            response = session.put(
                f"{api_url}/{file}",
                data=monitor,
                headers={"Content-Type": monitor.content_type},
            )
            # Print the response

            log(str(response.status_code))
            log(response.text)
            log("")
