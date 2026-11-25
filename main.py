import os
import streamlit as st
import tensorflow as tf
import numpy as np
import pandas as pd
from PIL import Image
from pesticide_recommendations import get_recommendation

st.set_page_config(page_title="Intelligent Pesticide Sprinkling System", page_icon="🌱", layout="wide")

CLASS_NAMES = [
'Apple___Apple_scab','Apple___Black_rot','Apple___Cedar_apple_rust','Apple___healthy',
'Blueberry___healthy','Cherry_(including_sour)___Powdery_mildew','Cherry_(including_sour)___healthy',
'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot','Corn_(maize)___Common_rust_',
'Corn_(maize)___Northern_Leaf_Blight','Corn_(maize)___healthy','Grape___Black_rot',
'Grape___Esca_(Black_Measles)','Grape___Leaf_blight_(Isariopsis_Leaf_Spot)','Grape___healthy',
'Orange___Haunglongbing_(Citrus_greening)','Peach___Bacterial_spot','Peach___healthy',
'Pepper,_bell___Bacterial_spot','Pepper,_bell___healthy','Potato___Early_blight',
'Potato___Late_blight','Potato___healthy','Raspberry___healthy','Soybean___healthy',
'Squash___Powdery_mildew','Strawberry___Leaf_scorch','Strawberry___healthy',
'Tomato___Bacterial_spot','Tomato___Early_blight','Tomato___Late_blight','Tomato___Leaf_Mold',
'Tomato___Septoria_leaf_spot','Tomato___Spider_mites Two-spotted_spider_mite',
'Tomato___Target_Spot','Tomato___Tomato_Yellow_Leaf_Curl_Virus',
'Tomato___Tomato_mosaic_virus','Tomato___healthy'
]

MODEL_PATH = os.path.join(os.path.dirname(__file__), "trained_model.h5")

@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("trained_model.h5 was not found beside main.py.")
    return tf.keras.models.load_model(MODEL_PATH)

def predict_image(image_file):
    image_file.seek(0)
    image = Image.open(image_file).convert("RGB").resize((128, 128))
    arr = np.asarray(image, dtype=np.float32)
    arr = np.expand_dims(arr, axis=0)
    model = load_model()
    probabilities = model.predict(arr, verbose=0)[0]
    index = int(np.argmax(probabilities))
    confidence = float(probabilities[index]) * 100
    return CLASS_NAMES[index], confidence

def friendly_label(label):
    crop, disease = label.split("___", 1)
    return crop.replace("_", " ").replace(",", "") + " — " + disease.replace("_", " ").strip()

def show_recommendation(label):
    rec = get_recommendation(label)
    if not rec:
        st.info("No additional disease information is available.")
        return
    st.markdown("#### Disease information")
    a, b, c = st.columns(3)
    a.metric("Crop", rec.get("crop", "—"))
    b.metric("Disease", rec.get("disease", "—"))
    c.metric("Status", rec.get("status", "—"))
    if rec.get("message"):
        st.info(rec["message"])
    if rec.get("treatment_options"):
        st.write("**Treatment options recorded in the project database**")
        st.write(", ".join(rec["treatment_options"]))
    if rec.get("management_practices"):
        st.write("**Management practices**")
        for item in rec["management_practices"]:
            st.write("• " + item)
    if rec.get("note"):
        st.warning(rec["note"])
    if rec.get("source"):
        st.caption("Information source recorded in project: " + rec["source"])

def home_page():
    st.title("🌱 Intelligent Pesticide Sprinkling System")
    st.subheader("AI-assisted crop disease monitoring and precision-spraying simulation")
    image_path = os.path.join(os.path.dirname(__file__), "home_page.jpeg")
    if os.path.exists(image_path):
        st.image(image_path, use_column_width=True)
    st.markdown("""
    This prototype demonstrates a software workflow for monitoring crop health and planning
    targeted treatment. Upload sample plant images, review the CNN predictions, and simulate
    a zone-wise spray plan.
    """)
    x, y, z = st.columns(3)
    x.metric("Disease classes", "38")
    y.metric("Image input", "JPG / JPEG / PNG")
    z.metric("Hardware", "Simulation only")
    st.info("Start with **Single Image Recognition** or upload several samples in **Field Monitoring**.")

def recognition_page():
    st.title("🔍 Single Image Recognition")
    st.write("Upload a plant/leaf image to run the saved CNN model.")
    uploaded = st.file_uploader("Choose a plant image", type=["jpg", "jpeg", "png"], key="single_upload")
    if uploaded:
        st.image(uploaded, caption="Uploaded image", use_column_width=True)
        if st.button("Analyse image", type="primary"):
            with st.spinner("Analysing image..."):
                label, confidence = predict_image(uploaded)
            st.success("Prediction: " + friendly_label(label))
            st.metric("Model confidence for this prediction", f"{confidence:.2f}%")
            show_recommendation(label)
            st.caption("Confidence is the model's output for this uploaded image; it is not a guarantee of field diagnosis.")

