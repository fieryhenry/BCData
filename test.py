from typing import Any
import tbcml


def run(version: tbcml.GV):
    print(version)
    if version <= "7.4.2" or version >= "11.3.0":
        return
    apk = tbcml.Apk(version, "en")
    apk.download()
    apk.extract()

    for file in apk.get_assets_folder_path().get_files_recursive():
        if file.to_str().endswith(".cpp") or file.to_str().endswith(".h"):
            print(file.to_str())


versions = tbcml.Apk.get_all_versions(tbcml.CountryCode.EN)
# versions.reverse()

funcs: list[Any] = []
args: list[Any] = []

for version in versions:
    funcs.append(run)
    args.append((version,))

tbcml.run_in_threads(funcs, args, 1)
