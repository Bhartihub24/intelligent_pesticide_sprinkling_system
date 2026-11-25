# Intelligent Pesticide Sprinkling System — Prototype

## Run on Windows (VS Code)

1. Extract this ZIP.
2. Open the extracted `pest-mine` folder in VS Code.
3. Use your existing Python 3.10 environment if it already has the project dependencies installed. You do not need the Plant Disease dataset folder to run the app.
4. In the VS Code terminal, activate the environment. Example (change the path to your actual environment):

   ```powershell
   & "C:\path\to\pestenv\Scripts\Activate.ps1"
   ```

5. Run:

   ```powershell
   python -m streamlit run main.py
   ```

If you need a fresh environment, use Python 3.10 and install `requirement.txt`:

```powershell
py -3.10 -m venv pestenv
.\pestenv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirement.txt
python -m streamlit run main.py
```

## Important files

- `main.py`: Streamlit application.
- `trained_model.h5`: saved CNN model used for predictions.
- `pesticide_recommendations.py`: small disease information database.
- `Train_plant_disease.ipynb` and `Test_Plant_Disease.ipynb`: training/testing notebooks.

The app loads `trained_model.h5` from the same folder as `main.py`. It does not read the original dataset folder during normal app use. The dataset is needed only if you retrain the model or rerun the training notebook.

## Prototype capabilities

- Single plant/leaf image classification.
- Multiple uploaded sample images, each treated as a field-zone sample.
- Simple field grid and equal-zone flagged-area estimate.
- CSV export of field analysis and simulated spray plan.
- Spray quantity arithmetic using values entered by the user from a verified product label.

## Limitations (important for your presentation)

The current CNN classifies individual plant/leaf images. It is not trained for drone/aerial images, object detection, image segmentation, GPS mapping, or pixel-level infected-area measurement. The field area is an illustrative equal-zone estimate based on sample count, not a measured infected area. The spray planner is a simulation only; no drone, pump, valve, GPS, or sprayer hardware is connected. Do not present the entered application values as pesticide recommendations.
