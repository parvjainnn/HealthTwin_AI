import React from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text } from 'react-native';
import { palette } from '../theme/palette';

export function AppButton({ title, loading, disabled, variant = 'primary', ...props }) {
  const isPrimary = variant === 'primary';
  const styles = getStyles(isPrimary);
  return (
    <Pressable style={[styles.button, disabled && styles.disabled]} disabled={disabled || loading} {...props}>
      {loading ? (
        <ActivityIndicator size="small" color={isPrimary ? '#ffffff' : palette.primary} />
      ) : (
        <Text style={styles.title}>{title}</Text>
      )}
    </Pressable>
  );
}

function getStyles(isPrimary) {
  return StyleSheet.create({
    button: {
      borderRadius: 14,
      paddingVertical: 13,
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: isPrimary ? palette.primary : palette.surfaceAlt,
      borderWidth: 1,
      borderColor: isPrimary ? palette.primary : palette.border
    },
    disabled: {
      opacity: 0.6
    },
    title: {
      color: isPrimary ? '#ffffff' : palette.text,
      fontWeight: '800',
      fontSize: 15
    }
  });
}
