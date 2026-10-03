#!/usr/bin/env python3
"""LOLZ-порт, режим full, исходники: zram по умолчанию сжимает zstd (как у LOLZ).

В этом дереве нет Kconfig ZRAM_DEF_COMP, алгоритм по умолчанию зашит в zram_drv.c ("lzo").
Правка условная: zstd только если CONFIG_CRYPTO_ZSTD включён, иначе остаётся lzo, чтобы zram не сломался.
Рантайм: алгоритм можно сменить до задания disksize: echo lz4 > /sys/block/zram0/comp_algorithm
Запуск: apply_lolz_full.py <корень ядра>. Идемпотентен.
"""
import pathlib
import sys

p = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".") / "drivers/block/zram/zram_drv.c"
s = p.read_text()
old = 'static const char *default_compressor = "lzo";\n'
new = ('static const char *default_compressor =\n'
       '#if IS_ENABLED(CONFIG_CRYPTO_ZSTD)\n'
       '\t"zstd";\n'
       '#else\n'
       '\t"lzo";\n'
       '#endif\n')
if new in s:
    print("[lolz-full] zram_drv.c: уже")
elif s.count(old) == 1:
    p.write_text(s.replace(old, new))
    print("[lolz-full] zram_drv.c: компрессор по умолчанию zstd (если CRYPTO_ZSTD)")
else:
    print("[ОШИБКА] zram_drv.c: не нашёл строку default_compressor", file=sys.stderr)
    sys.exit(1)