def field_page():
    st.title("🛰️ Field Monitoring")
    st.write("Upload several plant/leaf images. For this prototype, each image represents one sample from a field zone.")
    uploads = st.file_uploader("Upload multiple sample images", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="field_uploads")
    area = st.number_input("Total field area (acres)", min_value=0.01, value=1.0, step=0.1)
    if not uploads:
        st.info("Upload two or more sample images to view the field-monitoring demonstration.")
        return
    if st.button("Analyse field samples", type="primary"):
        rows = []
        progress = st.progress(0)
        for i, file in enumerate(uploads):
            label, conf = predict_image(file)
            healthy = label.lower().endswith("healthy")
            rows.append({
                "Zone": f"Zone {i+1}",
                "Image": file.name,
                "Prediction": friendly_label(label),
                "Status": "Healthy sample" if healthy else "Flagged for review",
                "Confidence": round(conf, 2),
                "Needs review": not healthy
            })
            progress.progress((i + 1) / len(uploads))
        st.session_state["field_rows"] = rows
        st.session_state["field_area"] = float(area)
    rows = st.session_state.get("field_rows")
    if not rows:
        return
    df = pd.DataFrame(rows)
    total = len(df)
    flagged = int(df["Needs review"].sum())
    share = flagged / total * 100
    zone_area = float(st.session_state.get("field_area", area)) / total
    estimated_area = flagged * zone_area
    a, b, c = st.columns(3)
    a.metric("Samples analysed", total)
    b.metric("Zones flagged", f"{flagged}/{total}")
    c.metric("Flagged sample share", f"{share:.1f}%")
    st.subheader("Zone analysis")
    st.dataframe(df.drop(columns=["Needs review"]))
    # st.dataframe(df.drop(columns=["Needs review"]), use_column_width=True)
    st.subheader("Illustrative field-zone map")
    cols = st.columns(min(4, total))
    for i, row in enumerate(rows):
        with cols[i % len(cols)]:
            if row["Needs review"]:
                st.error(f'{row["Zone"]}\n\nDisease prediction')
            else:
                st.success(f'{row["Zone"]}\n\nHealthy prediction')
    st.metric("Estimated area represented by flagged samples", f"{estimated_area:.2f} acres")
    st.warning("Important limitation: this is an equal-sized-zone sample estimate, not image segmentation or GPS-based measurement. Each uploaded leaf image is treated as one zone sample. It does not measure the actual infected pixels or field boundary.")
    st.download_button("Download field analysis CSV", df.drop(columns=["Needs review"]).to_csv(index=False), "field_analysis.csv", "text/csv")

def spray_page():
    st.title("🚿 Precision Spray Plan Simulator")
    st.write("Create an illustrative list of zones to inspect/treat based on the latest Field Monitoring analysis.")
    rows = st.session_state.get("field_rows")
    if not rows:
        st.info("Run Field Monitoring first. The simulator uses its flagged-zone results.")
        return
    flagged = [r for r in rows if r["Needs review"]]
    if not flagged:
        st.success("No zones were flagged in the current sample set. Continue routine monitoring.")
        return
    st.write("**Zones flagged by the image classifier:** " + ", ".join(r["Zone"] for r in flagged))
    st.caption("Enter application values only from the exact registered product label or a qualified agricultural adviser. This tool does not recommend a pesticide or dose.")
    rate = st.number_input("Verified product rate (mL per litre of water)", min_value=0.0, value=0.0, step=0.1)
    water = st.number_input("Verified spray-water volume (litres per acre)", min_value=0.0, value=0.0, step=1.0)
    total_area = float(st.session_state.get("field_area", 1.0))
    area_per_zone = total_area / len(rows)
    coverage = len(flagged) * area_per_zone
    st.metric("Illustrative flagged-zone area", f"{coverage:.2f} acres")
    if rate > 0 and water > 0:
        product_ml = coverage * water * rate
        st.metric("Calculated product quantity for entered values", f"{product_ml:.1f} mL")
    else:
        st.info("Enter both verified label values to calculate an illustrative quantity.")
    plan = pd.DataFrame([{
        "Zone": r["Zone"],
        "Action": "Inspect and consider targeted treatment under expert/label guidance",
        "Sample prediction": r["Prediction"],
        "Estimated zone area (acres)": round(area_per_zone, 3)
    } for r in flagged])
    st.subheader("Simulated zone instructions")
    st.dataframe(plan)
    # st.dataframe(plan, use_column_width=True)
    st.download_button("Download simulated spray plan CSV", plan.to_csv(index=False), "simulated_spray_plan.csv", "text/csv")
    st.warning("This is a planning simulation only. No pump, drone, GPS, valve, or sprayer is connected. Do not use this calculation as a real-world pesticide prescription.")

def about_page():
    st.title("ℹ️ About the Project")
    st.markdown("""
    **Project objective:** demonstrate an AI-assisted workflow that can support crop-disease monitoring and targeted pesticide-spraying planning.

    **Implemented in this software prototype**
    - Saved CNN model for classifying uploaded plant/leaf images into 38 classes.
    - Single-image disease recognition.
    - Multiple sample-image analysis with zone labels and a simple field-grid display.
    - A transparent equal-zone estimate of the area represented by flagged samples.
    - Downloadable, simulated zone-wise spray instructions.

    **Not yet implemented**
    - Live drone/camera feed, GPS coordinates, field boundary mapping.
    - Aerial-image disease detection or pixel-level segmentation.
    - Verified crop-specific pesticide dosing database for all diseases.
    - Physical IoT controller, pump/valves, or actual automated spraying.

    **Dataset/model note:** the CNN uses the already-trained `trained_model.h5` file. The original training dataset is only required if you want to retrain the model or rerun the training notebook.
    """)
    st.warning("The current CNN is trained for plant/leaf image classification. The field-zone workflow is a prototype simulation and should not be described as a validated drone-based field measurement system.")

def main():
    st.sidebar.title("🌱 Project Dashboard")
    page = st.sidebar.radio("Navigate", ["Home", "Single Image Recognition", "Field Monitoring", "Spray Plan Simulator", "About"])
    st.sidebar.markdown("---")
    st.sidebar.caption("Software prototype • Hardware integration is future work")
    if page == "Home":
        home_page()
    elif page == "Single Image Recognition":
        recognition_page()
    elif page == "Field Monitoring":
        field_page()
    elif page == "Spray Plan Simulator":
        spray_page()
    else:
        about_page()

if __name__ == "__main__":
    main()
