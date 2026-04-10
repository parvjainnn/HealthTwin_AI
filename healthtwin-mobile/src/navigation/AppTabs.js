import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { DashboardScreen } from '../screens/app/DashboardScreen';
import { PredictionsScreen } from '../screens/app/PredictionsScreen';
import { ChatScreen } from '../screens/app/ChatScreen';
import { HistoryScreen } from '../screens/app/HistoryScreen';
import { SettingsScreen } from '../screens/app/SettingsScreen';
import { palette } from '../theme/palette';

const Tab = createBottomTabNavigator();

export function AppTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: palette.surface },
        headerTitleStyle: { color: palette.text, fontWeight: '700' },
        tabBarStyle: { backgroundColor: palette.surface, borderTopColor: palette.border },
        tabBarActiveTintColor: palette.primary,
        tabBarInactiveTintColor: palette.textMuted
      }}
    >
      <Tab.Screen name="Dashboard" component={DashboardScreen} options={{ title: 'Dashboard' }} />
      <Tab.Screen name="Predict" component={PredictionsScreen} options={{ title: 'Predict' }} />
      <Tab.Screen name="Chat" component={ChatScreen} options={{ title: 'AI Chat' }} />
      <Tab.Screen name="History" component={HistoryScreen} options={{ title: 'History' }} />
      <Tab.Screen name="Settings" component={SettingsScreen} options={{ title: 'Settings' }} />
    </Tab.Navigator>
  );
}
