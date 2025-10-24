1. 在 build_cython 時, 會先把 .py 暫時放在這個資料夾內, 避免 pyinstaller 把 .py 包進去
2. 目的是讓 pyinstaller 能把 .so 包進去, 這樣才能加密成功
