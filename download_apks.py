from tbcml import core

# https://github.com/fieryhenry/TBCModLoader
# currently working as of commit 18dcd32


def do(cc: core.CountryCode, gv: core.GameVersion):
    print(cc.get_code())
    print(gv.to_string())

    output_path = (
        core.Path("APKs")
        .add(cc.get_code())
        .generate_dirs()
        .add(gv.to_string() + ".apk")
    )

    apk = core.Apk(gv, cc)
    success = apk.download()  # progress=None)
    if not success:
        print("Failed to download apk")
        return

    apk.apk_path.copy(output_path)


all_ccs = core.CountryCode.get_all()
for cc in all_ccs:
    all_gvs = core.Apk.get_all_versions(cc)
    for gv in all_gvs:
        do(cc, gv)
