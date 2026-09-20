import React, { useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, View } from 'react-native';
import { AppButton } from '../../components/AppButton';
import { AppInput } from '../../components/AppInput';
import { Card } from '../../components/Card';
import { MetricCard } from '../../components/MetricCard';
import { useNetworkStatus } from '../../hooks/useNetworkStatus';
import { analyzeVitals, fetchWatch, saveHealthLog } from '../../services/api/healthApi';
import { normalizeApiError } from '../../services/api/client';
import { palette } from '../../theme/palette';

const INITIAL_FORM = {
  age: '28',
  gender: 'Male',
  weight: '72',
  height: '175',
  steps: '6500',
  sleep: '6.5',
  water: '2',
  heart_rate: '72'
};

export function DashboardScreen() {
  const isConnected = useNetworkStatus();
  const [form, setForm] = useState(INITIAL_FORM);
  const [analysis, setAnalysis] = useState(null);
  const [watch, setWatch] = useState(null);
  const [loadingAnalyze, setLoadingAnalyze] = useState(false);
  const [loadingWatch, setLoadingWatch] = useState(false);
  const [loadingSave, setLoadingSave] = useState(false);

  const update = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  const normalizePayload = () => ({
    age: Number(form.age),
    gender: form.gender,
    weight: Number(form.weight),
    height: Number(form.height),
    steps: Number(form.steps),
    sleep: Number(form.sleep),
    water: Number(form.water),
    heart_rate: Number(form.heart_rate)
  });

  const onAnalyze = async () => {
    setLoadingAnalyze(true);
    try {
      const result = await analyzeVitals(normalizePayload());
      setAnalysis(result);
    } catch (error) {
      Alert.alert('Analyze failed', normalizeApiError(error));
    } finally {
      setLoadingAnalyze(false);
    }
  };

  const onSave = async () => {
    setLoadingSave(true);
    try {
      await saveHealthLog(normalizePayload());
      Alert.alert('Saved', 'Health log saved successfully.');
    } catch (error) {
      Alert.alert('Save failed', normalizeApiError(error));
    } finally {
      setLoadingSave(false);
    }
  };

  const onWatch = async () => {
    setLoadingWatch(true);
    try {
      const result = await fetchWatch(form.heart_rate || '72');
      setWatch(result);
    } catch (error) {
      Alert.alert('Watch failed', normalizeApiError(error));
    } finally {
      setLoadingWatch(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      {!isConnected ? <Text style={styles.offline}>You are offline. Data sync is paused.</Text> : null}

      <Card>
        <Text style={styles.title}>Vitals Input</Text>
        <View style={styles.form}>
          <AppInput label="Age" value={form.age} onChangeText={(v) => update('age', v)} keyboardType="numeric" />
          <AppInput label="Gender" value={form.gender} onChangeText={(v) => update('gender', v)} />
          <AppInput label="Weight (kg)" value={form.weight} onChangeText={(v) => update('weight', v)} keyboardType="numeric" />
          <AppInput label="Height (cm)" value={form.height} onChangeText={(v) => update('height', v)} keyboardType="numeric" />
          <AppInput label="Steps" value={form.steps} onChangeText={(v) => update('steps', v)} keyboardType="numeric" />
          <AppInput label="Sleep (hours)" value={form.sleep} onChangeText={(v) => update('sleep', v)} keyboardType="numeric" />
          <AppInput label="Water (liters)" value={form.water} onChangeText={(v) => update('water', v)} keyboardType="numeric" />
          <AppInput label="Heart Rate" value={form.heart_rate} onChangeText={(v) => update('heart_rate', v)} keyboardType="numeric" />
          <AppButton title="Analyze" loading={loadingAnalyze} onPress={onAnalyze} />
          <AppButton title="Save Log" variant="secondary" loading={loadingSave} onPress={onSave} />
          <AppButton title="Smartwatch Snapshot" variant="secondary" loading={loadingWatch} onPress={onWatch} />
        </View>
      </Card>

      {analysis ? (
        <Card>
          <Text style={styles.title}>Health Analysis</Text>
          <View style={styles.row}>
            <MetricCard label="Score" value={String(Math.round(analysis.health_score || 0))} />
            <MetricCard label="BMI" value={String(analysis.bmi || '-')} />
          </View>
          <View style={styles.row}>
            <MetricCard label="Obesity Risk" value={analysis.obesity_risk || '-'} />
            <MetricCard label="Fatigue Risk" value={analysis.fatigue_risk || '-'} />
          </View>
        </Card>
      ) : null}

      {watch ? (
        <Card>
          <Text style={styles.title}>Live Watch Snapshot</Text>
          <View style={styles.row}>
            <MetricCard label="Heart Rate" value={String(watch.heart_rate || '-')} />
            <MetricCard label="SpO2" value={String(watch.spo2 || '-')} />
          </View>
          <View style={styles.row}>
            <MetricCard label="Stress" value={String(watch.stress || '-')} />
            <MetricCard label="Steps" value={String(watch.live_steps || '-')} />
          </View>
        </Card>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: {
    padding: 16,
    gap: 14,
    backgroundColor: palette.bg
  },
  title: {
    color: palette.text,
    fontWeight: '800',
    fontSize: 20,
    marginBottom: 12
  },
  form: {
    gap: 10
  },
  row: {
    flexDirection: 'row',
    gap: 10,
    marginTop: 10
  },
  offline: {
    backgroundColor: '#fff4dd',
    color: palette.warning,
    borderColor: '#f4d7a7',
    borderWidth: 1,
    borderRadius: 12,
    paddingHorizontal: 12,
    paddingVertical: 9,
    fontWeight: '700'
  }
});
