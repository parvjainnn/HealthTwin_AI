import React, { useState } from 'react';
import { KeyboardAvoidingView, Platform, StyleSheet, Text, View } from 'react-native';
import { AppButton } from '../../components/AppButton';
import { AppInput } from '../../components/AppInput';
import { Card } from '../../components/Card';
import { useAuthStore } from '../../store/authStore';
import { palette } from '../../theme/palette';

export function LoginScreen({ navigation }) {
  const signIn = useAuthStore((state) => state.signIn);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const onSubmit = async () => {
    setError('');
    if (!username || !password) {
      setError('Please enter username and password.');
      return;
    }
    setLoading(true);
    const result = await signIn({ username, password, remember: true });
    setLoading(false);
    if (!result.ok) setError(result.message || 'Login failed.');
  };

  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.wrap}>
      <View style={styles.inner}>
        <Text style={styles.brand}>HealthTwin</Text>
        <Text style={styles.title}>Sign in to mobile app</Text>
        <Card>
          <View style={styles.form}>
            <AppInput label="Username" value={username} onChangeText={setUsername} />
            <AppInput label="Password" value={password} onChangeText={setPassword} secureTextEntry />
            {error ? <Text style={styles.error}>{error}</Text> : null}
            <AppButton title="Login" onPress={onSubmit} loading={loading} />
            <AppButton title="Create Account" variant="secondary" onPress={() => navigation.navigate('Signup')} />
          </View>
        </Card>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  wrap: {
    flex: 1,
    backgroundColor: palette.bg
  },
  inner: {
    flex: 1,
    justifyContent: 'center',
    padding: 18,
    gap: 14
  },
  brand: {
    color: palette.primary,
    textTransform: 'uppercase',
    letterSpacing: 1.5,
    fontWeight: '800',
    fontSize: 12
  },
  title: {
    color: palette.text,
    fontSize: 28,
    fontWeight: '800'
  },
  form: {
    gap: 12
  },
  error: {
    color: palette.danger,
    fontSize: 13,
    fontWeight: '600'
  }
});
