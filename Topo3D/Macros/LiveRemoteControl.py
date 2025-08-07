import time, os, traceback

WATCHED_SCRIPT = "/home/leandropaolo1/Documents/VSCODE/Parametric-Modeling/FreecadSeries/Topo3D/remote_script.py"

def watch_and_run():
    print("🔁 Watching for:", WATCHED_SCRIPT)
    while True:
        if os.path.exists(WATCHED_SCRIPT):
            try:
                with open(WATCHED_SCRIPT, 'r') as f:
                    code = f.read()
                print("🚀 Executing remote_script.py...")
                exec(code, globals())
                os.remove(WATCHED_SCRIPT)
            except Exception as e:
                print("❌ Error running script:\n", traceback.format_exc())
        time.sleep(1)

watch_and_run()
