from tbcml import core

# https://github.com/fieryhenry/TBCModLoader
# currently working as of commit 18dcd32


def do(cc: core.CountryCode):
    print(cc.get_code())
    gv = core.GameVersion.from_string_latest("latest", cc)
    print(gv.to_string())

    apk = core.Apk(gv, cc)
    success = apk.download()  # progress=None)
    if not success:
        print("Failed to download apk")
        return
    apk.extract()

    game_data = core.GamePacks.from_apk(apk)

    packnames = [
        "DataLocal",
        "resLocal",
        "resLocal_es",
        "resLocal_it",
        "resLocal_fr",
        "resLocal_de",
        "resLocal_th",
    ]

    folder = core.Path(f"{gv.to_string()}{cc.get_code()}")

    for packname in packnames:
        pack = game_data.get_pack(packname)
        if pack is None:
            continue
        pack.extract(folder)

    server_path = core.Path(f"{cc.get_code()}_server")

    apk.download_server_files(copy=True)
    apk.get_server_path(apk.country_code).copy_tree(server_path)

    delete_old(cc)
    update_latest_txt(cc)


def delete_old(cc: core.CountryCode):
    all_paths: list[core.Path] = []
    for folder in core.Path(".").get_dirs():
        if folder.get_file_name().endswith(cc.get_code()):
            all_paths.append(folder)

    latest_version = core.GameVersion.from_string_latest("latest", cc)
    for path in all_paths:
        if path.get_file_name() == f"{latest_version.to_string()}{cc.get_code()}":
            continue
        path.remove()


def update_latest_txt(cc: core.CountryCode):
    latest_version = core.GameVersion.from_string_latest("latest", cc)
    path = core.Path("latest.txt")
    if not path.exists():
        path.create()
    lines = path.read().to_str().split("\n")
    if len(lines) < 4:
        lines = ["", "", "", ""]
    index = 0
    if cc == core.CountryCode.EN:
        index = 0
    elif cc == core.CountryCode.JP:
        index = 1
    elif cc == core.CountryCode.KR:
        index = 2
    elif cc == core.CountryCode.TW:
        index = 3
    lines[index] = latest_version.to_string() + cc.get_code()
    path.write(core.Data("\n".join(lines).encode("utf-8")))


def update_all():
    for cc in core.CountryCode.get_all():
        do(cc)


if __name__ == "__main__":
    # update_all()
    do(core.CountryCode.EN)
