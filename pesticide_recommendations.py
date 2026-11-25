
# Disease-specific pesticide and management information

PESTICIDE_DATABASE = {
    "Tomato___Early_blight": {
        "crop": "Tomato",
        "disease": "Early Blight",
        "causal_organism": "Alternaria solani",

        "treatment_options": [
            "Mancozeb",
            "Chlorothalonil"
        ],

        "management_practices": [
            "Remove and destroy infected plant debris.",
            "Use disease-free seeds.",
            "Practice crop rotation.",
            "Monitor plants regularly for disease symptoms."
        ],

        "source": "ICAR Kharif Agro-Advisory 2025 and TNAU Agritech Portal",

        "note": (
            "Select a suitable registered product and follow its "
            "current label instructions. Confirm the formulation, "
            "dose, application interval and pre-harvest waiting period "
            "with an agricultural expert."
        )
    }
}


def get_disease_details(class_label):

    if "___" not in class_label:
        return None

    crop, disease = class_label.split("___", 1)

    crop = crop.replace("_", " ").strip()
    disease = disease.replace("_", " ").strip()

    status = "Healthy" if disease.lower() == "healthy" else "Disease Detected"

    return {
        "crop": crop,
        "disease": disease,
        "status": status
    }


def get_recommendation(class_label):

    details = get_disease_details(class_label)

    if details is None:
        return None

    if details["status"] == "Healthy":
        details["treatment_options"] = []
        details["management_practices"] = [
            "Continue regular crop monitoring.",
            "Maintain proper irrigation and plant nutrition.",
            "Remove dead or damaged leaves when appropriate."
        ]
        details["message"] = "No disease-specific pesticide treatment is indicated."
        return details

    recommendation = PESTICIDE_DATABASE.get(class_label)
    # print("-----------------------------")
    # print(recommendation)

    if recommendation is None:
        details["treatment_options"] = []
        details["management_practices"] = []
        details["message"] = (
            "No verified recommendation is currently available "
            "in the project database for this disease."
        )
        return details

    result = details.copy()
    # print("-----------------------------")
    # print(result)
    result.update(recommendation)
    # print("-----------------------------")
    # print(result)
    # print("-----------------------------")

    return result
