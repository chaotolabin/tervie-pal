import { createClient } from '@supabase/supabase-js'

// Đây là thông tin dự án của bạn
const supabaseUrl = 'https://ktxalsscztqdkvvpxldb.supabase.co'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt0eGFsc3NjenRxZGt2dnB4bGRiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU3ODQ3MjcsImV4cCI6MjA4MTM2MDcyN30.REU6poPZniuqb0eh4KlG31Ri8EXIWQRPW0vU3N1xSwI' // Bạn lấy mã này ở bước 3 bên dưới
