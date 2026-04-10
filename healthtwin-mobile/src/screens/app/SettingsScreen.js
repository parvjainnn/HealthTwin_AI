import React, { useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, View } from 'react-native';
import { AppButton } from '../../components/AppButton';
import { AppInput } from '../../components/AppInput';
import { Card } from '../../components/Card';
import { useNetworkStatus } from '../../hooks/useNetworkStatus';
import { useAuthStore } from '../../store/authStore';
import { useConfigStore } from '../../store/configStore';
import { palette } from '../../theme/palette';

export function SettingsScreen() {
  const user = useAuthStore((state) => state.user);
  const signOut = useAuthStore((state) => state.signOut);
  const apiBaseUrl = useConfigStore((state) => state.apiBaseUrl);
  const setApiUrl = useConfigStore((state) => state.setApiUrl);
  const isConnected = useNetworkStatus();
  const [urlInput, setUrlInput] = useState(apiBaseUrl);

  const saveUrl = () => {
    if (!urlInput.trim()) {
      Alert.alert('Invalid URL', 'Please enter a backend URL.');
      return;
    }
    setApiUrl(urlInput);
    Alert.alert('Updated', 'Backend URL updated successfully.');
  };

  const logout = async () => {
    await signOut();
  };

  return (
    <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      <Card>
        <Text style={styles.title}>Account</Text>
        <Text style={styles.info}>Username: {user?.username || '-'}</Text>
        <Text style={styles.info}>Email: {user?.email || '-'}</Text>
      </Card>

      <Card>
        <Text style={styles.title}>Backend Configuration</Text>
        <AppInput label="API Base URL" value={urlInput} onChangeText={setUrlInput} />
        <Text style={styles.hint}>For Android emulator use `http://10.0.2.2:5000`.</Text>
        <Text style={styles.hint}>For real phone use your laptop IP, like `http://192.168.1.10:5000`.</Text>
        <AppButton title="Save Backend URL" onPress={saveUrl} />
      </Card>

      <Card>
        <Text style={styles.title}>Connection</Text>
        <View style={styles.statusRow}>
          <View style={[styles.dot, { backgroundColor: isConnected ? '#2e9b70' : palette.danger }]} />
          <Text style={styles.statusText}>{isConnected ? 'Online' : 'Offline'}</Text>
        </View>
      </Card>

      <AppButton title="Logout" variant="secondary" onPress={logout} />
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
    marginBottom: 10
  },
  info: {
    color: palette.textMuted,
    marginTop: 6
  },
  hint: {
    marginTop: 8,
    color: palette.textMuted,
    lineHeight: 20
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8
  },
  dot: {
    width: 10,
    height: 10,
    borderRadius: 10
  },
  statusText: {
    color: palette.text,
    fontWeight: '700'
  }
});
