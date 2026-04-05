"""Flask HealthTwin entry point."""
# ── MUST be set before ANY import that may load transformers/keras ──────────
import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"        # use tf-keras, not Keras 3
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"      # suppress oneDNN verbose log
# ────────────────────────────────────────────────────────────────────────────

from flask_app import create_app
import threading

if __name__ == '__main__':
    app = create_app()

    # Pre-warm the brain tumor model in a background thread so the first
    # prediction request doesn't stall while TensorFlow initialises.
    def _prewarm():
        try:
            from flask_app.ml_models import _get_brain_tumor_model
            _get_brain_tumor_model()
        except Exception:
            pass
    threading.Thread(target=_prewarm, daemon=True).start()

    # use_reloader=False is critical: Flask's reloader kills the worker when
    # TensorFlow starts up (heavy import + sub-process spawning), which drops
    # any in-flight HTTP request and causes a "Network error" on the client.
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
