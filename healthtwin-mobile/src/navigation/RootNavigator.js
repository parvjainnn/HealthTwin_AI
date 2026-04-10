import React, { useEffect } from 'react';
import { ActivityIndicator, StyleSheet, View } from 'react-native';
import { AuthNavigator } from './AuthNavigator';
import { AppTabs } from './AppTabs';
import { useAuthStore } from '../store/authStore';
import { useConfigStore } from '../store/configStore';
import { palette } from '../theme/palette';

export function RootNavigator() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const isBootstrapping = useAuthStore((state) => state.isBootstrapping);
  const bootstrapSession = useAuthStore((state) => state.bootstrapSession);
  const apiBaseUrl = useConfigStore((state) => state.apiBaseUrl);
  const hydrateApiUrl = useConfigStore((state) => state.hydrateApiUrl);

  useEffect(() => {
    hydrateApiUrl(apiBaseUrl);
    bootstrapSession();
  }, [apiBaseUrl, bootstrapSession, hydrateApiUrl]);

  if (isBootstrapping) {
    return (
      <View style={styles.loaderWrap}>
        <ActivityIndicator size="large" color={palette.primary} />
      </View>
    );
  }

  return isAuthenticated ? <AppTabs /> : <AuthNavigator />;
}

const styles = StyleSheet.create({
  loaderWrap: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: palette.bg
  }
});
