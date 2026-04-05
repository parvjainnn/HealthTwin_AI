import React, { useMemo, useState } from "react";
import {
  SafeAreaView,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View
} from "react-native";
import { StatusBar as ExpoStatusBar } from "expo-status-bar";

const LIGHT_THEME = {
  mode: "light",
  background: "#f3fff5",
  backgroundSoft: "#e7f7eb",
  card: "#ffffff",
  cardAlt: "#eef9f0",
  text: "#143524",
  textSoft: "#5e7f6d",
  border: "#d0e7d5",
  accent: "#2f9f74",
  accentSoft: "#88d7a0",
  accentDeep: "#1f7c58",
  chip: "#e4f5e8",
  danger: "#d96a76",
  warning: "#e9a463"
};

const DARK_THEME = {
  mode: "dark",
  background: "#071018",
  backgroundSoft: "#0f1b24",
  card: "#10202a",
  cardAlt: "#162833",
  text: "#effff6",
  textSoft: "#9cb6aa",
  border: "#233946",
  accent: "#71e7a4",
  accentSoft: "#2fa574",
  accentDeep: "#b4ffd0",
  chip: "#163125",
  danger: "#ff8b95",
  warning: "#ffb66d"
};

const overviewCards = [
  { title: "Vitals cockpit", copy: "Track weight, sleep, hydration, heart rate, and a single health score." },
  { title: "AI medical chat", copy: "Ask health questions with the same assistant you already built for web." },
  { title: "Risk prediction", copy: "Run diabetes and heart checks from mobile-friendly forms." },
  { title: "Records vault", copy: "Keep patient bills, prescriptions, and reports in one future-ready place." }
];

const initialVitals = {
  name: "User",
  age: "28",
  gender: "Male",
  weight: "72",
  height: "175",
  steps: "6500",
  sleep: "6.5",
  water: "2",
  heart_rate: "72"
};

const initialDiabetes = {
  pregnancies: "0",
  glucose: "120",
  blood_pressure: "80",
  skin_thickness: "20",
  insulin: "85",
  bmi: "26.1",
  diabetes_pedigree_function: "0.52",
  age: "28"
};

const initialHeart = {
  age: "45",
  sex: "1",
  chest_pain_type: "1",
  resting_bp: "130",
  cholesterol: "220",
  fasting_bs: "0",
  resting_ecg: "0",
  max_hr: "150",
  exercise_angina: "0",
  oldpeak: "1.0"
};

const fallbackChatReply =
  "I could not reach the backend, so this is a mobile demo response. Once your FastAPI server is running, this screen will use the real HealthTwin AI endpoint.";

