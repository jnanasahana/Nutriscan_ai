import pandas as pd

# Example unhealthy ingredients list
UNHEALTHY_INGREDIENTS = ['sugar', 'salt', 'corn syrup', 'hydrogenated', 'trans fat']

def analyze_ingredients(ingredients_df):
    """
    Analyze ingredients for health impact.
    Returns a DataFrame with flags and health summary list.
    """
    df = ingredients_df.copy()
    df['is_unhealthy'] = df['ingredient'].str.lower().apply(
        lambda x: any(uw in x for uw in UNHEALTHY_INGREDIENTS)
    )

    health_summary = []
    if df['is_unhealthy'].any():
        unhealthy_list = df[df['is_unhealthy']]['ingredient'].tolist()
        health_summary.append(f"Contains unhealthy ingredients: {', '.join(unhealthy_list)}")
    else:
        health_summary.append("No unhealthy ingredients detected ✅")

    # Overall label
    label = "Healthy ✅" if not df['is_unhealthy'].any() else "Unhealthy ❌"

    return df, health_summary


def recommend_alternatives(nutrition, scaler=None, dataset_path="data/nutrition_dataset.csv", top_k=3):
    """
    Return a list of recommended alternative products based on nutrition.
    """
    try:
        df = pd.read_csv(dataset_path)
    except FileNotFoundError:
        return []

    df['label'] = df['label'].astype(str)
    healthy_df = df[df['label'].str.lower() == 'healthy'].copy()
    if healthy_df.empty:
        return []

    # If scaler provided, use cosine similarity
    if scaler is not None:
        from sklearn.metrics.pairwise import cosine_similarity
        expected_features = scaler.feature_names_in_
        nutrition_numeric = {k: float(nutrition.get(k, 0)) for k in expected_features}
        X_healthy = scaler.transform(healthy_df[expected_features])
        user_vec = scaler.transform(pd.DataFrame([nutrition_numeric]).reindex(columns=expected_features, fill_value=0))
        sims = cosine_similarity(user_vec, X_healthy)[0]
        top_indices = sims.argsort()[::-1][:top_k]
        healthy_df = healthy_df.iloc[top_indices]

    recommendations = []
    for _, row in healthy_df.iterrows():
        recommendations.append({
            "product_name": row.get("product_name", "Unknown"),
            "label": row.get("label", "Healthy"),
            "calories": row.get("calories", 0),
            "protein": row.get("protein", 0),
            "carbohydrates": row.get("carbohydrates", 0),
            "fat": row.get("fat", 0),
            "sodium": row.get("sodium", 0),
        })
    return recommendations
