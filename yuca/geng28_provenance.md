# Provenance of `geng28` (the `geng` used for the order-14 K₄-free runs)

**Result.** `/lustre/proyectos/p029/busqueda_minimal/bin/geng28` on YUCA is byte-identical to `bin/geng` of the
conda-forge package **nauty 2.9.3, build `hb03c661_0`, subdir `linux-64`**.  The chain below goes from the channel's
own index to the bytes that ran; every hash was recomputed on 17 Oct 2026.

| link | evidence | value |
|---|---|---|
| channel index | `https://conda.anaconda.org/conda-forge/linux-64/repodata.json.zst`, entry `nauty-2.9.3-hb03c661_0.conda` (`provenance_geng28/repodata_entry_conda_forge_linux-64.json`) | SHA-256 `63228fa3f782c80c4730d5e42ec6d39c89d2940835325d52fe79b92da890ed2e`, MD5 `7bc7f0947d5c9ba0d576beeb9156cea3`, 6,707,226 bytes |
| package artifact | `https://conda.anaconda.org/conda-forge/linux-64/nauty-2.9.3-hb03c661_0.conda`, downloaded again | same SHA-256, MD5 and size (also the copy in the local package cache and the SHA-256 recorded by the installer in `conda-meta/` on 11 Oct 2026) |
| file list of the package | `info/paths.json` inside the artifact (`provenance_geng28/info_paths_bin_geng_labelg.json`) | `bin/geng`: SHA-256 `179508d908b1f399fde36cb0e702960150eaa8b48ba0788bc8627cbdf33ae2cb`, 395,424 bytes |
| extracted executable | `bin/geng` extracted from the artifact | SHA-256 `179508d9…`, 395,424 bytes; `strings` shows `/usr/local/src/conda/nauty-2.9.3`; `--version` prints `Nauty&Traces version 2.9301 (32 bits)` |
| executable on YUCA | probe P0 of round 3 (`probe.json`, SHA-256 `41428f3a…c494`, approved by the author) | `geng28`: SHA-256 `179508d9…`, `--version` token `2.9301` |
| source of the package | `info/recipe/meta.yaml` (`provenance_geng28/info_recipe_meta.yaml`) | `https://pallini.di.uniroma1.it/nauty2_9_3.tar.gz`, SHA-256 `9fc4edae04f88a0f5883985be3b39cf7f898fd6cc96e96b9ee25452743cc1b5b`, patch `popcount.patch`; `info/index.json`: depends `__glibc >=2.17,<3.0.a0`, `libgcc >=14` |

How the file reached YUCA (11 Oct 2026, recorded in the working transcript of that day): `bin/geng` of the local
conda environment `grafos`, created earlier that day from conda-forge with `nauty-2.9.3-hb03c661_0`
(`provenance_geng28/local_env_conda_meta_history_excerpt.txt`, `provenance_geng28/local_env_conda_meta_nauty.json`,
which list the package URL, its SHA-256 and that of `bin/geng`), was copied to a staging file, uploaded to the
user's scratch directory on YUCA and copied to `/lustre/proyectos/p029/busqueda_minimal/bin/geng28` (modification
time 2026-10-11 11:01:25 MST, 395,424 bytes).  The staging copy on YUCA no longer exists.  The label "nauty 2.8" was
attached at that upload without checking the version; it is wrong (see `yuca/README.md`).

What this does not show: that the nauty sources of the package match the release (not needed for the runs, which
depend only on the bytes).  The `labelg` used on YUCA (`/lustre/proyectos/p029/Librerias/nauty27r4/labelg`,
SHA-256 `f6a1ded5…`) is a different file from the package's `bin/labelg` (`b54cbdde…`).

Reproduce (any machine with Python 3 and the `zstandard` module):

```bash
curl -sSLO https://conda.anaconda.org/conda-forge/linux-64/nauty-2.9.3-hb03c661_0.conda
sha256sum nauty-2.9.3-hb03c661_0.conda          # 63228fa3f782c80c4730d5e42ec6d39c89d2940835325d52fe79b92da890ed2e
python3 - <<'EOF'
import hashlib, io, json, tarfile, zipfile, zstandard
z = zipfile.ZipFile("nauty-2.9.3-hb03c661_0.conda")
untar = lambda m: tarfile.open(fileobj=io.BytesIO(zstandard.ZstdDecompressor().stream_reader(io.BytesIO(z.read(m))).read()))
info = untar(next(n for n in z.namelist() if n.startswith("info-")))
pkg = untar(next(n for n in z.namelist() if n.startswith("pkg-")))
listed = next(p for p in json.load(info.extractfile("info/paths.json"))["paths"] if p["_path"] == "bin/geng")
print("paths.json :", listed["sha256"], listed["size_in_bytes"])
print("bin/geng   :", hashlib.sha256(pkg.extractfile("bin/geng").read()).hexdigest())
EOF
sha256sum /lustre/proyectos/p029/busqueda_minimal/bin/geng28     # on YUCA: the same 179508d9…
```
