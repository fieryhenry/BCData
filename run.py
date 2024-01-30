import tbcml

# https://github.com/fieryhenry/tbcml/tree/new-structure
# currently working as of commit https://github.com/fieryhenry/tbcml/commit/e716282adcbed53c1bac034fe7a5d66ff396e1c4


def do(cc: tbcml.CountryCode):
    print(cc.get_code())
    gv = tbcml.GameVersion.from_string_latest("latest", cc)
    print(gv.to_string())

    apk = tbcml.Apk(gv, cc)
    success = apk.download()  # progress=None)
    if not success:
        print("Failed to download apk")
        return
    apk.extract()

    game_data = tbcml.GamePacks.from_apk(apk)

    packnames = [
        "DataLocal",
        "resLocal",
        "resLocal_es",
        "resLocal_it",
        "resLocal_fr",
        "resLocal_de",
        "resLocal_th",
    ]

    folder = tbcml.Path(f"{gv.to_string()}{cc.get_code()}")

    for packname in packnames:
        pack = game_data.get_pack(packname)
        if pack is None:
            continue
        pack.extract(folder)

    server_path = tbcml.Path(f"{cc.get_code()}_server")

    apk.download_server_files()
    apk.get_server_path().copy_tree(server_path)

    delete_old(cc)
    update_latest_txt(cc)


def delete_old(cc: tbcml.CountryCode):
    all_paths: list[tbcml.Path] = []
    for folder in tbcml.Path(".").get_dirs():
        if folder.get_file_name().endswith(cc.get_code()):
            all_paths.append(folder)

    latest_version = tbcml.GameVersion.from_string_latest("latest", cc)
    for path in all_paths:
        if path.get_file_name() == f"{latest_version.to_string()}{cc.get_code()}":
            continue
        path.remove()


def update_latest_txt(cc: tbcml.CountryCode):
    latest_version = tbcml.GameVersion.from_string_latest("latest", cc)
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
    # update_all()
    do(tbcml.CountryCode.EN)
