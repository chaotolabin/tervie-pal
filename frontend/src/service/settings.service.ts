import apiClient from './apiClient';

export const SettingsService = {
  changePassword: async (currentPassword: string, newPassword: string): Promise<void> => {
    await apiClient.patch('/settings/password', {
      current_password: currentPassword,
      new_password: newPassword
    });
  }
};

