from tbcml import core

# requires latest version of tbcml from github
# https://github.com/fieryhenry/TBCModLoader#from-source
# currently working as of commit 64fb93a


def do(cc: core.CountryCode):
    gv = core.GameVersion.from_string_latest("latest", cc)
    print(gv.to_string())

    apk = core.Apk(gv, cc)
    apk.download()
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


do(core.CountryCode.EN)  # Change this to download a different version
