import React, { useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, View } from 'react-native';
import { AppButton } from '../../components/AppButton';
import { AppInput } from '../../components/AppInput';
import { Card } from '../../components/Card';
import { predictDiabetes, predictHeart } from '../../services/api/healthApi';
import { normalizeApiError } from '../../services/api/client';
import { palette } from '../../theme/palette';

const DIABETES_FIELDS = {
  pregnancies: '0',
  glucose: '120',
  blood_pressure: '80',
  skin_thickness: '20',
  insulin: '85',
  bmi: '26.1',
  diabetes_pedigree_function: '0.52',
  age: '28'
};

const HEART_FIELDS = {
  age: '45',
  sex: '1',
  chest_pain_type: '1',
  resting_bp: '130',
  cholesterol: '220',
  fasting_bs: '0',
  resting_ecg: '0',
  max_hr: '150',
  exercise_angina: '0',
  oldpeak: '1.0'
};

export function PredictionsScreen() {
  const [tab, setTab] = useState('diabetes');
  const [diabetes, setDiabetes] = useState(DIABETES_FIELDS);
  const [heart, setHeart] = useState(HEART_FIELDS);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const active = tab === 'diabetes' ? diabetes : heart;
  const setActive = tab === 'diabetes' ? setDiabetes : setHeart;

  const onSubmit = async () => {
    setLoading(true);
    try {
      const payload = Object.fromEntries(Object.entries(active).map(([k, v]) => [k, Number(v)]));
      const response = tab === 'diabetes' ? await predictDiabetes(payload) : await predictHeart(payload);
      setResult(response);
    } catch (error) {
      Alert.alert('Prediction failed', normalizeApiError(error));
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      <Card>
        <Text style={styles.title}>Disease Prediction</Text>
        <View style={styles.tabRow}>
          <AppButton title="Diabetes" variant={tab === 'diabetes' ? 'primary' : 'secondary'} onPress={() => setTab('diabetes')} />
          <AppButton title="Heart" variant={tab === 'heart' ? 'primary' : 'secondary'} onPress={() => setTab('heart')} />
        </View>
        <View style={styles.form}>
          {Object.entries(active).map(([key, value]) => (
            <AppInput
              key={key}
              label={key.replace(/_/g, ' ')}
              value={String(value)}
              onChangeText={(val) => setActive((prev) => ({ ...prev, [key]: val }))}
              keyboardType="numeric"
            />
          ))}
        </View>
        <AppButton title="Run Prediction" loading={loading} onPress={onSubmit} />
      </Card>

      {result ? (
        <Card>
          <Text style={styles.title}>Result</Text>
          <Text style={styles.resultLabel}>{result.risk_label || result.prediction || 'Completed'}</Text>
          {result.confidence ? (
            <Text style={styles.helpText}>Confidence: {Math.round(Number(result.confidence) * 100)}%</Text>
          ) : null}
          {result.message ? <Text style={styles.helpText}>{result.message}</Text> : null}
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
  tabRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 10
  },
  form: {
    gap: 10,
    marginBottom: 10
  },
  resultLabel: {
    color: palette.primary,
    fontSize: 28,
    fontWeight: '800'
  },
  helpText: {
    marginTop: 8,
    color: palette.textMuted,
    lineHeight: 21
  }
});
