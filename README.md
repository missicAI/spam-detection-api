# SpamGuard

SpamGuard checks whether an English SMS is likely to be spam. It includes a small app for trying messages and an API that other programs can call.

The project covers the whole path from preparing the data to saving and serving the trained model.

## Run the app

Use Python 3.12. On Windows, run `CAI_DAT.bat`, then `CHAY_DEMO.bat`. For the API, open `CHAY_API.bat`.

From a terminal:

```bash
python -m pip install -r requirements.txt
python train.py
python -m streamlit run app.py
```

To start the API:

```bash
python -m uvicorn spamguard.service:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/docs to try it. Send a request to `/predict` with a `text` field. Empty messages and messages over 5,000 characters are rejected.

## Training and results

The data comes from the [UCI SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms+spam+collection). Repeated messages are removed before the data is split, so the same text does not appear in both training and testing.

The model learns from 4,127 messages and is checked on another 1,032. It uses TF-IDF to turn text into numbers and Logistic Regression to choose a label.

On this test set, spam F1 is **93.08%**, precision is **91.67%**, and recall is **94.53%**. The full report and examples of mistakes are in `reports/`.

These results apply to this English SMS dataset. They do not establish how well the model works on Vietnamese messages or newer spam. The displayed probability is a model estimate, not a guarantee.

## Checks and files

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

`spamguard/training.py` prepares the data and trains the model. `service.py` loads it once when the API starts and uses it for incoming messages. Run `python train.py` after cloning to create the model file.

A Dockerfile is included for running the API in a container. It has not yet been built in the supplied validation environment.

Built with Python, pandas, scikit-learn, FastAPI and Streamlit. Code uses the MIT license. Dataset credit and its CC BY 4.0 license are in [data/ATTRIBUTION.md](data/ATTRIBUTION.md).
