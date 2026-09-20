import React, { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, RefreshControl, ScrollView, StyleSheet, Text, View } from 'react-native';
import { Card } from '../../components/Card';
import { fetchHistory } from '../../services/api/healthApi';
import { normalizeApiError } from '../../services/api/client';
import { palette } from '../../theme/palette';

export function HistoryScreen() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  const load = useCallback(async (refreshMode = false) => {
    if (refreshMode) setRefreshing(true);
    else setLoading(true);
    setError('');
    try {
      const data = await fetchHistory();
      setLogs(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(normalizeApiError(e));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  if (loading) {
    return (
      <View style={styles.loader}>
        <ActivityIndicator size="large" color={palette.primary} />
      </View>
    );
  }

  return (
    <ScrollView
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => load(true)} />}
    >
      {error ? <Text style={styles.error}>{error}</Text> : null}
      {logs.length === 0 ? (
        <Card>
          <Text style={styles.emptyTitle}>No health logs yet</Text>
          <Text style={styles.emptyCopy}>Add entries from Dashboard and they will appear here.</Text>
        </Card>
      ) : (
        logs.map((log) => (
          <Card key={String(log.id)}>
            <Text style={styles.date}>{log.timestamp}</Text>
            <View style={styles.row}>
              <Text style={styles.k}>Score:</Text>
              <Text style={styles.v}>{Math.round(log.health_score || 0)}</Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.k}>BMI:</Text>
              <Text style={styles.v}>{log.bmi}</Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.k}>Sleep:</Text>
              <Text style={styles.v}>{log.sleep} h</Text>
            </View>
            <View style={styles.row}>
              <Text style={styles.k}>Steps:</Text>
              <Text style={styles.v}>{log.steps}</Text>
            </View>
          </Card>
        ))
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  loader: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: palette.bg
  },
  content: {
    padding: 16,
    gap: 12,
    backgroundColor: palette.bg
  },
  error: {
    color: palette.danger,
    fontWeight: '700'
  },
  emptyTitle: {
    color: palette.text,
    fontWeight: '800',
    fontSize: 20
  },
  emptyCopy: {
    marginTop: 8,
    color: palette.textMuted,
    lineHeight: 21
  },
  date: {
    color: palette.primary,
    fontWeight: '800',
    marginBottom: 8
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 4
  },
  k: {
    color: palette.textMuted
  },
  v: {
    color: palette.text,
    fontWeight: '700'
  }
});
