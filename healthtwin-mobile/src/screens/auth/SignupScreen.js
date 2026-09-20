import React, { useState } from 'react';
import { KeyboardAvoidingView, Platform, StyleSheet, Text, View } from 'react-native';
import { AppButton } from '../../components/AppButton';
import { AppInput } from '../../components/AppInput';
import { Card } from '../../components/Card';
import { useAuthStore } from '../../store/authStore';
import { palette } from '../../theme/palette';

export function SignupScreen({ navigation }) {
  const signUp = useAuthStore((state) => state.signUp);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const onSubmit = async () => {
    setError('');
    if (!username || !email || !password || !confirmPassword) {
      setError('All fields are required.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setLoading(true);
    const result = await signUp({
      username,
      email,
      password,
      confirm_password: confirmPassword
    });
    setLoading(false);
    if (!result.ok) setError(result.message || 'Signup failed.');
  };

  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.wrap}>
      <View style={styles.inner}>
        <Text style={styles.brand}>HealthTwin</Text>
        <Text style={styles.title}>Create account</Text>
        <Card>
          <View style={styles.form}>
            <AppInput label="Username" value={username} onChangeText={setUsername} />
            <AppInput label="Email" value={email} onChangeText={setEmail} keyboardType="email-address" />
            <AppInput label="Password" value={password} onChangeText={setPassword} secureTextEntry />
            <AppInput label="Confirm Password" value={confirmPassword} onChangeText={setConfirmPassword} secureTextEntry />
            {error ? <Text style={styles.error}>{error}</Text> : null}
            <AppButton title="Create Account" onPress={onSubmit} loading={loading} />
            <AppButton title="Back to Login" variant="secondary" onPress={() => navigation.goBack()} />
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
