import React, { useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, View } from 'react-native';
import { AppButton } from '../../components/AppButton';
import { AppInput } from '../../components/AppInput';
import { Card } from '../../components/Card';
import { askAdvisor } from '../../services/api/healthApi';
import { normalizeApiError } from '../../services/api/client';
import { palette } from '../../theme/palette';

const INITIAL_MESSAGE = {
  role: 'assistant',
  text: 'Hi, I am MediBot. Ask health or wellness questions any time.'
};

export function ChatScreen() {
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const onSend = async () => {
    const text = input.trim();
    if (!text || loading) return;

    setInput('');
    const next = [...messages, { role: 'user', text }];
    setMessages(next);
    setLoading(true);

    try {
      const response = await askAdvisor({
        question: text,
        user_data: {},
        history: next.map((m) => ({ role: m.role, content: m.text }))
      });
      setMessages((prev) => [...prev, { role: 'assistant', text: response.response || 'No response received.' }]);
    } catch (error) {
      Alert.alert('Chat failed', normalizeApiError(error));
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.wrap}>
      <ScrollView contentContainerStyle={styles.messages} showsVerticalScrollIndicator={false}>
        {messages.map((m, idx) => (
          <Card key={`${m.role}-${idx}`} style={m.role === 'user' ? styles.userCard : styles.botCard}>
            <Text style={styles.role}>{m.role === 'user' ? 'You' : 'MediBot'}</Text>
            <Text style={styles.text}>{m.text}</Text>
          </Card>
        ))}
      </ScrollView>
      <View style={styles.composer}>
        <AppInput label="Message" value={input} onChangeText={setInput} />
        <AppButton title={loading ? 'Sending...' : 'Send'} onPress={onSend} loading={loading} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    flex: 1,
    padding: 16,
    gap: 12,
    backgroundColor: palette.bg
  },
  messages: {
    gap: 10,
    paddingBottom: 20
  },
  userCard: {
    backgroundColor: '#dff5e8',
    borderColor: '#c7e7d5',
    alignSelf: 'flex-end',
    maxWidth: '92%'
  },
  botCard: {
    alignSelf: 'flex-start',
    maxWidth: '92%'
  },
  role: {
    color: palette.textMuted,
    textTransform: 'uppercase',
    fontSize: 11,
    letterSpacing: 1,
    fontWeight: '700',
    marginBottom: 4
  },
  text: {
    color: palette.text,
    lineHeight: 20
  },
  composer: {
    gap: 10
  }
});
