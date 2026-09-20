"""Rule-based AI Health Advisor — ported from Streamlit dashboard."""


def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight", "#8b5cf6"
    elif bmi < 25:
        return "Normal", "#00ff88"
    elif bmi < 30:
        return "Overweight", "#ffa500"
    else:
        return "Obese", "#ff4757"


def get_ai_response(question, user_data):
    q = question.lower()

    bmi = user_data.get("bmi", 22)
    sleep = user_data.get("sleep", 7)
    steps = user_data.get("steps", 7000)
    water = user_data.get("water", 2)
    heart_rate = user_data.get("heart_rate", 70)
    age = user_data.get("age", 30)
    weight = user_data.get("weight", 70)
    height = user_data.get("height", 170)
    health_score = user_data.get("health_score", 70)
    ob_risk = user_data.get("obesity_risk", "Low")
    fat_risk = user_data.get("fatigue_risk", "Low")
    bmi_cat, _ = bmi_category(bmi)

    responses = []

    if any(k in q for k in ["tired", "fatigue", "energy", "exhaust", "sleepy"]):
        if sleep < 6:
            responses.append(f"🛌 **Sleep Deficit Detected** — You're averaging only {sleep}h. Your body needs 7–9 hours. Try a consistent bedtime 30 minutes earlier each week.")
        if steps < 4000:
            responses.append(f"🚶 **Sedentary Alert** — Low activity ({steps:,} steps) reduces circulation. Even a 15-minute walk boosts energy.")
        if water < 1.5:
            responses.append(f"💧 **Dehydration Risk** — At {water}L/day you may be mildly dehydrated, causing fatigue.")
        if not responses:
            responses.append(f"✅ Your vitals look reasonable! Fatigue could stem from stress or diet. Try reducing blue light 1h before bed.")

    elif any(k in q for k in ["weight", "bmi", "obese", "fat", "slim", "overweight"]):
        responses.append(f"⚖️ **Your BMI is {bmi} ({bmi_cat})**. ")
        if bmi > 25:
            deficit = round((bmi - 24.9) * ((height / 100) ** 2), 1)
            responses.append(f"Losing ~{deficit}kg would bring you into the healthy range. A 500-calorie daily deficit achieves ~0.5kg/week.")
        elif bmi < 18.5:
            responses.append("You're underweight. Add 300–500 kcal/day through protein-rich whole foods.")
        else:
            responses.append(f"You're in the healthy BMI range. Maintain it with {steps:,}+ daily steps.")

    elif any(k in q for k in ["sleep", "insomnia", "rest", "nap"]):
        if sleep < 7:
            responses.append(f"😴 You're getting {sleep}h — below the 7–9h adult recommendation. Try no caffeine after 2pm, consistent wake times, and a cooler bedroom.")
        else:
            responses.append(f"🌙 Your {sleep}h sleep is healthy. Maintain quality by avoiding alcohol 3h before bed.")

    elif any(k in q for k in ["exercise", "steps", "active", "workout", "walk", "run"]):
        if steps < 5000:
            responses.append(f"🏃 **Low Activity** — {steps:,} steps is below WHO guidelines. Add 1,000 steps/week progressively.")
        elif steps >= 10000:
            responses.append(f"🔥 **Great Activity!** {steps:,} steps. Add strength training 2–3x/week for metabolic benefits.")
        else:
            responses.append(f"👟 **Decent Activity** — {steps:,} steps. A 20-minute post-dinner walk would hit the 10k target.")

    elif any(k in q for k in ["water", "hydrat", "drink", "thirst"]):
        if water < 2:
            responses.append(f"💧 **Increase Hydration** — {water}L is below recommended 2.5L. Use a marked bottle and set hourly reminders.")
        else:
            responses.append(f"✅ **Good Hydration** — {water}L is on target. Spread intake throughout the day.")

    elif any(k in q for k in ["heart", "bp", "blood pressure", "cardiac", "pulse"]):
        if heart_rate and heart_rate > 90:
            responses.append(f"❤️ **Elevated Resting HR** ({heart_rate} bpm) — Normal is 60–80. Consider 30-min cardio 3x/week.")
        elif heart_rate:
            responses.append(f"✅ **Heart Rate Normal** ({heart_rate} bpm). Regular aerobic exercise keeps it optimal.")

    elif any(k in q for k in ["diet", "eat", "food", "nutrition", "calories"]):
        responses.append(f"🥗 **Nutrition Guidance** for BMI {bmi} ({bmi_cat}): ")
        if bmi > 25:
            responses.append("High-protein, low-glycemic diet. Prioritize vegetables, lean proteins, complex carbs. Avoid processed sugars.")
        elif bmi < 18.5:
            responses.append("Increase caloric density with nuts, avocados, legumes. Add a protein shake post-workout.")
        else:
            responses.append("Balanced Mediterranean-style diet. 50% veg/fruit, 25% whole grains, 25% lean protein.")

    elif any(k in q for k in ["score", "health", "overall", "summary", "status"]):
        grade = "Excellent 🌟" if health_score >= 80 else "Good 👍" if health_score >= 65 else "Fair ⚠️" if health_score >= 50 else "Needs Attention 🔴"
        responses.append(f"📊 **Health Score: {health_score}/100 — {grade}**\n\nBreakdown reflects BMI ({bmi_cat}), sleep ({sleep}h), activity ({steps:,} steps), hydration ({water}L).")
        if health_score < 70:
            lowest = min([("sleep", sleep / 9), ("steps", steps / 10000), ("water", water / 2.5)], key=lambda x: x[1])
            responses.append(f"\n⚡ **Biggest opportunity**: Improve your **{lowest[0]}** for fastest gains.")

    elif any(k in q for k in ["advice", "recommend", "tip", "suggest", "help", "improve"]):
        tips = []
        if sleep < 7: tips.append(f"• Sleep: Add 30 min earlier bedtime (currently {sleep}h, target 7–8h)")
        if steps < 7000: tips.append(f"• Activity: Add a 20-min walk (currently {steps:,}, target 7,000+)")
        if water < 2: tips.append(f"• Hydration: 1 more glass/hour (currently {water}L, target 2.5L)")
        if bmi > 25: tips.append("• Weight: Reduce 200 kcal/day — small sustainable deficit")
        if not tips:
            tips = ["• Metrics are solid! Focus on consistency", "• Add strength training 2x/week", "• Annual blood panel recommended"]
        responses.append("🎯 **Personalized Recommendations:**\n\n" + "\n".join(tips))

    else:
        responses.append(f"🤖 Based on your profile (BMI: {bmi}, Sleep: {sleep}h, Steps: {steps:,}, Score: {health_score}/100), I can advise on: **fatigue, weight, sleep, exercise, hydration, diet, heart health, or your health score**.")

    return " ".join(responses)
