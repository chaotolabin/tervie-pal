export type StreakStatus = 'green' | 'yellow' | 'gray';

export interface StreakDayResponse {
  day: string; // YYYY-MM-DD
  status: StreakStatus;
}

export interface StreakResponse {
  current_streak: number;
  longest_streak: number;
  week: StreakDayResponse[];
}