export default function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [activeTab, setActiveTab] = useState("home");
  const [apiBaseUrl, setApiBaseUrl] = useState("http://127.0.0.1:8000");
  const [vitals, setVitals] = useState(initialVitals);
  const [analysis, setAnalysis] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [watchData, setWatchData] = useState(null);
  const [watchLoading, setWatchLoading] = useState(false);
  const [predictionTab, setPredictionTab] = useState("diabetes");
  const [diabetesForm, setDiabetesForm] = useState(initialDiabetes);
  const [heartForm, setHeartForm] = useState(initialHeart);
  const [predictionResult, setPredictionResult] = useState(null);
  const [predictionLoading, setPredictionLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hello, I am HealthTwin AI. Ask about symptoms, treatments, recovery, or wellness habits."
    }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

  const theme = darkMode ? DARK_THEME : LIGHT_THEME;
  const styles = useMemo(() => createStyles(theme), [theme]);

  const callApi = async (path, options = {}) => {
    const response = await fetch(`${apiBaseUrl}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {})
      },
      ...options
    });

    const json = await response.json();
    if (!response.ok) {
      throw new Error(json.detail || json.error || "Request failed");
    }
    return json;
  };

  const analyzeDashboard = async () => {
    setAnalysisLoading(true);
    try {
      const payload = {
        ...vitals,
        age: Number(vitals.age),
        weight: Number(vitals.weight),
        height: Number(vitals.height),
        steps: Number(vitals.steps),
        sleep: Number(vitals.sleep),
        water: Number(vitals.water),
        heart_rate: Number(vitals.heart_rate)
      };
      const result = await callApi("/api/dashboard/analyze", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      setAnalysis(result);
    } catch (error) {
      const bmi = Number(vitals.weight) / Math.pow(Number(vitals.height) / 100, 2);
      const roundedBmi = Number.isFinite(bmi) ? Number(bmi.toFixed(1)) : 0;
      const healthScore = Math.max(
        35,
        Math.min(
          96,
          Math.round(
            92 -
              Math.abs(22 - roundedBmi) * 2 -
              Math.max(0, 7 - Number(vitals.sleep)) * 3 -
              Math.max(0, 8000 - Number(vitals.steps)) / 1200
          )
        )
      );
      setAnalysis({
        bmi: roundedBmi,
        bmi_category: roundedBmi < 18.5 ? "Underweight" : roundedBmi < 25 ? "Healthy" : roundedBmi < 30 ? "Overweight" : "Obese",
        bmi_color: roundedBmi < 25 ? "#2f9f74" : "#e9a463",
        health_score: healthScore,
        breakdown: {
          bmi_pts: Math.max(8, Math.min(25, 25 - Math.round(Math.abs(22 - roundedBmi) * 1.5))),
          sleep_pts: Math.max(8, Math.min(25, Math.round(Number(vitals.sleep) * 3))),
          step_pts: Math.max(8, Math.min(25, Math.round(Number(vitals.steps) / 450))),
          water_pts: Math.max(5, Math.min(15, Math.round(Number(vitals.water) * 5))),
          hr_pts: 8
        },
        obesity_risk: roundedBmi < 25 ? "Low" : roundedBmi < 30 ? "Medium" : "High",
        obesity_prob: roundedBmi < 25 ? 18 : roundedBmi < 30 ? 49 : 74,
        fatigue_risk: Number(vitals.sleep) < 6 ? "High" : Number(vitals.sleep) < 7 ? "Medium" : "Low",
        fatigue_prob: Number(vitals.sleep) < 6 ? 76 : Number(vitals.sleep) < 7 ? 48 : 21,
        fallback: true,
        note: error.message
      });
    } finally {
      setAnalysisLoading(false);
    }
  };

  const fetchWatch = async () => {
    setWatchLoading(true);
    try {
      const result = await callApi(`/api/dashboard/watch?base_hr=${encodeURIComponent(vitals.heart_rate || "72")}`);
      setWatchData(result);
    } catch (error) {
      setWatchData({
        heart_rate: Number(vitals.heart_rate) || 72,
        spo2: 98.1,
        stress: 32,
        live_steps: Number(vitals.steps) + 426,
        calories: 512,
        fallback: true
      });
    } finally {
      setWatchLoading(false);
    }
  };

  const runPrediction = async () => {
    setPredictionLoading(true);
    try {
      const path = predictionTab === "diabetes" ? "/api/predict/diabetes" : "/api/predict/heart";
      const form = predictionTab === "diabetes" ? diabetesForm : heartForm;
      const payload = Object.fromEntries(Object.entries(form).map(([key, value]) => [key, Number(value)]));
      const result = await callApi(path, {
        method: "POST",
        body: JSON.stringify(payload)
      });
      setPredictionResult(result);
    } catch (error) {
      setPredictionResult({
        disease: predictionTab === "diabetes" ? "Diabetes" : "Heart Disease",
        prediction: predictionTab === "diabetes" ? 0 : 1,
        risk_label: predictionTab === "diabetes" ? "Moderate" : "Elevated",
        confidence: predictionTab === "diabetes" ? 0.71 : 0.76,
        message: `Demo result shown because the mobile app could not reach ${predictionTab} prediction API.`,
        fallback: true
      });
    } finally {
      setPredictionLoading(false);
    }
  };

  const sendChat = async () => {
    const trimmed = chatInput.trim();
    if (!trimmed || chatLoading) return;

    const nextMessages = [...messages, { role: "user", text: trimmed }];
    setMessages(nextMessages);
    setChatInput("");
    setChatLoading(true);

    try {
      const result = await callApi("/api/chat", {
        method: "POST",
        body: JSON.stringify({
          message: trimmed,
          history: nextMessages.map((item) => ({ role: item.role, content: item.text }))
        })
      });
      setMessages((current) => [...current, { role: "assistant", text: result.reply || fallbackChatReply }]);
    } catch (error) {
      setMessages((current) => [...current, { role: "assistant", text: fallbackChatReply }]);
    } finally {
      setChatLoading(false);
    }
  };

  const renderHome = () => (
    <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
      <View style={styles.heroCard}>
        <View style={styles.badge}>
          <Text style={styles.badgeText}>HealthTwin Mobile</Text>
        </View>
        <Text style={styles.heroTitle}>A companion app for your AI health platform.</Text>
        <Text style={styles.heroCopy}>
          This mobile client is designed around your current backend so you can analyze vitals, ask HealthTwin AI questions,
          and carry the core experience in your pocket.
        </Text>
        <View style={styles.urlCard}>
          <Text style={styles.sectionLabel}>Backend base URL</Text>
          <TextInput
            value={apiBaseUrl}
            onChangeText={setApiBaseUrl}
            placeholder="http://192.168.1.10:8000"
            placeholderTextColor={theme.textSoft}
            style={styles.input}
            autoCapitalize="none"
            autoCorrect={false}
          />
          <Text style={styles.helperText}>
            Use your computer's local IP for a physical phone. For Android emulator, `10.0.2.2:8000` often works.
          </Text>
        </View>
      </View>

      <View style={styles.grid}>
        {overviewCards.map((card) => (
          <View key={card.title} style={styles.featureCard}>
            <Text style={styles.featureTitle}>{card.title}</Text>
            <Text style={styles.featureCopy}>{card.copy}</Text>
          </View>
        ))}
      </View>

      <View style={styles.sectionCard}>
        <Text style={styles.sectionTitle}>Recommended mobile roadmap</Text>
        <Text style={styles.bullet}>1. Start with FastAPI routes for mobile because they are already session-free.</Text>
        <Text style={styles.bullet}>2. Add token auth before exposing patient records and uploads on mobile.</Text>
        <Text style={styles.bullet}>3. Next iteration: document picker, OCR uploads, and local health reminders.</Text>
      </View>
    </ScrollView>
  );

  const renderDashboard = () => (
    <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
      <View style={styles.sectionCard}>
        <Text style={styles.sectionTitle}>Vitals analyzer</Text>
        <View style={styles.fieldGrid}>
          {Object.entries(vitals).map(([key, value]) => (
            <View key={key} style={styles.fieldWrap}>
              <Text style={styles.fieldLabel}>{key.replace("_", " ")}</Text>
              <TextInput
                value={value}
                onChangeText={(text) => setVitals((current) => ({ ...current, [key]: text }))}
                style={styles.input}
                placeholderTextColor={theme.textSoft}
              />
            </View>
          ))}
        </View>
        <View style={styles.row}>
          <TouchableOpacity style={styles.primaryButton} onPress={analyzeDashboard}>
            <Text style={styles.primaryButtonText}>{analysisLoading ? "Analyzing..." : "Analyze health"}</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.secondaryButton} onPress={fetchWatch}>
            <Text style={styles.secondaryButtonText}>{watchLoading ? "Loading..." : "Simulate watch"}</Text>
          </TouchableOpacity>
        </View>
      </View>

      {analysis ? (
        <View style={styles.sectionCard}>
          <Text style={styles.sectionTitle}>Analysis result</Text>
          <View style={styles.metricRow}>
            <MetricCard theme={theme} label="Health score" value={String(Math.round(analysis.health_score))} />
            <MetricCard theme={theme} label="BMI" value={String(analysis.bmi)} />
          </View>
          <View style={styles.metricRow}>
            <MetricCard theme={theme} label="Obesity risk" value={analysis.obesity_risk} />
            <MetricCard theme={theme} label="Fatigue risk" value={analysis.fatigue_risk} />
          </View>
          <Text style={styles.helperText}>
            {analysis.fallback ? "Showing offline estimation because the API was unavailable." : "Live result from FastAPI dashboard analysis."}
          </Text>
        </View>
      ) : null}

      {watchData ? (
        <View style={styles.sectionCard}>
          <Text style={styles.sectionTitle}>Watch snapshot</Text>
          <View style={styles.metricRow}>
            <MetricCard theme={theme} label="Heart rate" value={`${watchData.heart_rate}`} />
            <MetricCard theme={theme} label="SpO2" value={`${watchData.spo2}`} />
          </View>
          <View style={styles.metricRow}>
            <MetricCard theme={theme} label="Stress" value={`${watchData.stress}`} />
            <MetricCard theme={theme} label="Steps" value={`${watchData.live_steps}`} />
          </View>
        </View>
      ) : null}
    </ScrollView>
  );

  const activePredictionForm = predictionTab === "diabetes" ? diabetesForm : heartForm;
  const setActivePredictionForm = predictionTab === "diabetes" ? setDiabetesForm : setHeartForm;

  const renderPredictions = () => (
    <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
      <View style={styles.sectionCard}>
        <Text style={styles.sectionTitle}>Mobile prediction tools</Text>
        <View style={styles.tabRow}>
          {["diabetes", "heart"].map((tab) => (
            <TouchableOpacity
              key={tab}
              style={[styles.segmentButton, predictionTab === tab && styles.segmentButtonActive]}
              onPress={() => setPredictionTab(tab)}
            >
              <Text style={[styles.segmentButtonText, predictionTab === tab && styles.segmentButtonTextActive]}>
                {tab === "diabetes" ? "Diabetes" : "Heart"}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
        <View style={styles.fieldGrid}>
          {Object.entries(activePredictionForm).map(([key, value]) => (
            <View key={key} style={styles.fieldWrap}>
              <Text style={styles.fieldLabel}>{key.replace(/_/g, " ")}</Text>
              <TextInput
                value={value}
                onChangeText={(text) => setActivePredictionForm((current) => ({ ...current, [key]: text }))}
                style={styles.input}
                placeholderTextColor={theme.textSoft}
                keyboardType="numeric"
              />
            </View>
          ))}
        </View>
        <TouchableOpacity style={styles.primaryButton} onPress={runPrediction}>
          <Text style={styles.primaryButtonText}>{predictionLoading ? "Running..." : "Run prediction"}</Text>
        </TouchableOpacity>
      </View>

      {predictionResult ? (
        <View style={styles.sectionCard}>
          <Text style={styles.sectionTitle}>{predictionResult.disease}</Text>
          <Text style={styles.resultHeadline}>{predictionResult.risk_label}</Text>
          <Text style={styles.featureCopy}>{predictionResult.message}</Text>
          {predictionResult.confidence ? (
            <Text style={styles.helperText}>Confidence: {Math.round(predictionResult.confidence * 100)}%</Text>
          ) : null}
        </View>
      ) : null}
    </ScrollView>
  );

  const renderChat = () => (
    <View style={styles.chatScreen}>
      <ScrollView contentContainerStyle={styles.chatMessages}>
        {messages.map((message, index) => (
          <View
            key={`${message.role}-${index}`}
            style={[styles.chatBubble, message.role === "user" ? styles.chatBubbleUser : styles.chatBubbleAssistant]}
          >
            <Text style={[styles.chatRole, message.role === "user" ? styles.chatRoleUser : null]}>
              {message.role === "user" ? "You" : "HealthTwin AI"}
            </Text>
            <Text style={[styles.chatText, message.role === "user" ? styles.chatTextUser : null]}>{message.text}</Text>
          </View>
        ))}
      </ScrollView>
      <View style={styles.chatComposer}>
        <TextInput
          value={chatInput}
          onChangeText={setChatInput}
          placeholder="Ask a health question..."
          placeholderTextColor={theme.textSoft}
          style={[styles.input, styles.chatInput]}
          multiline
        />
        <TouchableOpacity style={styles.primaryButton} onPress={sendChat}>
          <Text style={styles.primaryButtonText}>{chatLoading ? "..." : "Send"}</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  const renderRecords = () => (
    <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
      <View style={styles.sectionCard}>
        <Text style={styles.sectionTitle}>Records vault</Text>
        <Text style={styles.featureCopy}>
          This first mobile scaffold keeps the records workflow visible so we can extend it next with document picking, secure uploads, and OCR previews.
        </Text>
      </View>
      {[
        { title: "Bills", note: "Attach lab bills, invoices, and visit receipts." },
        { title: "Prescriptions", note: "Store doctor-prescribed medications for follow-up visits." },
        { title: "Reports", note: "Future add-on for scans, discharge summaries, and lab documents." }
      ].map((item) => (
        <View key={item.title} style={styles.featureCard}>
          <Text style={styles.featureTitle}>{item.title}</Text>
          <Text style={styles.featureCopy}>{item.note}</Text>
        </View>
      ))}
    </ScrollView>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle={darkMode ? "light-content" : "dark-content"} />
      <ExpoStatusBar style={darkMode ? "light" : "dark"} />
      <View style={styles.container}>
        <View style={styles.header}>
          <View>
            <Text style={styles.appLabel}>HealthTwin</Text>
            <Text style={styles.headerTitle}>Mobile app scaffold</Text>
          </View>
          <TouchableOpacity style={styles.themeButton} onPress={() => setDarkMode((current) => !current)}>
            <Text style={styles.themeButtonText}>{darkMode ? "Light" : "Dark"}</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.tabs}>
          {[
            ["home", "Home"],
            ["dashboard", "Dashboard"],
            ["predictions", "Predict"],
            ["chat", "AI Chat"],
            ["records", "Records"]
          ].map(([key, label]) => (
            <TouchableOpacity
              key={key}
              style={[styles.tabButton, activeTab === key && styles.tabButtonActive]}
              onPress={() => setActiveTab(key)}
            >
              <Text style={[styles.tabButtonText, activeTab === key && styles.tabButtonTextActive]}>{label}</Text>
            </TouchableOpacity>
          ))}
        </View>

        <View style={styles.content}>
          {activeTab === "home" && renderHome()}
          {activeTab === "dashboard" && renderDashboard()}
          {activeTab === "predictions" && renderPredictions()}
          {activeTab === "chat" && renderChat()}
          {activeTab === "records" && renderRecords()}
        </View>
      </View>
    </SafeAreaView>
  );
}

function MetricCard({ theme, label, value }) {
  return (
    <View
      style={{
        flex: 1,
        backgroundColor: theme.cardAlt,
        borderRadius: 18,
        padding: 16,
        borderWidth: 1,
        borderColor: theme.border
      }}
    >
      <Text style={{ color: theme.textSoft, fontSize: 12, textTransform: "uppercase", letterSpacing: 1.2 }}>{label}</Text>
      <Text style={{ color: theme.text, fontSize: 24, fontWeight: "800", marginTop: 8 }}>{value}</Text>
    </View>
  );
}

function createStyles(theme) {
  return StyleSheet.create({
    safeArea: {
      flex: 1,
      backgroundColor: theme.background
    },
    container: {
      flex: 1,
      backgroundColor: theme.background
    },
    header: {
      paddingHorizontal: 20,
      paddingTop: 16,
      paddingBottom: 12,
      flexDirection: "row",
      alignItems: "center",
      justifyContent: "space-between"
    },
    appLabel: {
      color: theme.accent,
      fontSize: 12,
      fontWeight: "800",
      textTransform: "uppercase",
      letterSpacing: 1.8
    },
    headerTitle: {
      color: theme.text,
      fontSize: 24,
      fontWeight: "800",
      marginTop: 6
    },
    themeButton: {
      backgroundColor: theme.card,
      borderColor: theme.border,
      borderWidth: 1,
      borderRadius: 999,
      paddingHorizontal: 16,
      paddingVertical: 10
    },
    themeButtonText: {
      color: theme.text,
      fontWeight: "700"
    },
    tabs: {
      flexDirection: "row",
      paddingHorizontal: 16,
      gap: 8,
      paddingBottom: 12
    },
    tabButton: {
      paddingHorizontal: 14,
      paddingVertical: 10,
      borderRadius: 999,
      backgroundColor: theme.card,
      borderWidth: 1,
      borderColor: theme.border
    },
    tabButtonActive: {
      backgroundColor: theme.accent
    },
    tabButtonText: {
      color: theme.textSoft,
      fontWeight: "700",
      fontSize: 13
    },
    tabButtonTextActive: {
      color: "#ffffff"
    },
    content: {
      flex: 1
    },
    scrollContent: {
      padding: 16,
      gap: 16
    },
    heroCard: {
      backgroundColor: theme.card,
      borderRadius: 28,
      padding: 20,
      borderWidth: 1,
      borderColor: theme.border
    },
    badge: {
      alignSelf: "flex-start",
      backgroundColor: theme.chip,
      borderRadius: 999,
      paddingHorizontal: 12,
      paddingVertical: 8
    },
    badgeText: {
      color: theme.accent,
      fontWeight: "800",
      fontSize: 12,
      textTransform: "uppercase",
      letterSpacing: 1.2
    },
    heroTitle: {
      color: theme.text,
      fontSize: 30,
      fontWeight: "800",
      lineHeight: 36,
      marginTop: 16
    },
    heroCopy: {
      color: theme.textSoft,
      fontSize: 15,
      lineHeight: 24,
      marginTop: 12
    },
    urlCard: {
      marginTop: 18,
      backgroundColor: theme.cardAlt,
      borderRadius: 20,
      padding: 16,
      borderWidth: 1,
      borderColor: theme.border
    },
    sectionCard: {
      backgroundColor: theme.card,
      borderRadius: 24,
      padding: 18,
      borderWidth: 1,
      borderColor: theme.border
    },
    sectionTitle: {
      color: theme.text,
      fontSize: 20,
      fontWeight: "800"
    },
    sectionLabel: {
      color: theme.textSoft,
      fontSize: 12,
      textTransform: "uppercase",
      letterSpacing: 1.1,
      fontWeight: "700",
      marginBottom: 10
    },
    helperText: {
      color: theme.textSoft,
      fontSize: 13,
      lineHeight: 20,
      marginTop: 10
    },
    grid: {
      gap: 12
    },
    featureCard: {
      backgroundColor: theme.card,
      borderRadius: 22,
      padding: 18,
      borderWidth: 1,
      borderColor: theme.border
    },
    featureTitle: {
      color: theme.text,
      fontSize: 18,
      fontWeight: "800"
    },
    featureCopy: {
      color: theme.textSoft,
      fontSize: 14,
      lineHeight: 22,
      marginTop: 8
    },
    bullet: {
      color: theme.textSoft,
      fontSize: 14,
      lineHeight: 22,
      marginTop: 10
    },
    fieldGrid: {
      gap: 12,
      marginTop: 14
    },
    fieldWrap: {
      gap: 8
    },
    fieldLabel: {
      color: theme.textSoft,
      fontSize: 12,
      textTransform: "uppercase",
      letterSpacing: 1.1,
      fontWeight: "700"
    },
    input: {
      backgroundColor: theme.backgroundSoft,
      borderColor: theme.border,
      borderWidth: 1,
      borderRadius: 16,
      paddingHorizontal: 14,
      paddingVertical: 12,
      color: theme.text,
      fontSize: 15
    },
    row: {
      flexDirection: "row",
      gap: 10,
      marginTop: 16
    },
    primaryButton: {
      backgroundColor: theme.accent,
      borderRadius: 16,
      paddingHorizontal: 18,
      paddingVertical: 14,
      alignItems: "center",
      justifyContent: "center"
    },
    primaryButtonText: {
      color: "#ffffff",
      fontWeight: "800",
      fontSize: 15
    },
    secondaryButton: {
      flex: 1,
      backgroundColor: theme.cardAlt,
      borderColor: theme.border,
      borderWidth: 1,
      borderRadius: 16,
      paddingHorizontal: 18,
      paddingVertical: 14,
      alignItems: "center",
      justifyContent: "center"
    },
    secondaryButtonText: {
      color: theme.text,
      fontWeight: "800",
      fontSize: 15
    },
    metricRow: {
      flexDirection: "row",
      gap: 12,
      marginTop: 14
    },
    tabRow: {
      flexDirection: "row",
      gap: 10,
      marginTop: 16,
      marginBottom: 6
    },
    segmentButton: {
      flex: 1,
      borderRadius: 999,
      paddingVertical: 12,
      backgroundColor: theme.cardAlt,
      borderWidth: 1,
      borderColor: theme.border,
      alignItems: "center"
    },
    segmentButtonActive: {
      backgroundColor: theme.accent
    },
    segmentButtonText: {
      color: theme.text,
      fontWeight: "700"
    },
    segmentButtonTextActive: {
      color: "#ffffff"
    },
    resultHeadline: {
      color: theme.accentDeep,
      fontSize: 28,
      fontWeight: "800",
      marginTop: 14
    },
    chatScreen: {
      flex: 1,
      padding: 16
    },
    chatMessages: {
      gap: 12,
      paddingBottom: 18
    },
    chatBubble: {
      borderRadius: 20,
      padding: 14,
      borderWidth: 1,
      maxWidth: "92%"
    },
    chatBubbleAssistant: {
      alignSelf: "flex-start",
      backgroundColor: theme.card,
      borderColor: theme.border
    },
    chatBubbleUser: {
      alignSelf: "flex-end",
      backgroundColor: theme.accent,
      borderColor: theme.accent
    },
    chatRole: {
      color: theme.textSoft,
      fontSize: 11,
      textTransform: "uppercase",
      letterSpacing: 1.1,
      fontWeight: "800",
      marginBottom: 6
    },
    chatRoleUser: {
      color: "#dcfff0"
    },
    chatText: {
      color: theme.text,
      fontSize: 15,
      lineHeight: 22
    },
    chatTextUser: {
      color: "#ffffff"
    },
    chatComposer: {
      gap: 10,
      paddingTop: 12
    },
    chatInput: {
      minHeight: 100,
      textAlignVertical: "top"
    }
  });
}
