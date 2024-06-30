import tbcml

# https://github.com/fieryhenry/tbcml
# currently working as of commit https://github.com/fieryhenry/tbcml/commit/e716282adcbed53c1bac034fe7a5d66ff396e1c4


def do(cc: tbcml.CountryCode):
    print(cc.get_code())
    gv = tbcml.GameVersion.from_string_latest("latest", cc)
    print(gv.to_string())

    apk = tbcml.Apk(gv, cc)
    res = apk.download()  # progress=None)
    if not res:
        print(res.error)
        return
    print("Downloaded apk")
    res = apk.extract(use_apktool=False)
    if not res:
        print(res.error)
        return

    print("Extracted apk")

    folder = tbcml.Path(f"{gv.to_string()}{cc.get_code()}")
    if not folder.exists():
        game_data = tbcml.GamePacks.from_pkg(apk, all_langs=True)

        packnames = [
            "DataLocal",
            "resLocal",
            "resLocal_es",
            "resLocal_it",
            "resLocal_fr",
            "resLocal_de",
            "resLocal_th",
        ]

        for packname in packnames:
            pack = game_data.get_pack(packname)
            if pack is None:
                continue
            pack.extract(folder)

        print("Extracted game data")

    server_path = tbcml.Path(f"{cc.get_code()}_server")

    if cc == tbcml.CountryCode.EN:
        langs = tbcml.Language.get_all()
        langs += [None]
        for lang in langs:
            print(lang or "en")
            res = apk.download_server_files(lang=lang, display=True)
    else:
        res = apk.download_server_files(display=True)

    if not res:
        print(res.error)
        return

    apk.get_server_path().copy_tree(server_path)
    print("Downloaded server data")

    delete_old(cc, gv)
    update_latest_txt(cc, gv)
    print("Updated latest.txt")


def delete_old(cc: tbcml.CountryCode, latest_version: tbcml.GameVersion):
    all_paths: list[tbcml.Path] = []
    for folder in tbcml.Path(".").get_dirs():
        if folder.get_file_name().endswith(cc.get_code()):
            all_paths.append(folder)

    for path in all_paths:
        if path.get_file_name() == f"{latest_version.to_string()}{cc.get_code()}":
            continue
        path.remove()


def update_latest_txt(cc: tbcml.CountryCode, latest_version: tbcml.GameVersion):
    path = tbcml.Path("latest.txt")
    if not path.exists():
        path.create()
    lines = path.read().to_str().split("\n")
    if len(lines) < 4:
        lines = ["", "", "", ""]
    index = 0
    if cc == tbcml.CountryCode.EN:
        index = 0
    elif cc == tbcml.CountryCode.JP:
        index = 1
    elif cc == tbcml.CountryCode.KR:
        index = 2
    elif cc == tbcml.CountryCode.TW:
        index = 3
    lines[index] = latest_version.to_string() + cc.get_code()
    path.write(tbcml.Data("\n".join(lines).encode("utf-8")))


def update_all():
    for cc in tbcml.CountryCode.get_all():
        do(cc)


if __name__ == "__main__":
    update_all()
