import os, time, threading, traceback

WATCHED_SCRIPT = "/home/leandropaolo1/Documents/VSCODE/Parametric-Modeling/FreecadSeries/Macros/HoneyComb001.py"
    
def geometry_push_worker():
    print("🔁 [GeometryPush] Watching:", WATCHED_SCRIPT)
    while True:
        try:
            if os.path.exists(WATCHED_SCRIPT):
                with open(WATCHED_SCRIPT, 'r') as f:
                    code = f.read()
                print("🚀 [GeometryPush] Executing remote_script.py...")
                exec(code, globals())
                os.remove(WATCHED_SCRIPT)
        except Exception:
            print("❌ [GeometryPush] Error:\n", traceback.format_exc())
        time.sleep(1)

# Run watcher in a separate thread so it doesn't block FreeCAD GUI
thread = threading.Thread(target=geometry_push_worker, daemon=True)
thread.start()
print("✅ [GeometryPush] Running in background.")
