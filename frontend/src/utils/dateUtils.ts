
export function getLocalDateString(date?: Date): string {
  const d = date || new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

/**
 * Lấy ngày hôm qua dưới dạng string YYYY-MM-DD theo local timezone
 * 
 * @returns string - Date string của ngày hôm qua
 */
export function getYesterdayDateString(): string {
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  return getLocalDateString(yesterday);
}

/**
 * Lấy ngày cách đây N ngày dưới dạng string YYYY-MM-DD theo local timezone
 * 
 * @param daysAgo - Số ngày trước (0 = hôm nay, 1 = hôm qua, 2 = 2 ngày trước...)
 * @returns string - Date string
 */
export function getDaysAgoDateString(daysAgo: number): string {
  const date = new Date();
  date.setDate(date.getDate() - daysAgo);
  return getLocalDateString(date);
}

