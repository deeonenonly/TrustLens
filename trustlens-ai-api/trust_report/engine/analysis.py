def calculate_overall_analysis(individual_ingredients, unknown_ingredients):

    """
    Calculates product-level TrustLens analysis from all ingredients.

    STATUS CODES:
    0 = Fully executed
    1 = Unable to analyse
    2 = Partial success

    Current input contains ingredient names only, not quantities.

    Therefore, quantity-dependent ingredients such as sugar and salt
    receive smaller presence-based penalties. They are NOT treated as
    exceeding unhealthy thresholds unless quantity data is available.
    """

    # --------------------------------------------------
    # NO RECOGNIZED INGREDIENTS
    # --------------------------------------------------

    if not individual_ingredients:

        return {
            "overall_trust_score": 0,

            "status": 1,

            "overall_safety_adult": {
                "score": 0,
                "remark": (
                    "No recognized ingredients were available for analysis."
                )
            },

            "overall_safety_child": {
                "score": 0,
                "remark": (
                    "No recognized ingredients were available for analysis."
                )
            },

            "overall_safety_pregnancy": {
                "score": 0,
                "remark": (
                    "No recognized ingredients were available for analysis."
                )
            },

            "overall_flags": [
                "NO_MATCHED_INGREDIENTS"
            ],

            "overall_remarks": (
                "The product cannot be reliably evaluated because its "
                "ingredients were not found in the TrustLens database."
            ),

            "key_concerns": [],

            "positive_aspects": []
        }

    # --------------------------------------------------
    # EXECUTION STATUS
    # --------------------------------------------------

    if unknown_ingredients:
        execution_status = 2
    else:
        execution_status = 0

    # --------------------------------------------------
    # BASE SCORE
    # --------------------------------------------------

    scores = [
        item.get("individual_trust_score", 0)
        for item in individual_ingredients
        if isinstance(
            item.get("individual_trust_score"),
            (int, float)
        )
    ]

    if scores:
        average_score = sum(scores) / len(scores)
        overall_score = average_score * 10
    else:
        overall_score = 0

    # --------------------------------------------------
    # COLLECT ALL FLAGS FROM ALL INGREDIENTS
    # --------------------------------------------------

    all_flags = []

    for item in individual_ingredients:

        flags = item.get("flags", [])

        if isinstance(flags, list):
            all_flags.extend(flags)

    unique_flags = list(set(all_flags))

    # --------------------------------------------------
    # FLAG GROUPS
    # --------------------------------------------------

    # Serious concerns even if exact quantity is unavailable.
    high_concern_flags = [
        "PARTIALLY_HYDROGENATED",
        "PARTIALLY_HYDROGENATED_OIL",
        "TRANS_FAT_CONCERN",
        "KNOWN_HAZARDOUS_ADDITIVE"
    ]

    # Quantity-dependent concerns.
    quantity_dependent_flags = [
        "ADDED_SUGAR",
        "HIGH_SODIUM_QUANTITY_FLAG",
        "SODIUM_SOURCE",
        "ENERGY_DENSE",
        "CONTEXT_DEPENDENT"
    ]

    # Moderate concerns that can be evaluated from presence.
    moderate_concern_flags = [
        "LIMITED_TRANSPARENCY",
        "PROCESSED_FAT_CONCERN",
        "ARTIFICIAL_FLAVOR"
    ]

    # --------------------------------------------------
    # COUNT FLAG TYPES
    # --------------------------------------------------

    high_concern_count = sum(
        1
        for flag in unique_flags
        if flag in high_concern_flags
    )

    quantity_dependent_count = sum(
        1
        for flag in unique_flags
        if flag in quantity_dependent_flags
    )

    moderate_concern_count = sum(
        1
        for flag in unique_flags
        if flag in moderate_concern_flags
    )

    # --------------------------------------------------
    # APPLY PENALTIES
    # --------------------------------------------------

    # Strong penalty for genuinely high-concern ingredients.
    overall_score -= high_concern_count * 15

    # Small penalty only.
    # Sugar/salt presence does not mean excessive quantity.
    overall_score -= quantity_dependent_count * 2

    # Moderate concerns receive smaller penalties.
    overall_score -= moderate_concern_count * 3

    # Unknown ingredients reduce confidence.
    overall_score -= len(unknown_ingredients) * 5

    # --------------------------------------------------
    # INGREDIENT COMBINATION PENALTIES
    # --------------------------------------------------

    # Multiple quantity-dependent concerns can indicate
    # a more processed product, but do not justify a huge penalty.
    if quantity_dependent_count >= 3:
        overall_score -= 3

    # Multiple serious ingredients together deserve
    # an additional combination penalty.
    if high_concern_count >= 2:
        overall_score -= 5

    # Keep score within 0–100.
    overall_score = round(
        max(
            0,
            min(100, overall_score)
        )
    )

    # --------------------------------------------------
    # ADULT SAFETY CALCULATION
    # --------------------------------------------------

    # Adult score is the calculated overall score.
    adult_score = overall_score

    adult_score = round(
        max(
            0,
            min(100, adult_score)
        )
    )

    # --------------------------------------------------
    # CHILD SAFETY CALCULATION
    # --------------------------------------------------

    # Child starts from overall score.
    child_score = overall_score

    # Added sugar is more relevant to children,
    # but quantity is still unknown.
    if "ADDED_SUGAR" in unique_flags:
        child_score -= 5

    # Sodium is more relevant to children,
    # but quantity is still unknown.
    if (
        "HIGH_SODIUM_QUANTITY_FLAG" in unique_flags
        or "SODIUM_SOURCE" in unique_flags
    ):
        child_score -= 3

    # Several processing-related concerns deserve
    # a small additional penalty.
    if quantity_dependent_count >= 3:
        child_score -= 2

    child_score = round(
        max(
            0,
            min(100, child_score)
        )
    )

    # --------------------------------------------------
    # PREGNANCY SAFETY CALCULATION
    # --------------------------------------------------

    # Pregnancy starts from overall score.
    pregnancy_score = overall_score

    # Strong concerns matter more during pregnancy.
    if high_concern_count >= 1:
        pregnancy_score -= 5

    # Unknown ingredients reduce confidence further.
    if unknown_ingredients:
        pregnancy_score -= 5

    pregnancy_score = round(
        max(
            0,
            min(100, pregnancy_score)
        )
    )

    # --------------------------------------------------
    # OVERALL FLAGS
    # --------------------------------------------------

    overall_flags = []

    # Sugar is present, but quantity is unknown.
    if "ADDED_SUGAR" in unique_flags:

        overall_flags.append(
            "ADDED_SUGAR_PRESENT_QUANTITY_UNKNOWN"
        )

    # Sodium-related ingredients are present,
    # but this does not prove high sodium.
    if (
        "HIGH_SODIUM_QUANTITY_FLAG" in unique_flags
        or "SODIUM_SOURCE" in unique_flags
    ):

        overall_flags.append(
            "SODIUM_PRESENT_QUANTITY_UNKNOWN"
        )

    # Actual high-concern ingredients.
    if high_concern_count >= 1:

        overall_flags.append(
            "HIGH_CONCERN_INGREDIENT_PRESENT"
        )

    if high_concern_count >= 2:

        overall_flags.append(
            "MULTIPLE_HIGH_CONCERN_INGREDIENTS"
        )

    # Allergen detection.
    if any(
        "ALLERGEN" in flag
        for flag in unique_flags
    ):

        overall_flags.append(
            "ALLERGEN_PRESENT"
        )

    # Ingredient transparency.
    if "LIMITED_TRANSPARENCY" in unique_flags:

        overall_flags.append(
            "LIMITED_INGREDIENT_TRANSPARENCY"
        )

    # Processing concerns.
    if quantity_dependent_count >= 3:

        overall_flags.append(
            "MULTIPLE_QUANTITY_DEPENDENT_CONCERNS"
        )

    # Unknown ingredients.
    if unknown_ingredients:

        overall_flags.append(
            "UNKNOWN_INGREDIENTS_PRESENT"
        )

    # --------------------------------------------------
    # POSITIVE ASPECTS
    # --------------------------------------------------

    positive_aspects = []

    high_score_ingredients = [
        item.get("ingredient_name", "")
        for item in individual_ingredients
        if item.get(
            "individual_trust_score",
            0
        ) >= 8
    ]

    if high_score_ingredients:

        positive_aspects.append(
            "Contains higher-trust ingredients such as " +
            ", ".join(high_score_ingredients)
        )

    low_concern_ingredients = [
        item.get("ingredient_name", "")
        for item in individual_ingredients
        if item.get(
            "individual_trust_score",
            0
        ) >= 7
    ]

    if len(low_concern_ingredients) >= 2:

        positive_aspects.append(
            "Several ingredients have moderate to high individual trust scores."
        )

    if all(
        item.get(
            "individual_trust_score",
            0
        ) >= 5
        for item in individual_ingredients
    ):

        positive_aspects.append(
            "No matched ingredient has an extremely low individual trust score."
        )

    # --------------------------------------------------
    # KEY CONCERNS
    # --------------------------------------------------

    key_concerns = []

    if "ADDED_SUGAR" in unique_flags:

        key_concerns.append(
            "Contains added sugar, but the actual quantity is unavailable, "
            "so excessive intake cannot be confirmed."
        )

    if (
        "HIGH_SODIUM_QUANTITY_FLAG" in unique_flags
        or "SODIUM_SOURCE" in unique_flags
    ):

        key_concerns.append(
            "Contains sodium-related ingredients, but the exact amount is "
            "unknown and high sodium cannot be confirmed."
        )

    if "LIMITED_TRANSPARENCY" in unique_flags:

        key_concerns.append(
            "Contains a broadly labelled flavour ingredient with limited "
            "transparency about its exact composition."
        )

    if high_concern_count >= 1:

        key_concerns.append(
            "Contains one or more ingredients with a high individual "
            "health concern profile."
        )

    if any(
        "ALLERGEN" in flag
        for flag in unique_flags
    ):

        key_concerns.append(
            "Contains ingredients that may be unsuitable for people with "
            "relevant food allergies or intolerances."
        )

    if unknown_ingredients:

        key_concerns.append(
            "Some ingredients were not found in the TrustLens database, "
            "which reduces confidence in the overall evaluation."
        )

    # --------------------------------------------------
    # ADULT REMARK
    # --------------------------------------------------

    if adult_score >= 80:

        adult_remark = (
            "The overall ingredient combination appears generally safe "
            "for a normal adult based on the available ingredient data."
        )

    elif adult_score >= 60:

        adult_remark = (
            "The combination is acceptable for adults but contains some "
            "ingredient-level concerns. Exact ingredient amounts would "
            "improve the assessment."
        )

    elif adult_score >= 40:

        adult_remark = (
            "The combination should be consumed with dietary awareness "
            "because multiple ingredient-level concerns reduce its overall "
            "trust score."
        )

    else:

        adult_remark = (
            "The combination contains significant ingredient-level concerns "
            "and may be better limited or consumed occasionally."
        )

    # --------------------------------------------------
    # CHILD REMARK
    # --------------------------------------------------

    if child_score >= 80:

        child_remark = (
            "The combination appears generally suitable for children "
            "based on the available ingredient data."
        )

    elif child_score >= 60:

        child_remark = (
            "The combination may be acceptable for children, but added "
            "sugar and sodium-related ingredients should be monitored "
            "because children have lower dietary requirements."
        )

    elif child_score >= 40:

        child_remark = (
            "Children may require greater dietary awareness because added "
            "sugar, sodium or multiple processed ingredients can be more "
            "relevant to a child's overall diet."
        )

    else:

        child_remark = (
            "The combination has significant concerns for frequent child "
            "consumption. Exact quantities should be checked."
        )

    # --------------------------------------------------
    # PREGNANCY REMARK
    # --------------------------------------------------

    if pregnancy_score >= 80:

        pregnancy_remark = (
            "The ingredient combination appears generally acceptable "
            "during pregnancy based on the available data."
        )

    elif pregnancy_score >= 60:

        pregnancy_remark = (
            "The combination is generally acceptable during pregnancy, "
            "but overall nutritional quality and ingredient amounts should "
            "still be considered."
        )

    elif pregnancy_score >= 40:

        pregnancy_remark = (
            "The combination requires dietary awareness during pregnancy "
            "because some ingredients or incomplete information may reduce "
            "confidence in the assessment."
        )

    else:

        pregnancy_remark = (
            "The combination has significant concerns during pregnancy "
            "based on the available ingredient-level data."
        )

    # --------------------------------------------------
    # OVERALL REMARKS
    # --------------------------------------------------

    if overall_score >= 80:

        overall_remarks = (
            "Overall, this is a relatively favourable ingredient combination. "
            "Most matched ingredients have moderate to high trust scores. "
            "Dietary restrictions and allergens should still be considered."
        )

    elif overall_score >= 60:

        overall_remarks = (
            "Overall, this product has moderate trust. It contains several "
            "nutritionally favourable or generally low-concern ingredients, "
            "but some ingredient-level concerns reduce the score. Because "
            "exact quantities are unavailable, the actual dietary impact "
            "cannot be determined."
        )

    elif overall_score >= 40:

        overall_remarks = (
            "Overall, this combination should be consumed with some dietary "
            "awareness. It contains both favourable and lower-trust "
            "ingredients, and frequent consumption may be less suitable "
            "than occasional consumption."
        )

    else:

        overall_remarks = (
            "Overall, this combination has significant concerns based on "
            "the available ingredient data and may be better consumed only "
            "occasionally or avoided depending on individual dietary needs."
        )

    # --------------------------------------------------
    # RETURN FINAL ANALYSIS
    # --------------------------------------------------

    return {
        "overall_trust_score": overall_score,

        "status": execution_status,

        "overall_safety_adult": {
            "score": adult_score,
            "remark": adult_remark
        },

        "overall_safety_child": {
            "score": child_score,
            "remark": child_remark
        },

        "overall_safety_pregnancy": {
            "score": pregnancy_score,
            "remark": pregnancy_remark
        },

        "overall_flags": overall_flags,

        "overall_remarks": overall_remarks,

        "key_concerns": key_concerns,

        "positive_aspects": positive_aspects
    }